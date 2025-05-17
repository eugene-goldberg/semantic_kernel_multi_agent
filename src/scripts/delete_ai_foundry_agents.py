#!/usr/bin/env python3
"""
Script to delete all agents deployed to Azure AI Foundry.
This cleans up resources created during deployment.
"""

import os
import sys
import json
import asyncio
import logging
import aiohttp
import subprocess
from dotenv import load_dotenv

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

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

async def delete_agent(agent_id, base_url, api_version):
    """
    Delete a single agent from Azure AI Foundry.
    
    Args:
        agent_id: ID of the agent to delete
        base_url: Base URL for Azure AI Foundry API
        api_version: API version to use
    
    Returns:
        bool: True if successful, False otherwise
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
        
        logger.info(f"Deleting agent with ID: {agent_id}")
        
        # Send delete request
        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=headers) as response:
                if response.status >= 400:
                    error_text = await response.text()
                    logger.error(f"Error deleting agent: {error_text}")
                    return False
                
                logger.info(f"Successfully deleted agent: {agent_id}")
                return True
    except Exception as e:
        logger.error(f"Error deleting agent: {str(e)}")
        return False

async def delete_all_agents():
    """
    Delete all agents from Azure AI Foundry based on deployment info.
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
    
    logger.info(f"Using base URL: {base_url}")
    
    # Load deployment info
    deployment_files = [
        "ai_foundry_deployment_info.json",
        "orchestration_deployment_info.json",
        "sk_deployment_info.json"
    ]
    
    deployed_agents = set()
    for file_path in deployment_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    deployment_info = json.load(f)
                    
                # Extract agent IDs
                for key, value in deployment_info.items():
                    if key.endswith("_agent_id") and isinstance(value, str) and value.startswith("asst_"):
                        deployed_agents.add(value)
            except Exception as e:
                logger.error(f"Error reading {file_path}: {str(e)}")
    
    if not deployed_agents:
        logger.warning("No deployed agents found in deployment info files")
        return
    
    logger.info(f"Found {len(deployed_agents)} agents to delete")
    
    # Delete each agent
    results = []
    for agent_id in deployed_agents:
        result = await delete_agent(agent_id, base_url, api_version)
        results.append((agent_id, result))
    
    # Print summary
    logger.info("\nDeletion Summary:")
    successful = [agent_id for agent_id, result in results if result]
    failed = [agent_id for agent_id, result in results if not result]
    
    if successful:
        logger.info(f"Successfully deleted {len(successful)} agents")
        for agent_id in successful:
            logger.info(f"- {agent_id}")
    
    if failed:
        logger.warning(f"Failed to delete {len(failed)} agents")
        for agent_id in failed:
            logger.warning(f"- {agent_id}")
    
    # Clear deployment info files
    for file_path in deployment_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, "w") as f:
                    json.dump({"deployment_status": "deleted"}, f, indent=2)
                logger.info(f"Updated {file_path} to reflect deletions")
            except Exception as e:
                logger.error(f"Error updating {file_path}: {str(e)}")

async def main():
    """Main entry point."""
    try:
        await delete_all_agents()
        print("Agent deletion process completed.")
    except Exception as e:
        logger.error(f"Error in deletion process: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())