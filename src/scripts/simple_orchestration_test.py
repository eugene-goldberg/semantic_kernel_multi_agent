#!/usr/bin/env python3
"""
A simplified approach to testing the orchestration capability using the recommended
ChatCompletionAgent pattern for Semantic Kernel 1.30.0+
"""

import os
import sys
import asyncio
from dotenv import load_dotenv
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.agents import ChatCompletionAgent, ChatHistoryAgentThread

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from src.agents.plugins.weather_plugin import WeatherPlugin
from src.services.weather_service import WeatherService

async def setup_agents_with_plugins():
    """Setup the chat agent with the weather plugin"""
    # Load environment variables
    load_dotenv()
    
    # Get Azure OpenAI configuration
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    # Create a kernel for the agent
    kernel = sk.Kernel()
    
    # Register the Azure OpenAI service
    chat_service = AzureChatCompletion(
        service_id="chat",
        deployment_name=deployment,
        endpoint=endpoint,
        api_key=api_key,
        api_version="2024-05-01-preview"  # Required for function calling
    )
    kernel.add_service(chat_service)
    
    # Create the weather service and plugin
    weather_service = WeatherService()
    weather_plugin_obj = WeatherPlugin(weather_service)
    
    # Register the weather plugin with the kernel
    from semantic_kernel.functions import KernelPlugin
    weather_plugin = KernelPlugin.from_object(
        "WeatherPlugin",
        weather_plugin_obj,
        description="Provides weather information for locations"
    )
    kernel.plugins["WeatherPlugin"] = weather_plugin
    
    # Create the chat agent with the kernel containing the weather plugin
    agent = ChatCompletionAgent(
        kernel=kernel,
        service=chat_service,
        name="Assistant",
        instructions="""
        You are a helpful assistant that provides friendly and accurate information.
        When the user asks about weather, use the WeatherPlugin.GetWeather function to get
        accurate weather information. The function takes 'location' parameter in the format 'city, state'
        and an optional 'type' parameter that can be 'current' or 'forecast'.
        
        For example:
        - For "What's the weather in Seattle?", call GetWeather with location='Seattle, WA'
        - For "Will it rain tomorrow in Chicago?", call GetWeather with location='Chicago, IL' and type='forecast'
        
        DO NOT make up weather information. ALWAYS use the GetWeather function for weather queries.
        For other questions, answer directly from your knowledge.
        """
    )
    
    return agent

async def test_with_predefined_inputs(agent):
    """Test the agent with predefined inputs"""
    # Create a thread for the conversation
    thread = ChatHistoryAgentThread()
    
    # Test cases
    test_inputs = [
        "What's the capital of France?",
        "What's the weather like in Seattle?",
        "Will it rain tomorrow in Chicago?",
        "Tell me about the weather in New York",
        "How do I make pasta?"
    ]
    
    for user_input in test_inputs:
        print("\n" + "-" * 60)
        print(f"User: {user_input}")
        
        # Get response from the agent
        response = await agent.get_response(
            messages=user_input,
            thread=thread
        )
        
        print(f"Agent: {response}")

async def main():
    """Main entry point"""
    try:
        print("Setting up Semantic Kernel agent with weather plugin...")
        agent = await setup_agents_with_plugins()
        
        print("\nStarting test with predefined inputs...")
        await test_with_predefined_inputs(agent)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())