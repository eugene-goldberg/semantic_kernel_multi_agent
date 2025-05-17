#!/usr/bin/env python3
"""
Test script for SK-based agent orchestration.
This script tests the local orchestration of SK agents.
"""

import os
import sys
import asyncio
import json
import logging
from dotenv import load_dotenv

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.functions import KernelPlugin

from src.agents.chat_agent import ChatAgent
from src.agents.weather_agent import WeatherAgent
from src.agents.calculator_agent_sk import CalculatorAgent
from src.agents.orchestrator_agent_updated import OrchestratorAgent
from src.agents.plugins.weather_plugin import WeatherPlugin
from src.agents.plugins.calculator_plugin import CalculatorPlugin

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def setup_kernel():
    """Set up a kernel with Azure OpenAI service."""
    # Load environment variables
    load_dotenv()
    
    # Get Azure OpenAI configuration
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    if not all([endpoint, api_key, deployment]):
        raise ValueError("Azure OpenAI configuration not found in environment")
    
    # Create kernel
    kernel = sk.Kernel()
    
    # Add Azure OpenAI service
    service = AzureChatCompletion(
        service_id="chat",
        deployment_name=deployment,
        endpoint=endpoint,
        api_key=api_key,
        api_version="2024-02-15-preview"
    )
    
    # For SK 1.30.0, just pass the service object
    kernel.add_service(service)
    
    return kernel, service

async def setup_plugins(kernel):
    """Set up plugins for the kernel."""
    # Create and register weather plugin
    weather_plugin_obj = WeatherPlugin()
    kernel.add_plugin(weather_plugin_obj, plugin_name="WeatherPlugin")
    
    # Create and register calculator plugin
    calculator_plugin_obj = CalculatorPlugin()
    kernel.add_plugin(calculator_plugin_obj, plugin_name="CalculatorPlugin")
    
    # Return the plugin objects (not needed for API, but kept for compatibility)
    return weather_plugin_obj, calculator_plugin_obj

async def test_weather_agent():
    """Test the weather agent directly."""
    logger.info("\n=== Testing Weather Agent ===")
    
    kernel, service = await setup_kernel()
    weather_plugin, _ = await setup_plugins(kernel)
    
    weather_agent = WeatherAgent(service=service, kernel=kernel)
    agent = weather_agent.get_agent()
    
    # Test queries
    test_queries = [
        "What's the weather like in Seattle?",
        "What's the forecast for Chicago?",
        "Should I bring an umbrella to New York tomorrow?"
    ]
    
    for query in test_queries:
        logger.info(f"\nQuery: {query}")
        
        try:
            # Use get_response with string message
            response = await agent.get_response(messages=query)
            logger.info(f"Weather Agent Response: {response}")
        except Exception as e:
            logger.error(f"Error testing weather agent: {str(e)}")

async def test_calculator_agent():
    """Test the calculator agent directly."""
    logger.info("\n=== Testing Calculator Agent ===")
    
    kernel, service = await setup_kernel()
    _, calculator_plugin = await setup_plugins(kernel)
    
    calculator_agent = CalculatorAgent(service=service, kernel=kernel)
    agent = calculator_agent.get_agent()
    
    # Test queries
    test_queries = [
        "Calculate the square root of 64",
        "What is 15% of 230?",
        "Solve the equation 3x + 7 = 22"
    ]
    
    for query in test_queries:
        logger.info(f"\nQuery: {query}")
        
        try:
            # Use get_response with string message
            response = await agent.get_response(messages=query)
            logger.info(f"Calculator Agent Response: {response}")
        except Exception as e:
            logger.error(f"Error testing calculator agent: {str(e)}")

async def test_orchestrator():
    """Test the orchestrator agent."""
    logger.info("\n=== Testing Orchestrator Agent ===")
    
    kernel, service = await setup_kernel()
    weather_plugin, calculator_plugin = await setup_plugins(kernel)
    
    # Create agents
    chat_agent = ChatAgent(service=service)
    weather_agent = WeatherAgent(service=service, kernel=kernel)
    calculator_agent = CalculatorAgent(service=service, kernel=kernel)
    
    # Create orchestrator
    orchestrator = OrchestratorAgent(service=service)
    agent = orchestrator.get_agent()
    
    # Test queries for different agent types
    test_queries = [
        {"query": "Who wrote Pride and Prejudice?", "expected_agent": "chat"},
        {"query": "What's the weather like in Seattle?", "expected_agent": "weather"},
        {"query": "Calculate the square root of 64", "expected_agent": "calculator"}
    ]
    
    for test in test_queries:
        query = test["query"]
        expected_agent = test["expected_agent"]
        
        logger.info(f"\nQuery: {query}")
        logger.info(f"Expected Agent: {expected_agent}")
        
        try:
            # Use get_response with string message
            response = await agent.get_response(messages=query)
            logger.info(f"Orchestrator Response: {response}")
            
            # Convert response to string if it's not already
            response_text = str(response)
            logger.info(f"Response type: {type(response)}")
            
            # Check if the response mentions the expected agent
            if expected_agent.lower() in response_text.lower():
                logger.info(f"✓ Correct routing to {expected_agent} Agent")
            else:
                logger.warning(f"✗ Expected routing to {expected_agent} Agent, but not found in response")
        except Exception as e:
            logger.error(f"Error testing orchestrator: {str(e)}")

async def main():
    """Main test function."""
    try:
        # Test individual agents
        await test_weather_agent()
        await test_calculator_agent()
        
        # Test orchestrator
        await test_orchestrator()
        
        logger.info("\nAll tests complete!")
    except Exception as e:
        logger.error(f"Error in tests: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())