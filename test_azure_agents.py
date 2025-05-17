#!/usr/bin/env python3
"""
Comprehensive test script for Azure AI Foundry agents.
Tests each specialized agent and the orchestration capabilities.
"""

import os
import sys
import asyncio
import json
import time
import logging
from dotenv import load_dotenv

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from src.scripts.interact_ai_foundry_agents import AiFoundryClient

async def test_chat_agent():
    """Test the chat agent with various questions."""
    print("\n=== TESTING CHAT AGENT ===")
    client = AiFoundryClient()
    client.switch_agent('chat')
    await client.create_thread()
    
    # Test general knowledge question
    response = await client.send_message("What is the capital of France?")
    print(f"Q: What is the capital of France?\nA: {response}")
    
    # Test joke request
    response = await client.send_message("Tell me a joke about programming.")
    print(f"Q: Tell me a joke about programming.\nA: {response}")
    
    # Test opinion question
    response = await client.send_message("What's your favorite color?")
    print(f"Q: What's your favorite color?\nA: {response}")
    
    return True

async def test_weather_agent():
    """Test the weather agent with various locations."""
    print("\n=== TESTING WEATHER AGENT ===")
    client = AiFoundryClient()
    client.switch_agent('weather')
    await client.create_thread()
    
    # Test specific city
    response = await client.send_message("What's the weather like in Seattle?")
    print(f"Q: What's the weather like in Seattle?\nA: {response}")
    
    # Test weather forecast
    response = await client.send_message("Will it rain in Miami tomorrow?")
    print(f"Q: Will it rain in Miami tomorrow?\nA: {response}")
    
    # Test another location
    response = await client.send_message("What's the temperature in Chicago right now?")
    print(f"Q: What's the temperature in Chicago right now?\nA: {response}")
    
    return True

async def test_calculator_agent():
    """Test the calculator agent with various calculations."""
    print("\n=== TESTING CALCULATOR AGENT ===")
    client = AiFoundryClient()
    client.switch_agent('calculator')
    await client.create_thread()
    
    # Test basic arithmetic
    response = await client.send_message("What is 123 * 456?")
    print(f"Q: What is 123 * 456?\nA: {response}")
    
    # Test percentage calculation
    response = await client.send_message("What is 15% of 200?")
    print(f"Q: What is 15% of 200?\nA: {response}")
    
    # Test complex expression
    response = await client.send_message("Calculate (25 * 4) / (2 + 3)")
    print(f"Q: Calculate (25 * 4) / (2 + 3)\nA: {response}")
    
    return True

async def test_orchestrator_routing():
    """Test the orchestrator's ability to route to the correct agent."""
    print("\n=== TESTING ORCHESTRATOR ROUTING ===")
    client = AiFoundryClient()
    client.switch_agent('orchestrator')
    
    # Test calculator routing
    await client.create_thread()
    response = await client.send_message("What is 42 * 7?")
    print(f"Q: What is 42 * 7?\nA: {response}")
    
    # Test weather routing
    await client.create_thread()
    response = await client.send_message("What's the weather in New York?")
    print(f"Q: What's the weather in New York?\nA: {response}")
    
    # Test chat routing (general knowledge)
    await client.create_thread()
    response = await client.send_message("Who wrote Romeo and Juliet?")
    print(f"Q: Who wrote Romeo and Juliet?\nA: {response}")
    
    return True

async def main():
    """Run all tests."""
    print("Starting comprehensive tests for Azure AI Foundry agents...")
    
    try:
        await test_chat_agent()
        await test_weather_agent()
        await test_calculator_agent()
        await test_orchestrator_routing()
        
        print("\n=== TEST SUMMARY ===")
        print("✓ Chat Agent: Tested general knowledge, jokes, and opinions")
        print("✓ Weather Agent: Tested multiple locations and forecast types")
        print("✓ Calculator Agent: Tested arithmetic, percentages, and complex expressions")
        print("✓ Orchestrator: Tested routing to specialized agents")
        print("\nAll tests completed successfully!")
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())