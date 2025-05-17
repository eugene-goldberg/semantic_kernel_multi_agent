#!/usr/bin/env python3
"""
Script to verify all agents have been deleted from Azure AI Foundry.
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

# All previously known agent IDs
ALL_AGENT_IDS = [
    # Original 4 agents
    "asst_Axv9jCk8UKN6051pmq9r0gbc",  # CalculatorAgent
    "asst_TyyCFXEVVUJDzRbCcPCJWKGU",  # ChatAgent
    "asst_MKdlnsH8FXBvIePFYWmAzH4t",  # OrchestratorAgent
    "asst_Z55aX9qGZFWfeKVqk0Ng6GQL",  # WeatherAgent
    
    # 3 additional agents
    "asst_IoApfRbXaU3TjoUYDsiPkHNN",  # Agent608
    "asst_OqHBKHPpwRNhGWksATgMUrD1",  # WeatherAgent
    "asst_JkErsk8DfToMZ4HsueeqE9EP",  # ChatAgent
    
    # Last agent
    "asst_UcTrscbN86GsfTwFVcAL7IvB",  # Agent857
]

def main():
    """Main function to verify all agents have been deleted."""
    # Get Azure AD token
    credential = AzureCliCredential()
    token = credential.get_token("https://management.azure.com/.default").token
    
    # Set headers for API requests
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\nVerifying all agents have been deleted from Azure AI Foundry...")
    
    # Check each known agent ID
    found_agents = []
    for agent_id in ALL_AGENT_IDS:
        url = f"{BASE_URL}/assistants/{agent_id}?api-version=2024-12-01-preview"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            found_agents.append(agent_id)
    
    # Try to list all agents
    list_url = f"{BASE_URL}/assistants?api-version=2024-12-01-preview"
    list_response = requests.get(list_url, headers=headers)
    
    if list_response.status_code == 200:
        agents_data = list_response.json()
        listed_agents = agents_data.get("value", [])
        listed_count = len(listed_agents)
    else:
        listed_count = "Error getting list"
        listed_agents = []
    
    # Print results
    print("\n=== VERIFICATION RESULTS ===")
    
    if found_agents:
        print(f"\n❌ Found {len(found_agents)} agents still existing:")
        for agent_id in found_agents:
            print(f"  - {agent_id}")
    else:
        print(f"\n✅ All known agents have been deleted")
    
    print(f"\nAPI list endpoint returned: {listed_count} agents")
    
    if listed_agents:
        print("\nAgents from list endpoint:")
        for agent in listed_agents:
            agent_id = agent.get("id", "Unknown")
            name = agent.get("name", "Unknown")
            print(f"  - {agent_id} ({name})")
    
    # Final conclusion
    if not found_agents and (listed_count == 0 or listed_count == "Error getting list"):
        print("\n🎉 VERIFICATION SUCCESSFUL: No agents found in Azure AI Foundry")
    else:
        print("\n⚠️ VERIFICATION INCOMPLETE: Some agents may still exist")

if __name__ == "__main__":
    main()