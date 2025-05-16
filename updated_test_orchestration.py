#!/usr/bin/env python3
"""
Updated test script for Semantic Kernel orchestration with SK 1.30.0.
This version avoids the interactive chat loop and just runs a test query.
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

def setup_kernel_with_openai():
    """Set up a kernel with Azure OpenAI"""
    # Set required environment variables
    os.environ["AZURE_OPENAI_ENDPOINT"] = "https://sk-multi-agent-openai.openai.azure.com/"
    os.environ["AZURE_OPENAI_API_KEY"] = "48d4df6c7b5a49f38d7675620f8e3aa0"
    os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"] = "gpt-35-turbo"
    
    # Get Azure OpenAI configuration
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    print(f"Endpoint: {endpoint}")
    print(f"Deployment: {deployment}")
    print(f"API Key: {api_key[:5]}...")
    
    if not all([endpoint, api_key, deployment]):
        raise ValueError("Azure OpenAI configuration not found in environment variables")
    
    # Create a kernel
    kernel = sk.Kernel()
    
    # Add Azure OpenAI chat service
    kernel.add_service(
        AzureChatCompletion(
            service_id="chat",
            deployment_name=deployment,
            endpoint=endpoint,
            api_key=api_key,
            api_version="2024-02-15-preview"  # Use version that works with our deployed model
        )
    )
    
    return kernel

async def setup_weather_plugin(kernel):
    """Set up the weather plugin"""
    # Create a weather service instance
    weather_service = WeatherService()
    
    # Create the weather plugin instance
    weather_plugin_obj = WeatherPlugin(weather_service)
    
    # Use from_object to create a plugin from our weather plugin object
    from semantic_kernel.functions import KernelPlugin
    
    weather_plugin = KernelPlugin.from_object(
        "WeatherPlugin",      # Plugin name (string)
        weather_plugin_obj,   # Plugin instance
        description="Provides weather information for US cities"
    )
    
    # Add the plugin to the kernel
    kernel.plugins["WeatherPlugin"] = weather_plugin
    
    return weather_plugin

async def test_with_function_calling(kernel, user_query):
    """Test the kernel with a query that might trigger function calling"""
    # Create a chat history
    chat_history = ChatHistory()
    
    # Add system message
    chat_history.add_system_message("""
    You are a helpful assistant that provides friendly, concise, and accurate information.
    When the user asks about weather, you should use the GetWeather function to get accurate weather information.
    Always extract the location from the user's question when dealing with weather queries.
    
    For example:
    - If they ask 'What's the weather like in Seattle?', call GetWeather with location='Seattle, WA'
    - If they ask 'Will it rain tomorrow in Chicago?', call GetWeather with location='Chicago, IL' and type='forecast'
    
    DO NOT make up weather information. ALWAYS use the GetWeather function for weather queries.
    For other questions, answer directly from your knowledge.
    """)
    
    # Define tools for function calling
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
    settings = AzureChatPromptExecutionSettings(
        service_id="chat",
        ai_model_id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        temperature=0,
        tool_choice="auto",
        tools=tools
    )
    
    # Add user message and create arguments
    chat_history.add_user_message(user_query)
    
    # Create the arguments
    arguments = KernelArguments(history=chat_history)
    
    # Create a simple function template for chat
    from semantic_kernel.core_plugins.conversation.chat_plugin import ChatPlugin
    from semantic_kernel.text import TextChunker
    
    chat_plugin = kernel.add_plugin(ChatPlugin(), "chat")
    chat_function = chat_plugin["chat"]
    
    try:
        # Get the first response
        result = await kernel.invoke(chat_function, arguments=arguments, settings=settings)
        print(f"\nInitial response: {result}")
        
        # Check if function was called
        if hasattr(result, 'tool_calls') and result.tool_calls:
            print("\nFunction call detected!")
            
            for tool_call in result.tool_calls:
                if tool_call.function.name == "GetWeather":
                    print(f"Tool call: {tool_call.function.name}")
                    print(f"Arguments: {tool_call.function.arguments}")
                    
                    # Parse arguments
                    args = json.loads(tool_call.function.arguments)
                    location = args.get("location")
                    weather_type = args.get("type", "current")
                    
                    print(f"\nCalling WeatherPlugin.GetWeather for: {location} ({weather_type})")
                    
                    # Get the weather function
                    weather_plugin = kernel.plugins["WeatherPlugin"]
                    get_weather_function = weather_plugin["GetWeather"]
                    
                    # Call the weather function
                    weather_args = KernelArguments(location=location, type=weather_type)
                    weather_result = await kernel.invoke(get_weather_function, arguments=weather_args)
                    
                    weather_data = str(weather_result)
                    print(f"Weather data: {weather_data}")
                    
                    # Add result to chat history
                    chat_history.add_assistant_message(str(result))
                    chat_history.add_tool_message(tool_call.id, weather_data)
                    
                    # Get final response with weather data
                    final_settings = AzureChatPromptExecutionSettings(
                        service_id="chat",
                        ai_model_id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                        temperature=0,
                        tool_choice="none"
                    )
                    
                    final_result = await kernel.invoke(
                        chat_function, 
                        arguments=KernelArguments(history=chat_history),
                        settings=final_settings
                    )
                    
                    return str(final_result), True
            
            return str(result), False
        else:
            # No function call, just return the response
            return str(result), False
            
    except Exception as e:
        print(f"Error during function calling: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error: {str(e)}", False

async def test_orchestration():
    """Test the orchestration with a weather query"""
    print("Setting up Semantic Kernel orchestration...")
    
    kernel = setup_kernel_with_openai()
    await setup_weather_plugin(kernel)
    
    print("\nTesting weather query...")
    
    test_query = "What's the weather like in Seattle right now?"
    print(f"Query: {test_query}")
    
    response, used_function = await test_with_function_calling(kernel, test_query)
    print(f"\nFunction called: {used_function}")
    print(f"Final response: {response}")
    
    # Test a non-weather query
    print("\nTesting general knowledge query...")
    
    general_query = "What is the capital of France?"
    print(f"Query: {general_query}")
    
    response, used_function = await test_with_function_calling(kernel, general_query)
    print(f"\nFunction called: {used_function}")
    print(f"Final response: {response}")

async def main():
    """Main entry point"""
    try:
        await test_orchestration()
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())