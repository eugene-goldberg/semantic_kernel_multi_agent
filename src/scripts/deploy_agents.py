#!/usr/bin/env python3
import asyncio
import os
import json
import sys

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from src.utils.azure_agent_factory import AzureAgentFactory
from src.config.settings import AZURE_AI_HUB_NAME, AZURE_AI_PROJECT_NAME

async def deploy_agents():
    """Deploy agents to Azure AI Agent Service within a specific Hub and Project"""
    try:
        print("Connecting to Azure AI Foundry...")
        client = await AzureAgentFactory.create_client()
        
        # Display connection info
        hub_project = f"{AZURE_AI_HUB_NAME}/{AZURE_AI_PROJECT_NAME}" if AZURE_AI_HUB_NAME and AZURE_AI_PROJECT_NAME else "configured Hub/Project"
        print(f"Connected to {hub_project}")
        
        print("\nDeploying Chat Agent...")
        chat_agent = await AzureAgentFactory.deploy_chat_agent(client)
        
        print("\nDeploying Weather Agent...")
        weather_agent = await AzureAgentFactory.deploy_weather_agent(client)
        
        # Create a deployment info file for future reference
        deployment_info = {
            "hub_name": AZURE_AI_HUB_NAME,
            "project_name": AZURE_AI_PROJECT_NAME,
            "chat_agent_id": chat_agent.id,
            "weather_agent_id": weather_agent.id,
            "deployment_time": chat_agent.created_at.isoformat() if hasattr(chat_agent, 'created_at') else None
        }
        
        # Save deployment info to file
        with open("deployment_info.json", "w") as f:
            json.dump(deployment_info, f, indent=2)
        
        print("\nDeployment complete!")
        print(f"Chat Agent ID: {chat_agent.id}")
        print(f"Weather Agent ID: {weather_agent.id}")
        print(f"\nAgents deployed to Hub: {AZURE_AI_HUB_NAME}, Project: {AZURE_AI_PROJECT_NAME}")
        print("Deployment info saved to deployment_info.json")
        
    except Exception as e:
        print(f"Error during deployment: {str(e)}")
        # Print more detailed error information for troubleshooting
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(deploy_agents())