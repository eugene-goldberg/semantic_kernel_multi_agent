#!/usr/bin/env python3
"""
Script to list all agents in Azure AI Foundry regardless of deployment info.
"""

import os
import sys
import asyncio
import json
import logging
import aiohttp
import subprocess
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def get_access_token():
    """Get an Azure AD access token using Azure CLI."""
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

async def main():
    """List all agents in Azure AI Foundry."""
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
        
        # Create request URL
        url = f"{base_url}/assistants?api-version={api_version}"
        print(f"Requesting agents from: {url}")
        
        # Get list of all agents
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status >= 400:
                    error_text = await response.text()
                    logger.error(f"Error: {response.status} - {error_text}")
                    return
                
                try:
                    data = await response.json()
                    assistants = data.get("value", [])
                    
                    print(f"\nFound {len(assistants)} assistants in Azure AI Foundry:\n")
                    
                    if not assistants:
                        print("No assistants found.")
                        return
                    
                    print(f"{'ID':<40} {'Name':<20} {'Model':<15} {'Created':<25}")
                    print("-" * 100)
                    
                    for assistant in assistants:
                        assistant_id = assistant.get("id", "N/A")
                        name = assistant.get("name", "N/A")
                        model = assistant.get("model", "N/A")
                        created_time = assistant.get("systemData", {}).get("createdAt", "N/A")
                        
                        print(f"{assistant_id:<40} {name:<20} {model:<15} {created_time:<25}")
                    
                    # Compare against our deployment info
                    print("\nComparing with current deployment info:")
                    
                    with open("ai_foundry_deployment_info.json", "r") as f:
                        deployment_info = json.load(f)
                    
                    our_agents = {v: k for k, v in deployment_info.items() if k.endswith("_agent_id")}
                    
                    for assistant in assistants:
                        assistant_id = assistant.get("id")
                        agent_type = our_agents.get(assistant_id, "Unknown")
                        if agent_type != "Unknown":
                            agent_type = agent_type.replace("_agent_id", "")
                            status = "✓ Current Deployment"
                        else:
                            status = "! Not in deployment info"
                        
                        print(f"{assistant_id} - {assistant.get('name')}: {status}")
                    
                except Exception as e:
                    logger.error(f"Error parsing response: {e}")
                    print(f"Raw response: {await response.text()}")
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())