#!/usr/bin/env python3
"""
Deploy agents to Azure AI Foundry using REST API.
This script provides a unified deployment process for all agents.
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

from src.utils.ai_foundry_deployment_manager import AiFoundryDeploymentManager, AiFoundrySettings
from src.config.agent_configs import AGENT_CONFIGS

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def deploy_single_agent(agent_type):
    """
    Deploy a single agent type.
    
    Args:
        agent_type: Type of agent to deploy ('chat', 'weather', 'calculator', 'orchestrator')
    """
    try:
        # Create deployment settings
        settings = AiFoundrySettings()
        
        # Deploy the agent
        deployment = await AiFoundryDeploymentManager.deploy_agent(agent_type, settings)
        
        # Save deployment info
        AiFoundryDeploymentManager.save_deployment_info({agent_type: deployment}, f"{agent_type}_deployment_info.json")
        
        logger.info(f"Successfully deployed {agent_type} agent")
        logger.info(f"Agent ID: {deployment['agent_id']}")
        logger.info(f"Deployment info saved to {agent_type}_deployment_info.json")
        
        return deployment
    except Exception as e:
        logger.error(f"Error deploying {agent_type} agent: {str(e)}")
        raise

async def deploy_all_agents():
    """Deploy all agents to Azure AI Foundry."""
    try:
        # Create deployment settings
        settings = AiFoundrySettings()
        
        # Deploy all agents
        logger.info("Deploying all agents...")
        deployments = await AiFoundryDeploymentManager.deploy_all_agents(settings)
        
        # Save deployment info
        AiFoundryDeploymentManager.save_deployment_info(deployments, "ai_foundry_deployment_info.json")
        
        # Print summary
        logger.info("\nDeployment Summary:")
        for agent_type, deployment in deployments.items():
            logger.info(f"- {agent_type.capitalize()} Agent: {deployment['agent_id']}")
        
        logger.info(f"\nDeployment information saved to ai_foundry_deployment_info.json")
        logger.info("\nTo interact with the deployed agents, run:")
        logger.info("python src/scripts/interact_ai_foundry_agents.py")
        
        return deployments
    except Exception as e:
        logger.error(f"Error deploying agents: {str(e)}")
        raise

async def display_agent_configs():
    """Display available agent configurations."""
    logger.info("Available Agent Configurations:")
    
    for agent_type, config in AGENT_CONFIGS.items():
        logger.info(f"\n{agent_type.upper()} AGENT:")
        logger.info(f"  Name: {config['name']}")
        logger.info(f"  Model: {config['deployment_model']}")
        logger.info(f"  Plugins: {', '.join(config['plugins']) if config['plugins'] else 'None'}")
        logger.info(f"  Instructions: {config['instructions'][:100]}...")

def print_usage():
    """Print script usage information."""
    print("\nUsage:")
    print("  python deploy_ai_foundry_agents.py [command]")
    print("\nCommands:")
    print("  all           - Deploy all agents (default if no command is provided)")
    print("  chat          - Deploy only the chat agent")
    print("  weather       - Deploy only the weather agent")
    print("  calculator    - Deploy only the calculator agent")
    print("  orchestrator  - Deploy only the orchestrator agent")
    print("  info          - Display agent configurations")
    print("  help          - Show this help message")

async def main():
    """Main entry point."""
    # Load environment variables
    load_dotenv()
    load_dotenv('.env.ai_foundry')
    
    # Process command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
    else:
        command = "all"  # Default command
    
    try:
        if command == "all":
            await deploy_all_agents()
        elif command == "chat":
            await deploy_single_agent("chat")
        elif command == "weather":
            await deploy_single_agent("weather")
        elif command == "calculator":
            await deploy_single_agent("calculator")
        elif command == "orchestrator":
            await deploy_single_agent("orchestrator")
        elif command == "info":
            await display_agent_configs()
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