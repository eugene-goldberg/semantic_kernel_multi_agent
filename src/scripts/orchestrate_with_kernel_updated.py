#!/usr/bin/env python3
"""
Orchestration system using Semantic Kernel to delegate from chat agent to weather agent.
This version is updated to be compatible with Semantic Kernel 1.1.1+.
"""

import os
import sys
import asyncio
import json
from dotenv import load_dotenv
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from src.agents.plugins.weather_plugin import WeatherPlugin
from src.services.weather_service import WeatherService

def setup_kernel_with_openai():
    """Set up a kernel with Azure OpenAI"""
    # Load environment variables
    load_dotenv()
    
    # Get Azure OpenAI configuration
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    if not all([endpoint, api_key, deployment]):
        raise ValueError("Azure OpenAI configuration not found in .env file")
    
    # Create a kernel
    kernel = sk.Kernel()
    
    # Set up the service configuration
    service_id = "azure_chat_completion"
    azure_chat_completion = AzureChatCompletion(
        deployment_name=deployment,
        endpoint=endpoint,
        api_key=api_key,
        api_version="2024-05-01-preview"
    )
    
    # Add the service to the kernel
    kernel.add_service(azure_chat_completion)
    
    return kernel, service_id

async def setup_weather_plugin(kernel):
    """Set up the weather plugin with the current Semantic Kernel API"""
    # Create a weather service instance
    weather_service = WeatherService()
    
    # Create the weather plugin instance
    weather_plugin_obj = WeatherPlugin(weather_service)
    
    # Register the plugin functions manually
    plugin_name = "WeatherPlugin"
    
    # Create a plugin and add it to the kernel
    kernel.plugins[plugin_name] = sk.functions.KernelPlugin(
        name=plugin_name,
        description="Provides weather information for US cities"
    )
    
    # Register the GetWeather function
    kernel.plugins[plugin_name].add_function(
        sk.functions.KernelFunction.from_method(
            method=weather_plugin_obj.get_weather,
            name="GetWeather",
            description="Get weather information for a location (current or forecast)",
            plugin_name=plugin_name
        )
    )
    
    # Register the GetCurrentWeather function
    kernel.plugins[plugin_name].add_function(
        sk.functions.KernelFunction.from_method(
            method=weather_plugin_obj.get_current_weather,
            name="GetCurrentWeather", 
            description="Get the current weather for a US city",
            plugin_name=plugin_name
        )
    )
    
    # Register the GetWeatherForecast function
    kernel.plugins[plugin_name].add_function(
        sk.functions.KernelFunction.from_method(
            method=weather_plugin_obj.get_weather_forecast,
            name="GetWeatherForecast",
            description="Get the weather forecast for a US city",
            plugin_name=plugin_name
        )
    )
    
    return plugin_name

async def chat_with_function_calling(kernel, service_id, plugin_name, input_text, chat_history=None):
    """Chat with the model using function calling to trigger the weather plugin"""
    if chat_history is None:
        chat_history = []
    
    system_message = """
    You are a helpful assistant that provides friendly, concise, and accurate information.
    When the user asks about weather, you should use the GetWeather function to get accurate weather information.
    Always extract the location from the user's question when dealing with weather queries.
    
    For example:
    - If they ask 'What's the weather like in Seattle?', call GetWeather with location='Seattle, WA'
    - If they ask 'Will it rain tomorrow in Chicago?', call GetWeather with location='Chicago, IL' and type='forecast'
    
    DO NOT make up weather information. ALWAYS use the GetWeather function for weather queries.
    For other questions, answer directly from your knowledge.
    """
    
    # Prepare the chat history
    messages = [
        {"role": "system", "content": system_message}
    ]
    
    # Add chat history
    for msg in chat_history:
        messages.append(msg)
    
    # Add the current user message
    messages.append({"role": "user", "content": input_text})
    
    # Define the weather function as a tool
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
    
    # Get the chat completion service
    chat_completion_service = kernel.get_service(service_id)
    
    # Create settings with tool configuration
    settings = sk.ChatCompletionClientSettings(
        tools=tools,
        tool_choice="auto"
    )
    
    # Make the initial request
    response = await chat_completion_service.complete_chat_async(
        messages=messages,
        settings=settings
    )
    
    # Process the response
    content = response.content
    function_calls = []
    
    # Check if the model wants to call a function
    if hasattr(response, "tool_calls") and response.tool_calls:
        # Process each tool call
        for tool_call in response.tool_calls:
            if tool_call.function.name == "GetWeather":
                # Parse the arguments
                args = json.loads(tool_call.function.arguments)
                location = args.get("location")
                weather_type = args.get("type", "current")
                
                print(f"\nCalling weather service for: {location} ({weather_type})")
                
                # Get the weather function
                get_weather_function = kernel.plugins[plugin_name]["GetWeather"]
                
                # Call the function with the parsed arguments
                weather_result = await get_weather_function.invoke_async(
                    location=location,
                    type=weather_type
                )
                
                function_calls.append({
                    "name": "GetWeather",
                    "arguments": args,
                    "result": str(weather_result.result)
                })
                
                # Create a new message to continue the conversation
                followup_messages = messages.copy()
                followup_messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": "GetWeather",
                                "arguments": tool_call.function.arguments
                            }
                        }
                    ]
                })
                followup_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(weather_result.result)
                })
                
                # Get the final response that includes the function result
                final_response = await chat_completion_service.complete_chat_async(
                    messages=followup_messages
                )
                
                content = final_response.content
                
                break
    
    return content, function_calls

async def orchestration_chat():
    """Run the orchestration chat"""
    print("Setting up Semantic Kernel orchestration...")
    
    # Set up the kernel
    kernel, service_id = setup_kernel_with_openai()
    
    # Set up the weather plugin
    plugin_name = await setup_weather_plugin(kernel)
    
    print("\nWelcome to the Multi-Agent Chat!")
    print("You can ask general questions or about the weather.")
    print("Type 'exit' to quit.")
    
    # Chat loop
    chat_history = []
    
    while True:
        try:
            user_input = input("\nYou: ")
            
            # Check for exit command
            if user_input.lower() == "exit":
                print("Exiting chat...")
                break
                
            # Empty input should just prompt again
            if not user_input.strip():
                continue
                
            # Process the user input with function calling
            response, function_calls = await chat_with_function_calling(
                kernel, 
                service_id,
                plugin_name,
                user_input,
                chat_history
            )
            
            # Add messages to chat history
            chat_history.append({"role": "user", "content": user_input})
            chat_history.append({"role": "assistant", "content": response})
            
            # If there were function calls, show debug info
            if function_calls:
                print("\n[Function calls processed]")
            
            # Print the response
            print(f"Agent: {response}")
            
        except Exception as e:
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()

async def main():
    """Main entry point"""
    try:
        await orchestration_chat()
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())