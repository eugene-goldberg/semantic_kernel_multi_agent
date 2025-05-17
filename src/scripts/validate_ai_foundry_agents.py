#!/usr/bin/env python3
"""
Validate Azure AI Foundry agents using both individual checks and direct API calls.
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

async def validate_agent(agent_id, base_url, api_version):
    """Validate if an agent exists and can be used."""
    try:
        # Get access token
        token = await get_access_token()
        
        # Set up HTTP headers
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Generate API URL for the specific agent
        url = f"{base_url}/assistants/{agent_id}?api-version={api_version}"
        
        # Send request to check agent
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status >= 400:
                    logger.error(f"Agent not found: {agent_id} (Status: {response.status})")
                    return {"exists": False, "details": None}
                
                agent_data = await response.json()
                logger.info(f"Found agent: {agent_id} - {agent_data.get('name')}")
                
                # Create a thread to test the agent
                thread_url = f"{base_url}/threads?api-version={api_version}"
                async with session.post(thread_url, headers=headers) as thread_response:
                    if thread_response.status >= 400:
                        logger.error(f"Failed to create thread for agent: {agent_id}")
                        return {"exists": True, "usable": False, "details": agent_data}
                    
                    thread_data = await thread_response.json()
                    thread_id = thread_data.get("id")
                    
                    if not thread_id:
                        logger.error(f"No thread ID returned for agent: {agent_id}")
                        return {"exists": True, "usable": False, "details": agent_data}
                    
                    logger.info(f"Created thread: {thread_id} for agent: {agent_id}")
                    return {"exists": True, "usable": True, "details": agent_data, "thread_id": thread_id}
    except Exception as e:
        logger.error(f"Error validating agent: {str(e)}")
        return {"exists": False, "error": str(e)}

async def main():
    """Main validation function."""
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
    
    print(f"Using base URL: {base_url}")
    
    # Load agent IDs from deployment info
    try:
        with open("ai_foundry_deployment_info.json", "r") as f:
            deployment_info = json.load(f)
        
        agent_ids = {k.replace("_agent_id", ""): v for k, v in deployment_info.items() if k.endswith("_agent_id")}
        
        print(f"\nValidating {len(agent_ids)} agents from deployment info:\n")
        
        for agent_type, agent_id in agent_ids.items():
            print(f"Validating {agent_type.capitalize()} Agent ({agent_id})...")
            result = await validate_agent(agent_id, base_url, api_version)
            
            if result["exists"]:
                status = "✓ Exists and can create threads" if result.get("usable") else "⚠ Exists but has issues"
                name = result["details"].get("name", "N/A")
                model = result["details"].get("model", "N/A")
            else:
                status = "✗ Not found"
                name = "N/A"
                model = "N/A"
            
            print(f"  Status: {status}")
            print(f"  Name: {name}")
            print(f"  Model: {model}")
            print()
    
    except Exception as e:
        logger.error(f"Validation failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())