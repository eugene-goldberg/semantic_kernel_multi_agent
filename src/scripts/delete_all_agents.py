#!/usr/bin/env python3
"""
Script to delete all agents from Azure AI Foundry.
"""

import subprocess
import requests
import json
import logging

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
    # New agents
    "asst_rQuUpLi3ZaBCRZVwp6yHOe9Q",  # OrchestratorAgent (new)
    "asst_resP7LRHCTMRFZm3H2cfXhob",  # CalculatorAgent (new)
    "asst_KVqzqMZHr3aWc7BVJrqzaalm",  # WeatherAgent (new)
    "asst_C0CmYjY7nbIAxib7pnvhMSwi",  # ChatAgent (new)
    
    # Old agents
    "asst_dJaRM1GnG0IPTYpsVFcwz4xH",  # OrchestratorAgent (old)
    "asst_C2yjyR0ZE0bxbwdxgvNM9rgH",  # CalculatorAgent (old)
    "asst_NHWTbFChLxTSF6Wbs6LjplBj",  # ChatAgent (old)
    "asst_tVx0YKu1RUEPKw3zD0LIeetD",  # WeatherAgent (old)
]

def get_access_token():
    """Get Azure AD token using the Azure CLI."""
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

def main():
    """Delete all specified agents."""
    try:
        # Get access token
        token = get_access_token()
        
        # Set up HTTP headers
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        print("\nDeleting all specified agents from Azure AI Foundry...\n")
        print(f"{'Agent ID':<40} {'Status'}")
        print("-" * 50)
        
        successful_deletions = []
        failed_deletions = []
        
        for agent_id in AGENT_IDS:
            delete_url = f"{BASE_URL}/assistants/{agent_id}?api-version=2024-12-01-preview"
            response = requests.delete(delete_url, headers=headers)
            
            if response.status_code in [200, 202, 204]:
                print(f"{agent_id:<40} ✓ Deleted successfully")
                successful_deletions.append(agent_id)
            else:
                print(f"{agent_id:<40} ✗ Failed to delete (Status: {response.status_code})")
                failed_deletions.append((agent_id, response.status_code))
        
        # Print summary
        print(f"\nDeletion Summary:")
        print(f"Successfully deleted {len(successful_deletions)} out of {len(AGENT_IDS)} agents")
        
        if failed_deletions:
            print(f"\nFailed to delete {len(failed_deletions)} agents:")
            for agent_id, status in failed_deletions:
                print(f"- {agent_id} (Status: {status})")
        
        # Reset deployment info files
        for file_name in ["ai_foundry_deployment_info.json", "orchestration_deployment_info.json", "sk_deployment_info.json"]:
            try:
                with open(file_name, "w") as f:
                    json.dump({"deployment_status": "deleted"}, f, indent=2)
                print(f"Updated {file_name} to reflect deletions")
            except Exception as e:
                logger.error(f"Error updating {file_name}: {str(e)}")
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    main()