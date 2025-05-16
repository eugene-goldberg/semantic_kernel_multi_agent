#!/usr/bin/env python3
import asyncio
import os
import sys

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.orchestration.agent_thread import AgentThread
from semantic_kernel.agents import ChatCompletionAgent
from src.agents.plugins.weather_plugin import WeatherPlugin
from src.config.settings import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_DEPLOYMENT_NAME
)

async def test_local_agents():
    """Test local agent functionality using Semantic Kernel"""
    print("Initializing agents...")
    
    # Create the kernel
    kernel = Kernel()
    
    # Configure Azure OpenAI service
    service = AzureChatCompletion(
        deployment_name=AZURE_OPENAI_DEPLOYMENT_NAME,
        endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY
    )
    
    # Create a chat agent
    chat_agent = ChatCompletionAgent(
        service=service,
        kernel=kernel,
        name="ChatAgent",
        instructions=(
            "You are a helpful assistant that provides friendly, concise, and accurate information. "
            "You should be conversational but prioritize accuracy and brevity over verbosity. "
            "If you don't know something, admit it clearly rather than making guesses."
        )
    )
    
    # Create the weather agent
    weather_kernel = Kernel()
    
    # Add the weather plugin
    weather_plugin = WeatherPlugin()
    weather_kernel.import_plugin(weather_plugin, plugin_name="WeatherPlugin")
    
    # Create the weather agent
    weather_agent = ChatCompletionAgent(
        service=service,
        kernel=weather_kernel,
        name="WeatherAgent",
        instructions=(
            "You are a weather specialist agent that provides accurate and helpful weather information "
            "for locations in the United States. "
            "You have access to real-time US weather data through your WeatherPlugin skills. "
            "When asked about weather, always use the appropriate function from WeatherPlugin to get accurate data. "
            "For current weather, use the GetCurrentWeather function. "
            "For forecasts, use the GetWeatherForecast function. "
            "Provide your answers in a friendly, concise manner, focusing on the most relevant information. "
            "If asked about weather outside the United States, politely explain that your weather data "
            "is currently limited to US locations only."
        )
    )
    
    # Create an orchestrator agent
    orchestrator_agent = ChatCompletionAgent(
        service=service,
        kernel=kernel,
        name="OrchestratorAgent",
        instructions=(
            "You are a triage agent that routes user requests to the appropriate specialist agent. "
            "If the request is about weather or forecast information for US locations, direct it to the WeatherAgent. "
            "Note that the WeatherAgent can only provide weather data for locations within the United States "
            "as it uses the National Weather Service API. "
            "For all other general questions or conversations, direct it to the ChatAgent. "
            "Your job is to determine which specialist can best answer the query and route "
            "accordingly. Do not try to answer questions yourself - your role is purely to route "
            "requests to the appropriate specialist."
        ),
        plugins=[chat_agent, weather_agent]
    )
    
    # Create a thread for conversation
    thread = AgentThread()
    
    # Test chat agent
    print("\nTesting Chat Agent...")
    response = await chat_agent.invoke_async(messages=[{"role": "user", "content": "Hello! Who are you?"}], thread=thread)
    print(f"Chat Agent Response: {response}")
    
    # Test weather agent with US location
    print("\nTesting Weather Agent with US location...")
    try:
        response = await weather_agent.invoke_async(messages=[{"role": "user", "content": "What's the weather like in Seattle?"}], thread=thread)
        print(f"Weather Agent Response: {response}")
    except Exception as e:
        print(f"Error with weather agent: {str(e)}")
    
    # Test orchestrator agent
    print("\nTesting Orchestrator Agent with weather query...")
    response = await orchestrator_agent.invoke_async(messages=[{"role": "user", "content": "What's the weather like in New York?"}], thread=thread)
    print(f"Orchestrator Agent Response: {response}")
    
    print("\nTesting Orchestrator Agent with general query...")
    response = await orchestrator_agent.invoke_async(messages=[{"role": "user", "content": "Tell me a fun fact about the moon"}], thread=thread)
    print(f"Orchestrator Agent Response: {response}")

if __name__ == "__main__":
    asyncio.run(test_local_agents())