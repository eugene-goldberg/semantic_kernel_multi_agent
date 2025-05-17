#!/usr/bin/env python3
"""
Script to check specific agent IDs in Azure AI Foundry.
"""

import requests
import json
import logging
from azure.identity import AzureCliCredential

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Azure AI Foundry settings
SUBSCRIPTION_ID = "514bd6d3-2c02-45c6-a86f-29cf262a379a"
RESOURCE_GROUP = "semantic-kernel-multi-agent-rg"
WORKSPACE_NAME = "sk-multi-agent-project"
REGION = "eastus"

# Base URL for the Azure AI Foundry API
BASE_URL = f"https://{REGION}.api.azureml.ms/agents/v1.0/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/{RESOURCE_GROUP}/providers/Microsoft.MachineLearningServices/workspaces/{WORKSPACE_NAME}"

# Specific agent IDs to check
AGENT_IDS = [
    "asst_IoApfRbXaU3TjoUYDsiPkHNN",  # Agent608
    "asst_OqHBKHPpwRNhGWksATgMUrD1",  # WeatherAgent
    "asst_JkErsk8DfToMZ4HsueeqE9EP",  # ChatAgent
]

def main():
    """Main function to check specific agent IDs."""
    # Get Azure AD token
    credential = AzureCliCredential()
    token = credential.get_token("https://management.azure.com/.default").token
    
    # Set headers for API requests
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\nChecking specific Azure AI Foundry agents:")
    print("\nAgent ID                              Name/Type              Status   Model")
    print("-" * 75)
    
    for agent_id in AGENT_IDS:
        # Construct URL for specific agent
        url = f"{BASE_URL}/assistants/{agent_id}?api-version=2024-12-01-preview"
        
        try:
            # Make API request to check agent
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                agent_data = response.json()
                name = agent_data.get("name", "Unknown")
                model = agent_data.get("model", "Unknown")
                print(f"{agent_id}   {name:<20}   Exists   {model}")
            else:
                print(f"{agent_id}   Not found (Status: {response.status_code})")
        
        except Exception as e:
            logger.error(f"Error checking agent {agent_id}: {str(e)}")
            print(f"{agent_id}   Error: {str(e)}")
    
    # Now try to list all agents
    list_url = f"{BASE_URL}/assistants?api-version=2024-12-01-preview"
    try:
        list_response = requests.get(list_url, headers=headers)
        if list_response.status_code == 200:
            agents_data = list_response.json()
            agent_count = len(agents_data.get("value", []))
            print(f"\nAPI List endpoint returned {agent_count} agents")
            
            if agent_count > 0:
                print("\nAgents from list endpoint:")
                for agent in agents_data.get("value", []):
                    agent_id = agent.get("id", "Unknown")
                    name = agent.get("name", "Unknown")
                    model = agent.get("model", "Unknown")
                    print(f"{agent_id}   {name:<20}   {model}")
        else:
            print(f"\nFailed to list agents (Status: {list_response.status_code})")
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        print(f"\nError listing agents: {str(e)}")

if __name__ == "__main__":
    main()