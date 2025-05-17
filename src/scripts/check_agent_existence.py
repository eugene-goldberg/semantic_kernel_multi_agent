#!/usr/bin/env python3
"""
Script to verify existence of specific agents in Azure AI Foundry.
"""

import os
import sys
import asyncio
import logging
import aiohttp
import subprocess
import json
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

async def check_agent(agent_id, base_url, api_version):
    """
    Check if a specific agent exists.
    
    Args:
        agent_id: ID of the agent to check
        base_url: Base URL for Azure AI Foundry API
        api_version: API version to use
    
    Returns:
        dict: Agent details if found, None otherwise
    """
    try:
        # Get access token
        token = await get_access_token()
        
        # Set up HTTP headers
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Generate API URL
        url = f"{base_url}/assistants/{agent_id}?api-version={api_version}"
        
        logger.info(f"Checking agent with ID: {agent_id}")
        
        # Send request to check agent
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status >= 400:
                    logger.error(f"Agent not found: {agent_id} (Status: {response.status})")
                    return None
                
                agent_data = await response.json()
                logger.info(f"Found agent: {agent_id} - {agent_data.get('name')}")
                return agent_data
    except Exception as e:
        logger.error(f"Error checking agent: {str(e)}")
        return None

async def main():
    """Main entry point."""
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
    
    # Load deployment info
    deployment_files = [
        "ai_foundry_deployment_info.json",
        "orchestration_deployment_info.json",
        "sk_deployment_info.json"
    ]
    
    # Find the first valid deployment file
    deployment_info = None
    for file_path in deployment_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    deployment_info = json.load(f)
                    if isinstance(deployment_info, dict) and any(k.endswith("_agent_id") for k in deployment_info.keys()):
                        logger.info(f"Using deployment info from {file_path}")
                        break
            except Exception as e:
                logger.error(f"Error reading {file_path}: {str(e)}")
    
    if not deployment_info:
        logger.error("No valid deployment info found")
        return
    
    # Check each agent
    agent_types = ["chat", "weather", "calculator", "orchestrator"]
    results = []
    
    print("\nVerifying agents in Azure AI Foundry:\n")
    
    for agent_type in agent_types:
        agent_id_key = f"{agent_type}_agent_id"
        if agent_id_key in deployment_info:
            agent_id = deployment_info[agent_id_key]
            agent_data = await check_agent(agent_id, base_url, api_version)
            status = "✓ Found" if agent_data else "✗ Not Found"
            model = agent_data.get("model", "N/A") if agent_data else "N/A"
            
            results.append({
                "agent_type": agent_type,
                "agent_id": agent_id,
                "status": status,
                "model": model
            })
    
    # Print results
    print(f"{'Agent Type':<15} {'Agent ID':<40} {'Status':<10} {'Model':<15}")
    print("-" * 80)
    
    for result in results:
        print(f"{result['agent_type'].capitalize():<15} {result['agent_id']:<40} {result['status']:<10} {result['model']:<15}")

if __name__ == "__main__":
    asyncio.run(main())