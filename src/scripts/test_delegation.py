#!/usr/bin/env python3
"""
Test script for verifying orchestrated delegation to specialized agents.
This script runs a set of queries that test all three agent types with explicit prompts.
"""

import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from src.agents.chat_agent import ChatAgent
from src.agents.weather_agent import WeatherAgent
from src.agents.calculator_agent_sk import CalculatorAgent
from src.agents.orchestrator_agent_updated import OrchestratorAgent
from src.utils.sk_agent_factory import SkAgentFactory

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_delegation():
    """Test orchestrator delegation to each specialized agent."""
    logger.info("Setting up agents for delegation testing...")
    
    # Create service for all agents
    service = SkAgentFactory.create_service()
    
    # Create specialized agents
    chat_agent = ChatAgent(service=service)
    weather_agent = WeatherAgent(service=service)
    calculator_agent = CalculatorAgent(service=service)
    
    # Create orchestrator with all specialized agents
    orchestrator = OrchestratorAgent(service=service)
    orchestrator_agent = orchestrator.get_agent()
    
    # Test queries with explicit instructions mentioning the target agent
    test_queries = [
        {
            "query": "I need to use the ChatAgent to tell me who wrote Pride and Prejudice",
            "expected_agent": "chat",
            "description": "Explicit Chat Agent request"
        },
        {
            "query": "Please use the WeatherAgent to tell me the weather in Seattle",
            "expected_agent": "weather",
            "description": "Explicit Weather Agent request"
        },
        {
            "query": "I want the CalculatorAgent to calculate the square root of 64",
            "expected_agent": "calculator",
            "description": "Explicit Calculator Agent request"
        },
        {
            "query": "Which agent should I use to find the weather in Boston?",
            "expected_agent": "weather",
            "description": "Indirect Weather Agent reference"
        },
        {
            "query": "Can you help me solve 15% of 230?",
            "expected_agent": "calculator",
            "description": "Indirect Calculator Agent reference"
        },
        {
            "query": "Tell me about the history of artificial intelligence",
            "expected_agent": "chat",
            "description": "Implicit Chat Agent requirement"
        }
    ]
    
    for i, test in enumerate(test_queries):
        query = test["query"]
        expected_agent = test["expected_agent"]
        description = test["description"]
        
        logger.info(f"\n===== TEST {i+1}: {description} =====")
        logger.info(f"Query: {query}")
        logger.info(f"Expected Agent: {expected_agent}")
        
        try:
            # Get response from orchestrator
            response = await orchestrator_agent.get_response(messages=query)
            response_text = str(response)
            
            logger.info(f"Response: {response_text}")
            
            # Check if the response mentions the expected agent type
            agent_mentions = {
                "chat": ["chat agent", "chatgpt", "chat specialist", "general knowledge"],
                "weather": ["weather agent", "weather specialist", "weather information", "forecast"],
                "calculator": ["calculator agent", "calculator specialist", "calculation", "compute", "square root", "mathematical", "15%", "percent"]
            }
            
            # Check if expected agent's keywords are in the response
            found_mentions = [term for term in agent_mentions[expected_agent] 
                             if term.lower() in response_text.lower()]
            
            if found_mentions:
                logger.info(f"✓ SUCCESS: Response contains keywords related to {expected_agent.upper()} Agent: {found_mentions}")
            else:
                logger.warning(f"✗ FAILURE: Response does not contain keywords for {expected_agent.upper()} Agent")
                
            # Check if the expected agent appears to be handling the query
            if expected_agent == "chat" and not any(term.lower() in response_text.lower() 
                                                for agent in ["weather", "calculator"] 
                                                for term in agent_mentions[agent]):
                logger.info("✓ ChatAgent appears to be handling this query (no other agent keywords found)")
            elif expected_agent == "weather" and any(term.lower() in response_text.lower() for term in ["temperature", "forecast", "weather", "seattle", "boston"]):
                logger.info("✓ WeatherAgent appears to be handling this query")
            elif expected_agent == "calculator" and any(term.lower() in response_text.lower() for term in ["result", "answer", "=", "equals", "15%", "percent", "square root", "64", "8"]):
                logger.info("✓ CalculatorAgent appears to be handling this query")
            else:
                logger.warning("? Unclear which agent is handling the query based on response content")
                
        except Exception as e:
            logger.error(f"Error testing orchestrator: {str(e)}")
            import traceback
            traceback.print_exc()
    
    logger.info("\n===== ALL DELEGATION TESTS COMPLETED =====")

async def main():
    """Main entry point"""
    try:
        await test_delegation()
    except Exception as e:
        logger.error(f"Error in tests: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())