#!/usr/bin/env python3
"""
Script to list all agents directly from Azure AI Foundry API.
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
    """List all agents directly from the API."""
    try:
        # Get access token
        token = get_access_token()
        
        # Set up HTTP headers
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # List all agents directly
        url = f"{BASE_URL}/assistants?api-version=2024-12-01-preview"
        
        print(f"Requesting agents from: {url}")
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"Failed to list agents: {response.status_code}")
            print(response.text)
            return
        
        agents_data = response.json()
        agents = agents_data.get("value", [])
        
        print(f"\nFound {len(agents)} assistants in Azure AI Foundry:\n")
        
        if not agents:
            print("No assistants found.")
            return
        
        # Print all agents
        print(f"{'ID':<40} {'Name':<30} {'Model':<15} {'Created'}")
        print("-" * 90)
        
        for agent in agents:
            agent_id = agent.get("id", "Unknown")
            name = agent.get("name", "Unknown")
            model = agent.get("model", "Unknown")
            created_time = agent.get("createdOn", "Unknown")
            
            print(f"{agent_id:<40} {name:<30} {model:<15} {created_time}")
        
        # Now check all the expected agent IDs directly
        print("\nChecking specific agent IDs directly:")
        
        with open("ai_foundry_deployment_info.json", "r") as f:
            deployment_info = json.load(f)
        
        agent_ids = {
            "Chat": deployment_info.get("chat_agent_id"),
            "Weather": deployment_info.get("weather_agent_id"),
            "Calculator": deployment_info.get("calculator_agent_id"),
            "Orchestrator": deployment_info.get("orchestrator_agent_id")
        }
        
        for agent_type, agent_id in agent_ids.items():
            check_url = f"{BASE_URL}/assistants/{agent_id}?api-version=2024-12-01-preview"
            check_response = requests.get(check_url, headers=headers)
            
            status = "✓ Exists" if check_response.status_code == 200 else f"✗ Not found (Status: {check_response.status_code})"
            print(f"{agent_type:<15} {agent_id:<40} {status}")
            
            if check_response.status_code == 200:
                agent_data = check_response.json()
                print(f"{'':15} Name: {agent_data.get('name', 'Unknown')}")
                print(f"{'':15} Model: {agent_data.get('model', 'Unknown')}")
                print(f"{'':15} Created: {agent_data.get('createdOn', 'Unknown')}")
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    main()