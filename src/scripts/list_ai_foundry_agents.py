#!/usr/bin/env python3
"""
Script to list all agents deployed to Azure AI Foundry.
Displays agent IDs, names, and models.
"""

import os
import sys
import asyncio
import logging
import aiohttp
import subprocess
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def get_access_token():
    """
    Get an Azure AD access token using the Azure CLI.
    
    Returns:
        str: The access token
    """
    try:
        result = subprocess.run(
            ["az", "account", "get-access-token", "--query", "accessToken", "-o", "tsv"],
            capture_output=True,
            text=True,
            check=True
        )
        token = result.stdout.strip()
        return token
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get access token: {e.stderr}")
        raise

async def list_agents():
    """
    List all agents deployed to Azure AI Foundry.
    """
    # Load environment variables
    load_dotenv()
    load_dotenv('.env.ai_foundry')
    
    # Get configuration from environment
    subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
    resource_group = os.getenv("AZURE_RESOURCE_GROUP")
    workspace_name = os.getenv("AZURE_WORKSPACE_NAME")
    region = os.getenv("AZURE_REGION", "eastus")
    api_version = os.getenv("AI_FOUNDRY_API_VERSION", "2024-12-01-preview")
    
    # Construct base URL
    base_url = f"https://{region}.api.azureml.ms/agents/v1.0/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.MachineLearningServices/workspaces/{workspace_name}"
    
    try:
        # Get access token
        token = await get_access_token()
        
        # Set up HTTP headers
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Generate API URL for listing assistants
        url = f"{base_url}/assistants?api-version={api_version}"
        
        logger.info(f"Listing agents from: {base_url}")
        
        # Send request to list agents
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status >= 400:
                    error_text = await response.text()
                    logger.error(f"Error listing agents: {error_text}")
                    return
                
                data = await response.json()
                agents = data.get("value", [])
                
                if not agents:
                    print("No agents found in Azure AI Foundry.")
                    return
                
                print(f"\nFound {len(agents)} agents in Azure AI Foundry:\n")
                print(f"{'ID':<40} {'Name':<20} {'Model':<15}")
                print("-" * 75)
                
                for agent in agents:
                    agent_id = agent.get("id", "N/A")
                    name = agent.get("name", "N/A")
                    model = agent.get("model", "N/A")
                    
                    print(f"{agent_id:<40} {name:<20} {model:<15}")
                
                # Compare with our deployment info
                with open("ai_foundry_deployment_info.json", "r") as f:
                    import json
                    deployment_info = json.load(f)
                
                deployed_ids = [v for k, v in deployment_info.items() if k.endswith("_agent_id")]
                
                print("\nDeployment Status Verification:")
                for agent_type in ["chat", "weather", "calculator", "orchestrator"]:
                    agent_id_key = f"{agent_type}_agent_id"
                    if agent_id_key in deployment_info:
                        agent_id = deployment_info[agent_id_key]
                        found = any(a.get("id") == agent_id for a in agents)
                        status = "✓ Found" if found else "✗ Not Found"
                        print(f"{agent_type.capitalize()} Agent ({agent_id}): {status}")
                
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    """Main entry point."""
    await list_agents()

if __name__ == "__main__":
    asyncio.run(main())