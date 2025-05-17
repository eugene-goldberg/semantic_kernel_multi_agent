#!/usr/bin/env python3
"""
Script to delete specific agent IDs from Azure AI Foundry.
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

# Specific agent IDs to delete
AGENT_IDS = [
    "asst_IoApfRbXaU3TjoUYDsiPkHNN",  # Agent608
    "asst_OqHBKHPpwRNhGWksATgMUrD1",  # WeatherAgent
    "asst_JkErsk8DfToMZ4HsueeqE9EP",  # ChatAgent
]

def main():
    """Main function to delete specific agent IDs."""
    # Get Azure AD token
    credential = AzureCliCredential()
    token = credential.get_token("https://management.azure.com/.default").token
    
    # Set headers for API requests
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\nDeleting specific Azure AI Foundry agents:")
    print("\nAgent ID                              Status")
    print("-" * 50)
    
    successful_deletions = []
    failed_deletions = []
    
    for agent_id in AGENT_IDS:
        # Construct URL for specific agent
        url = f"{BASE_URL}/assistants/{agent_id}?api-version=2024-12-01-preview"
        
        try:
            # First check if agent exists
            check_response = requests.get(url, headers=headers)
            
            if check_response.status_code == 200:
                agent_data = check_response.json()
                name = agent_data.get("name", "Unknown")
                
                # Now delete the agent
                delete_response = requests.delete(url, headers=headers)
                
                if delete_response.status_code in [200, 202, 204]:
                    print(f"{agent_id}   Deleted successfully ({name})")
                    successful_deletions.append((agent_id, name))
                else:
                    error_msg = f"Failed to delete (Status: {delete_response.status_code})"
                    print(f"{agent_id}   {error_msg}")
                    failed_deletions.append((agent_id, name, error_msg))
            else:
                error_msg = f"Not found (Status: {check_response.status_code})"
                print(f"{agent_id}   {error_msg}")
                failed_deletions.append((agent_id, "Unknown", error_msg))
        
        except Exception as e:
            logger.error(f"Error deleting agent {agent_id}: {str(e)}")
            error_msg = f"Error: {str(e)}"
            print(f"{agent_id}   {error_msg}")
            failed_deletions.append((agent_id, "Unknown", error_msg))
    
    # Print summary
    print("\nDeletion Summary:")
    print(f"Successfully deleted {len(successful_deletions)} agents:")
    for agent_id, name in successful_deletions:
        print(f"- {agent_id} ({name})")
    
    if failed_deletions:
        print(f"\nFailed to delete {len(failed_deletions)} agents:")
        for agent_id, name, error in failed_deletions:
            print(f"- {agent_id} ({name}): {error}")

if __name__ == "__main__":
    main()