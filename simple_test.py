#!/usr/bin/env python3
"""
Simplified test script for Semantic Kernel orchestration.
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
    
    print("Weather plugin registered successfully!")
    return weather_plugin

async def simple_weather_test(kernel):
    """Test weather plugin directly"""
    # Get the weather function directly
    weather_plugin = kernel.plugins["WeatherPlugin"]
    get_weather_function = weather_plugin["GetWeather"]
    
    # Call the weather function directly for Seattle
    print("Testing GetWeather function directly for Seattle...")
    weather_args = KernelArguments(location="Seattle, WA", type="current")
    weather_result = await kernel.invoke(get_weather_function, arguments=weather_args)
    
    print(f"Weather result: {weather_result}")
    
    return weather_result

async def test_direct_chat_completion(kernel, query):
    """Test direct chat completion with Azure OpenAI"""
    print(f"Testing direct chat completion with query: {query}")
    
    # Create a chat history
    history = ChatHistory()
    history.add_system_message("You are a helpful assistant.")
    history.add_user_message(query)
    
    # Create execution settings
    settings = AzureChatPromptExecutionSettings(
        service_id="chat",
        ai_model_id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        temperature=0
    )
    
    # Create a basic prompt template
    prompt_template = "{{$history}}\nAssistant: "
    
    # Register the prompt as a kernel function
    from semantic_kernel.functions import KernelFunction
    
    kernel.add_function(
        function=KernelFunction.from_prompt(
            prompt=prompt_template,
            kernel=kernel,
            function_name="chat",
            plugin_name="assistant"
        )
    )
    
    # Get the function
    chat_function = kernel.functions.get_function("assistant", "chat")
    
    # Invoke the function
    arguments = KernelArguments(history=history)
    result = await kernel.invoke(chat_function, arguments=arguments, settings=settings)
    
    print(f"Chat completion result: {result}")
    return str(result)

async def main():
    """Main entry point"""
    try:
        print("Setting up Semantic Kernel...")
        kernel = setup_kernel_with_openai()
        await setup_weather_plugin(kernel)
        
        # Test weather function directly
        weather_result = await simple_weather_test(kernel)
        
        # Test chat completion
        chat_result = await test_direct_chat_completion(kernel, "What is the capital of France?")
        
        print("\nTest complete!")
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())