#!/usr/bin/env python3
import asyncio
import os
import sys
import json
import requests
from azure.identity import DefaultAzureCredential

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

async def deploy_agents_rest():
    """
    Deploy agents to Azure AI Agent Service using REST API directly
    """
    try:
        print("Connecting to Azure AI Foundry...")
        
        # Get authentication token
        credential = DefaultAzureCredential()
        token = credential.get_token("https://aiagent.azure.net/.default")
        
        # Construct API URL
        api_url = f"https://{AZURE_AI_PROJECT_HOST}/projects/{AZURE_AI_PROJECT_NAME}/agents"
        
        # Set up headers with authentication
        headers = {
            "Authorization": f"Bearer {token.token}",
            "Content-Type": "application/json"
        }
        
        # Deploy Chat Agent
        print("\nDeploying Chat Agent...")
        chat_agent_payload = {
            "name": "ChatAgent",
            "model": AZURE_OPENAI_DEPLOYMENT_NAME,
            "instructions": (
                "You are a helpful assistant that provides friendly, concise, and accurate information. "
                "You should be conversational but prioritize accuracy and brevity over verbosity. "
                "If you don't know something, admit it clearly rather than making guesses."
            )
        }
        
        chat_response = requests.post(api_url, headers=headers, json=chat_agent_payload)
        
        if chat_response.status_code in (200, 201):
            chat_agent = chat_response.json()
            print(f"Chat Agent created successfully with ID: {chat_agent.get('id')}")
        else:
            print(f"Failed to create Chat Agent: {chat_response.status_code}")
            print(f"Response: {chat_response.text}")
            # Continue anyway to try the weather agent
            chat_agent = {"id": "failed"}
        
        # Deploy Weather Agent
        print("\nDeploying Weather Agent...")
        weather_agent_payload = {
            "name": "WeatherAgent",
            "model": AZURE_OPENAI_DEPLOYMENT_NAME,
            "instructions": (
                "You are a weather specialist agent that provides accurate and helpful weather information "
                "for locations in the United States. "
                "You have access to real-time US weather data through the National Weather Service API. "
                "When asked about weather, use the coordinates of the city to get accurate data. "
                "For example, Seattle is at 47.6062, -122.3321. New York is at 40.7128, -74.0060. "
                "Provide your answers in a friendly, concise manner, focusing on the most relevant information. "
                "If asked about weather outside the United States, politely explain that your weather data "
                "is currently limited to US locations only."
            )
        }
        
        weather_response = requests.post(api_url, headers=headers, json=weather_agent_payload)
        
        if weather_response.status_code in (200, 201):
            weather_agent = weather_response.json()
            print(f"Weather Agent created successfully with ID: {weather_agent.get('id')}")
        else:
            print(f"Failed to create Weather Agent: {weather_response.status_code}")
            print(f"Response: {weather_response.text}")
            weather_agent = {"id": "failed"}
        
        # Save deployment info
        deployment_info = {
            "chat_agent_id": chat_agent.get("id"),
            "weather_agent_id": weather_agent.get("id")
        }
        
        with open("deployment_info.json", "w") as f:
            json.dump(deployment_info, f, indent=2)
        
        print("\nDeployment info saved to deployment_info.json")
        
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

# Try another approach with Microsoft Graph API
async def deploy_with_management_api():
    """
    Deploy agents using the Azure Management API
    """
    try:
        print("Attempting deployment using Azure Management API...")
        
        # Get authentication token for management API
        credential = DefaultAzureCredential()
        token = credential.get_token("https://management.azure.com/.default")
        
        # Construct API URL for AI Project
        project_url = (
            f"https://management.azure.com/subscriptions/{AZURE_SUBSCRIPTION_ID}"
            f"/resourceGroups/{AZURE_RESOURCE_GROUP}"
            f"/providers/Microsoft.MachineLearningServices/workspaces/{AZURE_AI_PROJECT_NAME}"
            f"?api-version=2024-01-01-preview"
        )
        
        # Set up headers with authentication
        headers = {
            "Authorization": f"Bearer {token.token}",
            "Content-Type": "application/json"
        }
        
        # First, get project information
        project_response = requests.get(project_url, headers=headers)
        
        if project_response.status_code == 200:
            project_info = project_response.json()
            print(f"Successfully connected to project: {project_info.get('name')}")
            
            # Now try to create agents
            agents_url = (
                f"https://management.azure.com/subscriptions/{AZURE_SUBSCRIPTION_ID}"
                f"/resourceGroups/{AZURE_RESOURCE_GROUP}"
                f"/providers/Microsoft.MachineLearningServices/workspaces/{AZURE_AI_PROJECT_NAME}"
                f"/agents?api-version=2024-02-01-preview"
            )
            
            # Deploy Chat Agent
            print("\nDeploying Chat Agent via Management API...")
            chat_agent_payload = {
                "properties": {
                    "agentType": "ChatCompletion",
                    "displayName": "ChatAgent",
                    "description": "General chat agent",
                    "model": {
                        "deploymentName": AZURE_OPENAI_DEPLOYMENT_NAME,
                        "instructions": (
                            "You are a helpful assistant that provides friendly, concise, and accurate information. "
                            "You should be conversational but prioritize accuracy and brevity over verbosity. "
                            "If you don't know something, admit it clearly rather than making guesses."
                        )
                    }
                }
            }
            
            chat_response = requests.put(
                f"{agents_url}/ChatAgent",
                headers=headers, 
                json=chat_agent_payload
            )
            
            if chat_response.status_code in (200, 201):
                chat_agent = chat_response.json()
                print(f"Chat Agent created successfully with ID: {chat_agent.get('id')}")
            else:
                print(f"Failed to create Chat Agent: {chat_response.status_code}")
                print(f"Response: {chat_response.text}")
        else:
            print(f"Failed to connect to project: {project_response.status_code}")
            print(f"Response: {project_response.text}")
            
    except Exception as e:
        print(f"Error during deployment: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Try both approaches
    asyncio.run(deploy_agents_rest())
    print("\n" + "="*50 + "\n")
    asyncio.run(deploy_with_management_api())