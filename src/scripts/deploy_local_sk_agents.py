#!/usr/bin/env python3
"""
Deploy Semantic Kernel agents locally for testing without Azure AI Service.
This creates local Semantic Kernel agents using the Azure OpenAI client.
"""

import os
import sys
import json
import asyncio
import logging
from dotenv import load_dotenv

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from src.config.agent_configs import AGENT_CONFIGS 
from src.utils.sk_agent_factory import SkAgentFactory

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def create_and_test_agent(agent_type):
    """
    Create and test a single agent type locally.
    
    Args:
        agent_type: Type of agent to create ('chat', 'weather', 'calculator', 'orchestrator')
    """
    try:
        # Create the agent using the factory
        agent = await SkAgentFactory.create_agent(agent_type)
        
        # Test the agent with a simple message
        logger.info(f"Testing {agent_type} agent...")
        
        if agent_type == "chat":
            test_message = "Tell me a short joke."
        elif agent_type == "weather":
            test_message = "What's the weather like in Seattle?"
        elif agent_type == "calculator":
            test_message = "Calculate 356 * 42."
        elif agent_type == "orchestrator":
            test_message = "I need to know the weather in Boston and then calculate the square root of 169."
        else:
            test_message = "Hello, how can you help me today?"
            
        # Get response from agent
        response = await agent.ask(test_message)
        
        logger.info(f"{agent_type.capitalize()} Agent Response: {response}")
        
        return {
            "agent_type": agent_type,
            "status": "success",
            "test_message": test_message,
            "response": response
        }
    except Exception as e:
        logger.error(f"Error creating/testing {agent_type} agent: {str(e)}")
        return {
            "agent_type": agent_type,
            "status": "error",
            "error": str(e)
        }

async def create_and_test_all_agents():
    """Create and test all agent types locally."""
    try:
        logger.info("Creating and testing all local agents...")
        results = {}
        
        for agent_type in AGENT_CONFIGS.keys():
            result = await create_and_test_agent(agent_type)
            results[agent_type] = result
            
        # Save results to file
        with open("local_agents_test_results.json", "w") as f:
            json.dump(results, f, indent=2)
            
        logger.info("Local agent testing complete. Results saved to local_agents_test_results.json")
        return results
    except Exception as e:
        logger.error(f"Error testing agents: {str(e)}")
        raise

def print_usage():
    """Print script usage information."""
    print("\nUsage:")
    print("  python deploy_local_sk_agents.py [command]")
    print("\nCommands:")
    print("  all           - Test all agents (default if no command is provided)")
    print("  chat          - Test only the chat agent")
    print("  weather       - Test only the weather agent")
    print("  calculator    - Test only the calculator agent")
    print("  orchestrator  - Test only the orchestrator agent")
    print("  help          - Show this help message")

async def main():
    """Main entry point."""
    # Load environment variables
    load_dotenv()
    
    # Process command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
    else:
        command = "all"  # Default command
    
    try:
        if command == "all":
            await create_and_test_all_agents()
        elif command == "chat":
            await create_and_test_agent("chat")
        elif command == "weather":
            await create_and_test_agent("weather")
        elif command == "calculator":
            await create_and_test_agent("calculator")
        elif command == "orchestrator":
            await create_and_test_agent("orchestrator")
        elif command in ["help", "-h", "--help"]:
            print_usage()
        else:
            print(f"Unknown command: {command}")
            print_usage()
    except Exception as e:
        logger.error(f"Deployment failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())