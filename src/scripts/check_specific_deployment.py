#!/usr/bin/env python3
"""
Script to check specific agent IDs directly from Azure AI Foundry.
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
    """Check specific agent IDs directly."""
    try:
        # Get access token
        token = get_access_token()
        
        # Set up HTTP headers
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Load deployment info
        with open("ai_foundry_deployment_info.json", "r") as f:
            deployment_info = json.load(f)
        
        # Check each agent ID directly
        agent_keys = ["chat_agent_id", "weather_agent_id", "calculator_agent_id", "orchestrator_agent_id"]
        total_found = 0
        
        print("\nChecking deployed agents directly:")
        print(f"{'Agent Type':<15} {'Agent ID':<40} {'Status':<10} {'Name':<20} {'Model'}")
        print("-" * 100)
        
        for key in agent_keys:
            agent_type = key.replace("_agent_id", "").capitalize()
            agent_id = deployment_info.get(key)
            
            if not agent_id:
                print(f"{agent_type:<15} {'Not found in deployment info':<40}")
                continue
            
            check_url = f"{BASE_URL}/assistants/{agent_id}?api-version=2024-12-01-preview"
            response = requests.get(check_url, headers=headers)
            
            if response.status_code == 200:
                agent_data = response.json()
                name = agent_data.get("name", "Unknown")
                model = agent_data.get("model", "Unknown")
                print(f"{agent_type:<15} {agent_id:<40} {'✓ Exists':<10} {name:<20} {model}")
                total_found += 1
            else:
                print(f"{agent_type:<15} {agent_id:<40} {'✗ Not found':<10} (Status: {response.status_code})")
        
        print(f"\nTotal agents found: {total_found} out of {len(agent_keys)}")
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    main()