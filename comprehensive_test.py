#!/usr/bin/env python3
"""
Comprehensive test showing full dialog between orchestrated agents.
"""

import os
import sys
import asyncio
import json
from dotenv import load_dotenv
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureChatPromptExecutionSettings
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.contents import ChatHistory

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from src.agents.plugins.weather_plugin import WeatherPlugin
from src.services.weather_service import WeatherService

def setup_kernel():
    """Set up a kernel with Azure OpenAI"""
    # Set required environment variables
    os.environ["AZURE_OPENAI_ENDPOINT"] = "https://sk-multi-agent-openai.openai.azure.com/"
    os.environ["AZURE_OPENAI_API_KEY"] = "48d4df6c7b5a49f38d7675620f8e3aa0"
    os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"] = "gpt-35-turbo"
    
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    print(f"Endpoint: {endpoint}")
    print(f"Deployment: {deployment}")
    print(f"API Key: {api_key[:5]}...")
    
    # Create kernel
    kernel = sk.Kernel()
    
    # Add Azure OpenAI service
    kernel.add_service(
        AzureChatCompletion(
            service_id="chat",
            deployment_name=deployment,
            endpoint=endpoint,
            api_key=api_key,
            api_version="2024-02-15-preview"
        )
    )
    
    return kernel

async def register_weather_plugin(kernel):
    """Register the weather plugin with the kernel"""
    # Create weather service
    weather_service = WeatherService()
    
    # Create weather plugin
    weather_plugin_obj = WeatherPlugin(weather_service)
    
    # Register plugin
    from semantic_kernel.functions import KernelPlugin
    
    weather_plugin = KernelPlugin.from_object(
        "WeatherPlugin",
        weather_plugin_obj,
        description="Provides weather information for US cities"
    )
    
    # Add plugin to kernel
    kernel.plugins["WeatherPlugin"] = weather_plugin
    
    print("Weather plugin registered successfully")
    return weather_plugin

async def create_chat_function(kernel, chat_history):
    """Create a chat function for orchestration"""
    from semantic_kernel.functions import KernelFunction
    
    # Create prompt template with tool usage instructions
    prompt_template = """
{{$history}}

You are a smart assistant who uses available tools to answer user questions.
For weather questions, you should call the GetWeather function.
Respond to the user in a helpful and conversational manner.
"""
    
    # Create function
    chat_function = KernelFunction.from_prompt(
        prompt=prompt_template,
        function_name="chat",
        plugin_name="ChatPlugin",
        description="Chat with the user and respond to their queries"
    )
    
    # Add to kernel
    kernel.add_function("ChatPlugin", chat_function)
    
    return chat_function

async def test_orchestration_conversation():
    """Run a comprehensive test of agent orchestration with multiple interactions"""
    print("Setting up Semantic Kernel orchestration...")
    
    # Setup kernel
    kernel = setup_kernel()
    
    # Register weather plugin
    await register_weather_plugin(kernel)
    
    # Create chat history
    chat_history = ChatHistory()
    chat_history.add_system_message("""
    You are a helpful assistant that provides friendly, concise, and accurate information.
    When asked about weather, you should use the GetWeather function to get accurate weather information.
    For other questions, answer directly from your knowledge.
    """)
    
    # Create chat function
    chat_function = await create_chat_function(kernel, chat_history)
    
    # Define tools for the model
    tools = [
        {
            "type": "function",
            "function": {
                "name": "GetWeather", 
                "description": "Get weather information for a location (current or forecast)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. Seattle, WA"
                        },
                        "type": {
                            "type": "string",
                            "enum": ["current", "forecast"],
                            "description": "The type of weather information to retrieve"
                        }
                    },
                    "required": ["location"]
                }
            }
        }
    ]
    
    # Create execution settings
    settings_with_tools = AzureChatPromptExecutionSettings(
        service_id="chat",
        ai_model_id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        temperature=0,
        tool_choice="auto",
        tools=tools
    )
    
    settings_without_tools = AzureChatPromptExecutionSettings(
        service_id="chat",
        ai_model_id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        temperature=0
    )
    
    # Test messages to demonstrate different capabilities
    test_messages = [
        "Hi, can you tell me about the weather in Seattle today?",
        "What about the forecast for New York?",
        "Tell me some facts about the Golden Gate Bridge",
        "How's the weather in Miami right now?",
        "Thanks for your help today!"
    ]
    
    # Process each message
    for idx, message in enumerate(test_messages):
        print(f"\n\n--- CONVERSATION TURN {idx+1} ---")
        print(f"User: {message}")
        
        # Add message to history
        chat_history.add_user_message(message)
        
        # Get response
        arguments = KernelArguments(history=chat_history)
        
        try:
            # First pass - with tools enabled
            response = await kernel.invoke(chat_function, arguments=arguments, settings=settings_with_tools)
            
            print(f"Initial assistant response: {response}")
            
            # Check for tool calls
            tool_calls_processed = False
            
            if hasattr(response, 'tool_calls') and response.tool_calls:
                print("\n[Function calling detected]")
                
                for tool_call in response.tool_calls:
                    if tool_call.function.name == "GetWeather":
                        print(f"Weather agent invoked")
                        
                        # Parse arguments from tool call
                        args = json.loads(tool_call.function.arguments)
                        location = args.get("location")
                        weather_type = args.get("type", "current")
                        
                        print(f"Getting weather for: {location} ({weather_type})")
                        
                        try:
                            # Call weather function
                            weather_plugin = kernel.plugins["WeatherPlugin"]
                            get_weather_function = weather_plugin["GetWeather"]
                            
                            weather_args = KernelArguments(location=location, type=weather_type)
                            weather_result = await kernel.invoke(get_weather_function, arguments=weather_args)
                            
                            print(f"Weather agent response: {weather_result}")
                            
                            # Add results to chat history
                            chat_history.add_assistant_message(str(response))
                            chat_history.add_tool_message(tool_call.id, str(weather_result))
                            
                            # Get final response incorporating the tool result
                            final_arguments = KernelArguments(history=chat_history)
                            final_response = await kernel.invoke(
                                chat_function, 
                                arguments=final_arguments,
                                settings=settings_without_tools
                            )
                            
                            print(f"Final assistant response: {final_response}")
                            
                            # Add to history for next turn
                            chat_history.add_assistant_message(str(final_response))
                            tool_calls_processed = True
                        except Exception as e:
                            print(f"Error processing weather function: {str(e)}")
                            # Continue conversation
                            chat_history.add_assistant_message(str(response))
            
            # If no tool calls were processed, just add the initial response to history
            if not tool_calls_processed:
                chat_history.add_assistant_message(str(response))
                
        except Exception as e:
            print(f"Error in conversation: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n\nConversation test complete!")

if __name__ == "__main__":
    asyncio.run(test_orchestration_conversation())