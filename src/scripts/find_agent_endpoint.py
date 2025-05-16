#!/usr/bin/env python3
"""
Find the correct endpoint for the Azure AI Agent Service.
"""

import os
import sys
import requests
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from dotenv import load_dotenv

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from src.config.settings import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_AI_PROJECT_NAME, 
    AZURE_RESOURCE_GROUP, 
    AZURE_SUBSCRIPTION_ID,
    AZURE_AI_PROJECT_HOST
)

def get_credential():
    """Get the best available credential"""
    # Try service principal first
    if all([
        os.getenv("AZURE_CLIENT_ID"),
        os.getenv("AZURE_CLIENT_SECRET"),
        os.getenv("AZURE_TENANT_ID")
    ]):
        print("Using Service Principal authentication...")
        return ClientSecretCredential(
            tenant_id=os.getenv("AZURE_TENANT_ID"),
            client_id=os.getenv("AZURE_CLIENT_ID"),
            client_secret=os.getenv("AZURE_CLIENT_SECRET")
        )
    else:
        print("Using Default Azure authentication...")
        return DefaultAzureCredential()

def try_endpoint(endpoint, credential, description):
    """Try to access an endpoint with the given credential"""
    print(f"\n--- Trying {description}: {endpoint} ---")
    
    try:
        # Get token
        token = credential.get_token("https://management.azure.com/.default")
        
        # Set up headers with authentication
        headers = {
            "Authorization": f"Bearer {token.token}",
            "Content-Type": "application/json"
        }
        
        # Make request
        response = requests.get(endpoint, headers=headers)
        
        # Process response
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print(f"SUCCESS! This endpoint works: {endpoint}")
            print(f"Response: {response.text[:100]}...")
            return True
        else:
            print(f"Failed. Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def find_agent_endpoint():
    """Find the correct endpoint for the Azure AI Agent Service"""
    # Load environment variables
    load_dotenv()
    
    print("Finding the correct endpoint for Azure AI Agent Service...")
    print(f"Current configuration:")
    print(f"  AZURE_AI_PROJECT_HOST: {AZURE_AI_PROJECT_HOST}")
    print(f"  AZURE_AI_PROJECT_NAME: {AZURE_AI_PROJECT_NAME}")
    print(f"  AZURE_OPENAI_ENDPOINT: {AZURE_OPENAI_ENDPOINT}")
    
    # Get credential
    credential = get_credential()
    
    # Try different endpoint patterns
    endpoint_patterns = [
        # Basic patterns with host only
        (f"https://{AZURE_AI_PROJECT_HOST}/", "Basic host"),
        (f"https://{AZURE_AI_PROJECT_HOST}/agents", "Agents API"),
        
        # Project-based patterns
        (f"https://{AZURE_AI_PROJECT_HOST}/api/projects/{AZURE_AI_PROJECT_NAME}", "Project API"),
        (f"https://{AZURE_AI_PROJECT_HOST}/projects/{AZURE_AI_PROJECT_NAME}", "Project root"),
        (f"https://{AZURE_AI_PROJECT_HOST}/projects/{AZURE_AI_PROJECT_NAME}/agents", "Project agents"),
        
        # Azure OpenAI connection patterns  
        (f"{AZURE_OPENAI_ENDPOINT}", "Azure OpenAI endpoint"),
        (f"{AZURE_OPENAI_ENDPOINT}/openai/agents", "OpenAI agents"),
        
        # Azure AI Services patterns
        (f"https://eastus.api.cognitive.microsoft.com/openai/agents", "East US Cognitive API"),
        (f"https://eastus.api.aiagent.azure.net", "East US Agent API"),
        
        # Management API patterns
        (f"https://management.azure.com/subscriptions/{AZURE_SUBSCRIPTION_ID}/resourceGroups/{AZURE_RESOURCE_GROUP}/providers/Microsoft.MachineLearningServices/workspaces/{AZURE_AI_PROJECT_NAME}?api-version=2023-10-01", "Management API")
    ]
    
    # Try each endpoint
    success = False
    for endpoint, description in endpoint_patterns:
        if try_endpoint(endpoint, credential, description):
            success = True
            print(f"\n✅ Found working endpoint: {endpoint}")
            print(f"To use this endpoint, run:")
            print(f"python3 src/scripts/deploy_agents_sdk.py --endpoint \"{endpoint}\"")
    
    if not success:
        print("\n❌ Could not find a working endpoint.")
        print("Please verify your configuration and Azure resources.")
        print("Consider checking the Azure Portal for the correct endpoint.")

if __name__ == "__main__":
    find_agent_endpoint()