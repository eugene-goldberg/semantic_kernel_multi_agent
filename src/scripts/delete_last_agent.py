#!/usr/bin/env python3
"""
Script to delete a specific agent ID from Azure AI Foundry.
"""

import requests
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

# Specific agent ID to delete
AGENT_ID = "asst_UcTrscbN86GsfTwFVcAL7IvB"  # Agent857

def main():
    """Main function to delete a specific agent ID."""
    # Get Azure AD token
    credential = AzureCliCredential()
    token = credential.get_token("https://management.azure.com/.default").token
    
    # Set headers for API requests
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"\nChecking and deleting agent: {AGENT_ID}")
    
    # Construct URL for specific agent
    url = f"{BASE_URL}/assistants/{AGENT_ID}?api-version=2024-12-01-preview"
    
    try:
        # First check if agent exists
        check_response = requests.get(url, headers=headers)
        
        if check_response.status_code == 200:
            agent_data = check_response.json()
            name = agent_data.get("name", "Unknown")
            model = agent_data.get("model", "Unknown")
            print(f"Found agent: {name} using model {model}")
            
            # Now delete the agent
            delete_response = requests.delete(url, headers=headers)
            
            if delete_response.status_code in [200, 202, 204]:
                print(f"✓ Successfully deleted agent: {AGENT_ID} ({name})")
            else:
                print(f"✗ Failed to delete agent: {AGENT_ID} ({name})")
                print(f"  Status code: {delete_response.status_code}")
        else:
            print(f"Agent not found. Status code: {check_response.status_code}")
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()