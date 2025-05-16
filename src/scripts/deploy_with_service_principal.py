#!/usr/bin/env python3
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

# Service Principal Authentication - to be set in environment variables
AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")

async def deploy_agents_with_service_principal():
    """
    Deploy agents to Azure AI Agent Service using a Service Principal for authentication
    """
    if not all([AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID]):
        print("ERROR: Service Principal credentials are missing.")
        print("Please set the following environment variables:")
        print("  - AZURE_CLIENT_ID")
        print("  - AZURE_CLIENT_SECRET")
        print("  - AZURE_TENANT_ID")
        print("\nYou can create a service principal with:")
        print("az ad sp create-for-rbac --name \"MultiAgentApp\" --role contributor --scopes /subscriptions/{AZURE_SUBSCRIPTION_ID}")
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
        # Try multiple scopes as the API might require different scopes
        possible_scopes = [
            "https://management.azure.com/.default",  # Azure Management API
            "https://api.aiagent.azure.net/.default",  # Try another endpoint
            "https://aiagent.azure.net/.default"  # Original endpoint
        ]
        
        access_token = None
        for scope in possible_scopes:
            try:
                print(f"Trying to authenticate with scope: {scope}")
                access_token = credential.get_token(scope).token
                print(f"Successfully authenticated with scope: {scope}")
                break
            except Exception as e:
                print(f"Authentication failed with scope {scope}: {str(e)}")
                
        if not access_token:
            raise Exception("Failed to authenticate with any scope. Please check your credentials and tenant.")
        
        # Try to determine the correct API URL format
        # Option 1: Standard AI Agent Service URL format
        api_url_1 = f"https://{AZURE_AI_PROJECT_HOST}/projects/{AZURE_AI_PROJECT_NAME}/agents"
        
        # Option 2: Management API format (could be different based on API version)
        api_url_2 = f"https://management.azure.com/subscriptions/{AZURE_SUBSCRIPTION_ID}/resourceGroups/{AZURE_RESOURCE_GROUP}/providers/Microsoft.MachineLearningServices/workspaces/{AZURE_AI_PROJECT_NAME}/agents?api-version=2024-02-01-preview"
        
        # Start with the first option
        api_url = api_url_1
        
        # Set up headers with authentication
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Try to access the project using different API URLs
        print(f"Testing connection to project: {AZURE_AI_PROJECT_NAME}...")
        
        # Try the first URL format
        print(f"Trying URL: https://{AZURE_AI_PROJECT_HOST}/projects/{AZURE_AI_PROJECT_NAME}")
        test_response_1 = requests.get(f"https://{AZURE_AI_PROJECT_HOST}/projects/{AZURE_AI_PROJECT_NAME}", headers=headers)
        
        if test_response_1.status_code == 200:
            print("Successfully connected to project using direct API!")
            api_url = api_url_1
        else:
            print(f"Direct API connection failed. Status: {test_response_1.status_code}")
            print(f"Response: {test_response_1.text}")
            
            # Try the management API format
            management_url = f"https://management.azure.com/subscriptions/{AZURE_SUBSCRIPTION_ID}/resourceGroups/{AZURE_RESOURCE_GROUP}/providers/Microsoft.MachineLearningServices/workspaces/{AZURE_AI_PROJECT_NAME}?api-version=2024-02-01-preview"
            print(f"Trying Management API URL: {management_url}")
            test_response_2 = requests.get(management_url, headers=headers)
            
            if test_response_2.status_code == 200:
                print("Successfully connected to project using Management API!")
                api_url = api_url_2
            else:
                print(f"Management API connection failed. Status: {test_response_2.status_code}")
                print(f"Response: {test_response_2.text}")
                print("\nPossible reasons:")
                print("1. Service Principal doesn't have access to the AI Agent service")
                print("2. Project name or host is incorrect")
                print("3. Token scope might be incorrect")
                
                # Try Azure CLI login as a last resort
                print("\nAttempting to use Azure CLI for deployment...")
                try:
                    import subprocess
                    subprocess.run(["az", "login", "--scope", "https://aiagent.azure.net/.default"], check=True)
                    print("Azure CLI login successful. Proceeding with deployment...")
                except Exception as e:
                    print(f"Azure CLI login failed: {str(e)}")
                    print("Please login manually with: az login --scope https://aiagent.azure.net/.default")
                    return
        
        print("Successfully connected to project!")
        
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
            "weather_agent_id": weather_agent.get("id"),
            "project_host": AZURE_AI_PROJECT_HOST,
            "project_name": AZURE_AI_PROJECT_NAME
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

if __name__ == "__main__":
    asyncio.run(deploy_agents_with_service_principal())