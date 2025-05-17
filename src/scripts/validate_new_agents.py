#!/usr/bin/env python3
"""
Script to validate newly deployed agents in Azure AI Foundry.
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

def load_deployment_info():
    """Load deployment information from JSON file."""
    try:
        with open('ai_foundry_deployment_info.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading deployment info: {str(e)}")
        return None

def main():
    """Main function to validate newly deployed agents."""
    # Get Azure AD token
    credential = AzureCliCredential()
    token = credential.get_token("https://management.azure.com/.default").token
    
    # Set headers for API requests
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Load deployment info
    deployment_info = load_deployment_info()
    if not deployment_info or deployment_info.get("deployment_status") != "success":
        print("No successful deployment info found. Please deploy agents first.")
        return
    
    # Get agent IDs
    agent_ids = {
        "Chat": deployment_info.get("chat_agent_id"),
        "Weather": deployment_info.get("weather_agent_id"),
        "Calculator": deployment_info.get("calculator_agent_id"),
        "Orchestrator": deployment_info.get("orchestrator_agent_id")
    }
    
    print("\nValidating newly deployed agents in Azure AI Foundry...\n")
    print("Agent Type      Agent ID                            Status         Model")
    print("-" * 80)
    
    success_count = 0
    for agent_type, agent_id in agent_ids.items():
        if not agent_id:
            print(f"{agent_type:15} {'N/A':35} Not deployed")
            continue
        
        # Get agent details
        url = f"{BASE_URL}/assistants/{agent_id}?api-version=2024-12-01-preview"
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                agent_data = response.json()
                name = agent_data.get("name", "Unknown")
                model = agent_data.get("model", "Unknown")
                print(f"{agent_type:15} {agent_id:35} ✓ Exists      {model}")
                success_count += 1
                
                # Try to create a thread (further validation)
                thread_url = f"{BASE_URL}/assistants/{agent_id}/threads?api-version=2024-12-01-preview"
                thread_response = requests.post(thread_url, headers=headers, json={})
                if thread_response.status_code in [200, 201]:
                    thread_id = thread_response.json().get("id")
                    print(f"{' ':15} {' ':35} ✓ Thread created: {thread_id}")
                else:
                    print(f"{' ':15} {' ':35} ✗ Thread creation failed")
            else:
                print(f"{agent_type:15} {agent_id:35} ✗ Not found   (Status: {response.status_code})")
        except Exception as e:
            print(f"{agent_type:15} {agent_id:35} ✗ Error: {str(e)}")
    
    # List all agents
    list_url = f"{BASE_URL}/assistants?api-version=2024-12-01-preview"
    try:
        list_response = requests.get(list_url, headers=headers)
        if list_response.status_code == 200:
            agents_data = list_response.json()
            listed_agents = agents_data.get("value", [])
            listed_count = len(listed_agents)
            
            print(f"\nAPI list endpoint returned: {listed_count} agents")
            
            if listed_agents:
                print("\nAgents from list endpoint:")
                for agent in listed_agents:
                    agent_id = agent.get("id", "Unknown")
                    name = agent.get("name", "Unknown")
                    model = agent.get("model", "Unknown")
                    print(f"  - {agent_id} ({name}) using {model}")
        else:
            print(f"\nFailed to list agents (Status: {list_response.status_code})")
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        print(f"\nError listing agents: {str(e)}")
    
    # Final summary
    print(f"\nValidation Summary: {success_count}/4 agents verified")
    if success_count == 4:
        print("🎉 All agents successfully deployed and validated!")
    else:
        print(f"⚠️ {4 - success_count} agents could not be verified")

if __name__ == "__main__":
    main()