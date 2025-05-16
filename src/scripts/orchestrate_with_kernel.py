#!/usr/bin/env python3
"""
Orchestration system using Semantic Kernel to delegate from chat agent to weather agent.
This uses a simpler approach compatible with Semantic Kernel 1.30.0,
and correctly invokes chat completion services with function calling.
"""

import os
import sys
import asyncio
import json
from dotenv import load_dotenv
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureChatPromptExecutionSettings
from semantic_kernel.functions.kernel_arguments import KernelArguments

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
    
    # Add Azure OpenAI chat service with function calling enabled
    kernel.add_service(
        AzureChatCompletion(
            service_id="chat", 
            deployment_name=deployment,
            endpoint=endpoint,
            api_key=api_key,
            api_version="2024-05-01-preview" # Ensure this supports function calling
        )
    )
    
    return kernel

async def setup_weather_plugin(kernel):
    """Set up the weather plugin"""
    # Create a weather service instance
    weather_service = WeatherService()
    
    # Create the weather plugin instance
    weather_plugin_obj = WeatherPlugin(weather_service)
    
    # Create a KernelPlugin and add functions from the weather plugin object
    from semantic_kernel.functions import KernelPlugin
    
    # Use from_object to create a plugin from our weather plugin object
    # The first argument is the plugin name (string), the second is the instance.
    weather_plugin = KernelPlugin.from_object(
        "WeatherPlugin",      # Plugin name (string)
        weather_plugin_obj,   # Plugin instance
        description="Provides weather information for US cities")
    
    # Add the plugin to the kernel
    kernel.plugins["WeatherPlugin"] = weather_plugin
    
    return weather_plugin

async def chat_with_function_calling(kernel, input_text, chat_history_list=None):
    """Chat with the model using function calling to trigger the weather plugin"""
    if chat_history_list is None:
        chat_history_list = [] 
    
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
    
    current_messages = [{"role": "system", "content": system_message}]
    current_messages.extend(chat_history_list) 
    current_messages.append({"role": "user", "content": input_text})
    
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
    
    chat_service = kernel.get_service("chat")
    if not chat_service:
        raise ValueError("Chat service 'chat' not found in kernel.")

    settings = AzureChatPromptExecutionSettings(
        tool_choice="auto",
        tools=tools
    )

    response_messages = await chat_service.complete_chat_async(
        messages=current_messages,
        settings=settings
    )

    if not response_messages:
        return "Sorry, I couldn't get a response.", []

    assistant_response_message = response_messages[0]
    content = assistant_response_message.content
    processed_function_calls = []

    if assistant_response_message.tool_calls:
        for tool_call in assistant_response_message.tool_calls:
            if tool_call.function.name == "GetWeather":
                args = json.loads(tool_call.function.arguments)
                location = args.get("location")
                weather_type = args.get("type", "current")
                
                print(f"\nCalling WeatherPlugin.GetWeather for: {location} ({weather_type})")
                
                weather_plugin_instance = kernel.plugins.get("WeatherPlugin")
                if not weather_plugin_instance:
                     raise ValueError("WeatherPlugin not found in kernel.")
                
                get_weather_function = weather_plugin_instance.get("GetWeather")
                if not get_weather_function:
                    raise ValueError("GetWeather function not found in WeatherPlugin.")

                function_args = KernelArguments(location=location, type=weather_type)
                weather_result_fr = await kernel.invoke(get_weather_function, arguments=function_args)
                
                weather_data = str(weather_result_fr.value)

                processed_function_calls.append({
                    "name": "GetWeather",
                    "arguments": args,
                    "result": weather_data
                })
                
                followup_messages_list = list(current_messages)
                followup_messages_list.append(assistant_response_message.to_dict())

                followup_messages_list.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": weather_data
                })
                
                final_settings = AzureChatPromptExecutionSettings(tool_choice="none") 

                final_response_messages = await chat_service.complete_chat_async(
                    messages=followup_messages_list,
                    settings=final_settings
                )
                
                if final_response_messages:
                    content = final_response_messages[0].content
                else:
                    content = "Sorry, I couldn't process the weather information."
                
                break 
    
    return content, processed_function_calls

async def orchestration_chat():
    """Run the orchestration chat"""
    print("Setting up Semantic Kernel orchestration...")
    
    kernel = setup_kernel_with_openai()
    await setup_weather_plugin(kernel)
    
    print("\nWelcome to the Multi-Agent Chat!")
    print("You can ask general questions or about the weather.")
    print("Type 'exit' to quit.")
    
    chat_history_list = [] 
    
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() == "exit":
                print("Exiting chat...")
                break
            if not user_input.strip():
                continue
                
            response_content, f_calls = await chat_with_function_calling(
                kernel, 
                user_input,
                chat_history_list
            )
            
            chat_history_list.append({"role": "user", "content": user_input})
            if response_content:
                 chat_history_list.append({"role": "assistant", "content": response_content})
            
            if f_calls:
                print("\n[Function calls processed]")
            
            print(f"Agent: {response_content}")
            
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
