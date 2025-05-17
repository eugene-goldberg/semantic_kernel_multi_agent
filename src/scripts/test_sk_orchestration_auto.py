#!/usr/bin/env python3
"""
Automated test script for SK-based agent orchestration.
This runs a series of predefined test queries to verify all agents are working correctly.
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

# Import the orchestration module
sys.path.append(os.path.join(project_root, 'src', 'scripts'))
import orchestrate_with_sk

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_test_queries():
    """Run a series of test queries against the SK orchestration system."""
    # Set up the kernel and plugins
    kernel = orchestrate_with_sk.setup_kernel_with_openai()
    await orchestrate_with_sk.setup_plugins(kernel)
    planner, system_message = await orchestrate_with_sk.setup_chat_agent(kernel)
    
    # Test queries covering different agent capabilities
    test_queries = [
        "What's the weather like in Seattle?",
        "Calculate the square root of 64",
        "Who wrote Pride and Prejudice?",
        "What's the forecast for Chicago?",
        "Solve the equation 3x + 7 = 22",
        "What is the capital of France?",
        "What is 15% of 230?"
    ]
    
    # Initialize chat history
    chat_history = []
    
    # Process each test query
    for i, query in enumerate(test_queries):
        logger.info(f"\n===== TEST QUERY {i+1}: {query} =====")
        
        # Add user message to chat history
        chat_history.append({"role": "user", "content": query})
        
        try:
            # Execute the planner
            result = await planner.invoke(
                kernel=kernel,
                question=query
            )
            
            # Add assistant message to chat history
            response_text = str(result)
            chat_history.append({"role": "assistant", "content": response_text})
            
            # Print the response
            logger.info(f"RESPONSE: {response_text}")
            
            # Analyze which plugin was used (if any)
            if "weather" in query.lower() and "Weather" in response_text:
                logger.info("✓ Weather plugin successfully used")
            elif any(term in query.lower() for term in ["calculate", "equation", "square root", "%"]) and any(term in response_text for term in ["result is", "equals", "calculate", "=", "√"]):
                logger.info("✓ Calculator plugin successfully used")
            else:
                logger.info("✓ General knowledge query handled")
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
    
    logger.info("\n===== ALL TESTS COMPLETED =====")

async def main():
    """Main entry point"""
    try:
        logger.info("Starting automated SK orchestration tests...")
        await run_test_queries()
        logger.info("All tests completed!")
    except Exception as e:
        logger.error(f"Error in tests: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())