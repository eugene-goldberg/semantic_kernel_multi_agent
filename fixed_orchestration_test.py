#!/usr/bin/env python3
"""
Fixed Semantic Kernel orchestration test compatible with SK 1.30.0.
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

async def test_weather_function(kernel):
    """Test the weather function directly"""
    try:
        weather_plugin = kernel.plugins["WeatherPlugin"]
        weather_function = weather_plugin["GetWeather"]
        
        # Try with different cities to increase chances of success
        test_locations = [
            "Seattle, WA",
            "New York, NY",
            "Los Angeles, CA",
            "Chicago, IL",
            "Denver, CO"
        ]
        
        for location in test_locations:
            try:
                print(f"\nTesting weather function with location: {location}")
                args = KernelArguments(location=location, type="current")
                result = await kernel.invoke(weather_function, arguments=args)
                print(f"Weather result: {result}")
                
                # If successful, return the result and location
                return result, location
            except Exception as e:
                print(f"Error with location {location}: {str(e)}")
                continue
        
        # If all attempts failed
        print("All weather function tests failed")
        return None, None
    except Exception as e:
        print(f"Error testing weather function: {str(e)}")
        return None, None

async def test_chat_with_function_calling(kernel, location):
    """Test chat with function calling for weather queries"""
    if not location:
        print("No valid location found. Skipping chat test.")
        return
    
    chat_history = ChatHistory()
    
    # Add system message
    chat_history.add_system_message("""
    You are a helpful assistant that provides friendly, concise, and accurate information.
    When asked about weather, you should use the GetWeather function to get accurate weather information.
    Always extract the location from the user's question when dealing with weather queries.
    
    For example:
    - If they ask 'What's the weather like in Seattle?', call GetWeather with location='Seattle, WA'
    - If they ask 'Will it rain tomorrow in Chicago?', call GetWeather with location='Chicago, IL' and type='forecast'
    """)
    
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
    settings = AzureChatPromptExecutionSettings(
        service_id="chat",
        ai_model_id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        temperature=0,
        tool_choice="auto",
        tools=tools
    )
    
    # Create a query using the location that worked
    query = f"What's the weather like in {location} right now?"
    print(f"\nTesting chat with query: '{query}'")
    
    chat_history.add_user_message(query)
    
    # Get chat service from kernel
    chat_service = kernel.get_service("chat")
    if not chat_service:
        print("Chat service not found")
        return
    
    try:
        # Create function to handle chat
        from semantic_kernel.functions import KernelFunction
        
        prompt_template = "{{$history}}\nAssistant: "
        
        chat_function = KernelFunction.from_prompt(
            prompt=prompt_template,
            function_name="chat",
            plugin_name="ChatPlugin",  # Plugin name is required in SK 1.30.0
            description="Chat with the user and respond to their queries"
        )
        
        kernel.add_function("ChatPlugin", chat_function)
        
        arguments = KernelArguments(history=chat_history)
        
        # Get response
        response = await kernel.invoke(chat_function, arguments=arguments, settings=settings)
        
        print(f"Initial response: {response}")
        
        # Check for tool calls
        if hasattr(response, 'tool_calls') and response.tool_calls:
            print("\nFunction call detected!")
            
            for tool_call in response.tool_calls:
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
                    
                    print(f"Weather data: {weather_result}")
                    
                    # Add assistant and tool message to history
                    chat_history.add_assistant_message(str(response))
                    chat_history.add_tool_message(tool_call.id, str(weather_result))
                    
                    # Get final response
                    settings_without_tools = AzureChatPromptExecutionSettings(
                        service_id="chat",
                        ai_model_id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                        temperature=0
                    )
                    
                    final_response = await kernel.invoke(
                        chat_function, 
                        arguments=KernelArguments(history=chat_history),
                        settings=settings_without_tools
                    )
                    
                    print(f"\nFinal response: {final_response}")
    except Exception as e:
        print(f"Error in chat with function calling: {str(e)}")
        import traceback
        traceback.print_exc()

async def run_test():
    """Run the main orchestration test"""
    print("Setting up Semantic Kernel orchestration...")
    
    # Setup kernel
    kernel = setup_kernel()
    
    # Register weather plugin
    await register_weather_plugin(kernel)
    
    # Test weather function directly
    weather_result, working_location = await test_weather_function(kernel)
    
    # Test chat with function calling
    await test_chat_with_function_calling(kernel, working_location)
    
    print("\nOrchestration testing complete")

if __name__ == "__main__":
    asyncio.run(run_test())