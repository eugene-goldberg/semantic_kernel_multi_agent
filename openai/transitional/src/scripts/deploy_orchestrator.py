#!/usr/bin/env python3
"""
Deploy the orchestrator agent to Azure AI Agent Service using a service principal

This script is designed to work with the multi-agent orchestration capability,
deploying an orchestrator agent that can delegate to other specialized agents.
"""

import asyncio
import os
import sys
import json
import requests
from azure.identity import ClientSecretCredential

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from src.config.settings import (
    AZURE_OPENAI_DEPLOYMENT_NAME,
    AZURE_AI_PROJECT_NAME, 
    AZURE_RESOURCE_GROUP, 
    AZURE_SUBSCRIPTION_ID,
    AZURE_AI_PROJECT_HOST
)

# Service Principal Authentication
AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")

async def deploy_orchestrator_agent():
    """
    Deploy the orchestrator agent to Azure AI Agent Service
    """
    if not all([AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID]):
        print("ERROR: Service Principal credentials are missing.")
        print("Please set the following environment variables:")
        print("  - AZURE_CLIENT_ID")
        print("  - AZURE_CLIENT_SECRET")
        print("  - AZURE_TENANT_ID")
        return

    try:
        print("Authenticating with Service Principal...")
        
        # Create credential object
        credential = ClientSecretCredential(
            tenant_id=AZURE_TENANT_ID,
            client_id=AZURE_CLIENT_ID,
            client_secret=AZURE_CLIENT_SECRET
        )
        
        # Get token for AI Agent service
        access_token = credential.get_token("https://management.azure.com/.default").token
        
        # Determine the API URL
        api_url = f"https://{AZURE_AI_PROJECT_HOST}/projects/{AZURE_AI_PROJECT_NAME}/agents"
        
        # Set up headers with authentication
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # First, try to load existing deployment info to get agent IDs
        try:
            with open("deployment_info.json", "r") as f:
                deployment_info = json.load(f)
            
            chat_agent_id = deployment_info.get("chat_agent_id")
            weather_agent_id = deployment_info.get("weather_agent_id")
            
            print(f"Found existing agent deployments:")
            print(f"  - Chat Agent ID: {chat_agent_id}")
            print(f"  - Weather Agent ID: {weather_agent_id}")
            
        except (FileNotFoundError, json.JSONDecodeError):
            print("No existing deployment info found. Please deploy chat and weather agents first.")
            print("You can use deploy_agents.py or deploy_with_service_principal.py to deploy them.")
            chat_agent_id = None
            weather_agent_id = None
            
        # Only proceed if we have the required agent IDs
        if not chat_agent_id or not weather_agent_id:
            print("ERROR: Missing agent IDs. Cannot deploy orchestrator without chat and weather agents.")
            return
        
        # Deploy Orchestrator Agent
        print("\nDeploying Orchestrator Agent...")
        orchestrator_agent_payload = {
            "name": "OrchestratorAgent",
            "model": AZURE_OPENAI_DEPLOYMENT_NAME,
            "instructions": (
                "You are an orchestrator agent responsible for routing user requests to the appropriate "
                "specialized agent. You have access to two specialized agents:\n\n"
                "1. Chat Agent (ID: " + chat_agent_id + ") - Handles general conversation and questions\n"
                "2. Weather Agent (ID: " + weather_agent_id + ") - Provides weather information\n\n"
                "For weather-related questions (about temperature, forecast, rain, etc.), delegate to the Weather Agent. "
                "For all other questions and conversations, delegate to the Chat Agent.\n\n"
                "Always analyze the user's question carefully to determine which agent would be best suited to answer it. "
                "When delegating, provide the full user query to the specialized agent."
            ),
            "plugins": [
                {
                    "name": "DelegateToAgent",
                    "manifest": {
                        "namespace": "agent.delegate",
                        "functions": [
                            {
                                "name": "delegateToAgent",
                                "description": "Delegates a user query to a specialized agent",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "agentId": {
                                            "type": "string",
                                            "description": "The ID of the agent to delegate to"
                                        },
                                        "query": {
                                            "type": "string",
                                            "description": "The user query to send to the specialized agent"
                                        }
                                    },
                                    "required": ["agentId", "query"]
                                }
                            }
                        ]
                    }
                }
            ]
        }
        
        orchestrator_response = requests.post(api_url, headers=headers, json=orchestrator_agent_payload)
        
        if orchestrator_response.status_code in (200, 201):
            orchestrator_agent = orchestrator_response.json()
            print(f"Orchestrator Agent created successfully with ID: {orchestrator_agent.get('id')}")
            
            # Update deployment info
            deployment_info["orchestrator_agent_id"] = orchestrator_agent.get("id")
            
            with open("deployment_info.json", "w") as f:
                json.dump(deployment_info, f, indent=2)
            
            print("\nDeployment info updated in deployment_info.json")
            
        else:
            print(f"Failed to create Orchestrator Agent: {orchestrator_response.status_code}")
            print(f"Response: {orchestrator_response.text}")
            
        # List all agents to verify
        print("\nListing all agents to verify deployment...")
        
        list_response = requests.get(api_url, headers=headers)
        
        if list_response.status_code == 200:
            agents = list_response.json()
            print(f"Found {len(agents)} agent(s):")
            for agent in agents:
                print(f"  - {agent.get('name')} (ID: {agent.get('id')})")
        else:
            print(f"Failed to list agents: {list_response.status_code}")
            print(f"Response: {list_response.text}")
            
    except Exception as e:
        print(f"Error during deployment: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(deploy_orchestrator_agent())