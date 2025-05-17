#!/usr/bin/env python3
"""
Test script to verify local Semantic Kernel agent orchestration.
This tests that the orchestrator correctly routes requests to specialized agents.
"""

import os
import sys
import asyncio
import json
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from src.utils.sk_agent_factory import SkAgentFactory

async def test_orchestrator_routing():
    """Test that the orchestrator routes to the correct specialized agents."""
    load_dotenv()
    
    # Create orchestrator agent
    logger.info("Creating orchestrator agent...")
    orchestrator = SkAgentFactory.create_agent("orchestrator")
    
    # Define test cases for different agent types
    test_messages = {
        "chat": [
            "Tell me a short joke about programming.",
            "What's the capital of France?",
            "Can you recommend a good book on machine learning?"
        ],
        "weather": [
            "What's the weather like in Seattle today?",
            "Will it rain in New York tomorrow?",
            "What's the forecast for Miami this weekend?"
        ],
        "calculator": [
            "Calculate 354 * 89.",
            "What is the square root of 144?",
            "Solve the equation 3x + 12 = 39."
        ],
        "mixed": [
            "What's the weather in Chicago and calculate 15% of 85?",
            "Tell me about machine learning and solve 42/6.",
            "What's the forecast for Los Angeles and what's the square root of 256?"
        ]
    }
    
    # Run test cases and record results
    results = {}
    
    logger.info("Running test cases...")
    
    for category, messages in test_messages.items():
        logger.info(f"\nTesting {category.upper()} queries:")
        category_results = []
        
        for message in messages:
            logger.info(f"\nQuery: {message}")
            
            # Get response from orchestrator
            response = await orchestrator.agent.ask(message)
            
            logger.info(f"Response: {response}")
            
            # Record result
            category_results.append({
                "query": message,
                "response": response
            })
        
        results[category] = category_results
    
    # Save results to file
    with open("orchestration_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    logger.info("\nTest complete. Results saved to orchestration_test_results.json")
    return results

if __name__ == "__main__":
    asyncio.run(test_orchestrator_routing())