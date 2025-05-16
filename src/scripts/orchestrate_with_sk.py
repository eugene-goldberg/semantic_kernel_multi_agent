#!/usr/bin/env python3
"""
Orchestration system using Semantic Kernel to delegate from chat agent to weather agent.
"""

import os
import sys
import asyncio
import json
from dotenv import load_dotenv
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureTextCompletion
from semantic_kernel.planners import FunctionCallingStepwisePlanner

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
    
    # Add Azure OpenAI chat service
    kernel.add_service(
        AzureChatCompletion(
            service_id="chat", 
            deployment_name=deployment,
            endpoint=endpoint,
            api_key=api_key
        )
    )
    
    return kernel

async def setup_chat_agent(kernel):
    """Set up the chat agent with function calling capabilities"""
    # Create a planner that can use function calling
    planner = FunctionCallingStepwisePlanner(
        kernel=kernel,
        service_id="chat",
        excluded_plugins=[],
        excluded_functions=[]
    )
    
    # Create the system message
    system_message = """
    You are a helpful assistant that provides friendly, concise, and accurate information.
    When the user asks about weather, you should call the GetWeather function to get accurate weather information.
    Always extract the location from the user's question when dealing with weather queries.
    
    For example:
    - If they ask 'What's the weather like in Seattle?', call GetWeather with location='Seattle, WA'
    - If they ask 'Will it rain tomorrow in Chicago?', call GetWeather with location='Chicago, IL' and type='forecast'
    
    DO NOT make up weather information. ALWAYS use the GetWeather function for weather queries.
    For other questions, answer directly from your knowledge.
    """
    
    return planner, system_message

async def setup_weather_plugin(kernel):
    """Set up the weather plugin"""
    # Create a weather service instance
    weather_service = WeatherService()
    
    # Create the weather plugin
    weather_plugin = WeatherPlugin(weather_service)
    
    # Import the plugin to the kernel
    kernel.import_plugin_from_object(weather_plugin, plugin_name="WeatherPlugin")
    
    return weather_plugin

async def orchestration_chat():
    """Run the orchestration chat"""
    print("Setting up Semantic Kernel orchestration...")
    
    # Set up the kernel
    kernel = setup_kernel_with_openai()
    
    # Set up the weather plugin
    await setup_weather_plugin(kernel)
    
    # Set up the chat agent with function calling
    planner, system_message = await setup_chat_agent(kernel)
    
    print("\nWelcome to the Multi-Agent Chat!")
    print("You can ask general questions or about the weather.")
    print("Type 'exit' to quit.")
    
    # Chat loop
    chat_history = []
    
    while True:
        try:
            user_input = input("\nYou: ")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting chat...")
            break
        
        if user_input.lower() == "exit":
            print("Exiting chat...")
            break
        
        # Add user message to chat history
        chat_history.append({"role": "user", "content": user_input})
        
        # Execute the planner to potentially call functions
        try:
            # Execute with function calling planner
            result = await planner.invoke(
                goal=user_input,
                system_message=system_message,
                chat_history=chat_history
            )
            
            # Add assistant message to chat history
            chat_history.append({"role": "assistant", "content": str(result)})
            
            # Print the response
            print(f"Agent: {result}")
            
        except Exception as e:
            print(f"Error: {str(e)}")
            print("Let me try again with a simpler approach...")
            
            # Fallback to regular completion
            response = await kernel.invoke_prompt(
                prompt=f"System: {system_message}\n\nUser: {user_input}",
                service_id="chat"
            )
            print(f"Agent: {response}")
            
            # Add to chat history
            chat_history.append({"role": "assistant", "content": str(response)})

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