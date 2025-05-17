#!/usr/bin/env python3
"""
Direct Azure REST API deployment script for agents.
This script bypasses the SDK authentication issues by using Azure CLI auth tokens directly.
"""

import os
import sys
import json
import subprocess
import requests
import time

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

def get_access_token():
    """Get access token from Azure CLI"""
    print("Getting access token from Azure CLI...")
    
    # First ensure the user is logged in
    login_check = subprocess.run(
        ["az", "account", "show"],
        capture_output=True,
        text=True
    )
    
    if login_check.returncode != 0:
        print("You need to login to Azure CLI first.")
        subprocess.run(["az", "login"], check=True)
    
    # Get the token for ARM
    token_process = subprocess.run(
        ["az", "account", "get-access-token", "--resource", "https://management.azure.com"],
        capture_output=True,
        text=True,
        check=True
    )
    
    token_data = json.loads(token_process.stdout)
    return token_data["accessToken"]

def list_available_agents(token):
    """List all available agents in Azure OpenAI service"""
    
    # Get deployed models in Azure OpenAI
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    ai_resources_url = (
        f"https://management.azure.com/subscriptions/{AZURE_SUBSCRIPTION_ID}"
        f"/resourceGroups/{AZURE_RESOURCE_GROUP}"
        f"/providers"
        f"?api-version=2021-04-01"
    )
    
    print(f"Checking available Azure resources in resource group {AZURE_RESOURCE_GROUP}...")
    response = requests.get(ai_resources_url, headers=headers)
    
    if response.status_code == 200:
        resources = response.json()
        print(f"Found {len(resources.get('value', []))} resources:")
        for resource in resources.get("value", []):
            print(f"  - {resource.get('name')} (Type: {resource.get('type')})")
    else:
        print(f"Failed to list resources: {response.status_code}")
        print(f"Response: {response.text}")

def deploy_agents():
    """Deploy agents using direct Azure REST API calls"""
    try:
        # Get access token from Azure CLI
        token = get_access_token()
        
        # List available resources to help diagnose issues
        list_available_agents(token)
        
        # Find the endpoint for deploying agents
        print("\nExploring Azure OpenAI deployments to find the right endpoint...")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Try to find the OpenAI account using latest API version
        openai_accounts_url = (
            f"https://management.azure.com/subscriptions/{AZURE_SUBSCRIPTION_ID}"
            f"/resourceGroups/{AZURE_RESOURCE_GROUP}"
            f"/providers/Microsoft.CognitiveServices"
            f"/accounts?api-version=2023-05-01"
        )
        
        response = requests.get(openai_accounts_url, headers=headers)
        
        if response.status_code == 200:
            accounts = response.json()
            openai_account = None
            
            for account in accounts.get("value", []):
                if account.get("kind") == "OpenAI" or "openai" in account.get("name", "").lower():
                    openai_account = account
                    print(f"Found OpenAI account: {account.get('name')}")
                    break
            
            if not openai_account:
                print("No OpenAI account found in the resource group.")
                return
                
            # Now get the deployments in this account
            account_name = openai_account.get("name")
            deployments_url = (
                f"https://management.azure.com/subscriptions/{AZURE_SUBSCRIPTION_ID}"
                f"/resourceGroups/{AZURE_RESOURCE_GROUP}"
                f"/providers/Microsoft.CognitiveServices"
                f"/accounts/{account_name}"
                f"/deployments?api-version=2023-05-01"
            )
            
            deployments_response = requests.get(deployments_url, headers=headers)
            
            if deployments_response.status_code == 200:
                deployments = deployments_response.json()
                print(f"Found {len(deployments.get('value', []))} deployments:")
                for deployment in deployments.get("value", []):
                    print(f"  - {deployment.get('name')} (Model: {deployment.get('properties', {}).get('model', {}).get('name')})")
            else:
                print(f"Failed to list deployments: {deployments_response.status_code}")
                print(f"Response: {deployments_response.text}")
        else:
            print(f"Failed to list OpenAI accounts: {response.status_code}")
            print(f"Response: {response.text}")
                
        # Try to find AI Hub/Project info
        print("\nExploring Azure AI resources...")
        
        ai_resources_url = (
            f"https://management.azure.com/subscriptions/{AZURE_SUBSCRIPTION_ID}"
            f"/resourceGroups/{AZURE_RESOURCE_GROUP}"
            f"/providers/Microsoft.MachineLearningServices"
            f"/workspaces?api-version=2023-10-01"
        )
        
        response = requests.get(ai_resources_url, headers=headers)
        
        if response.status_code == 200:
            workspaces = response.json()
            print(f"Found {len(workspaces.get('value', []))} AI workspaces:")
            for workspace in workspaces.get("value", []):
                print(f"  - {workspace.get('name')} (Location: {workspace.get('location')})")
                
                # Try to get projects in this workspace
                workspace_name = workspace.get("name")
                projects_url = (
                    f"https://management.azure.com/subscriptions/{AZURE_SUBSCRIPTION_ID}"
                    f"/resourceGroups/{AZURE_RESOURCE_GROUP}"
                    f"/providers/Microsoft.MachineLearningServices"
                    f"/workspaces/{workspace_name}"
                    f"/connections?api-version=2023-10-01"
                )
                
                projects_response = requests.get(projects_url, headers=headers)
                
                if projects_response.status_code == 200:
                    connections = projects_response.json()
                    print(f"    Found {len(connections.get('value', []))} connections:")
                    for connection in connections.get("value", []):
                        print(f"      - {connection.get('name')} (Type: {connection.get('properties', {}).get('category')})")
                else:
                    print(f"    Failed to list projects: {projects_response.status_code}")
                    print(f"    Response: {projects_response.text}")
        else:
            print(f"Failed to list AI workspaces: {response.status_code}")
            print(f"Response: {response.text}")
            
        # At this point, we have explored the account structure but haven't created agents yet
        # We need more information about the specific Azure AI Agent APIs available
            
        print("\nBased on the exploration, we need the following information to proceed:")
        print(f"1. Confirm AZURE_AI_PROJECT_NAME: {AZURE_AI_PROJECT_NAME}")
        print(f"2. Confirm AZURE_AI_PROJECT_HOST: {AZURE_AI_PROJECT_HOST}")
        print(f"3. Confirm AZURE_OPENAI_DEPLOYMENT_NAME: {AZURE_OPENAI_DEPLOYMENT_NAME}")
        print(f"4. Confirm AZURE_RESOURCE_GROUP: {AZURE_RESOURCE_GROUP}")
        print("\nPlease verify if these values match your Azure resources.")
        print("If they do not match, please update your .env file and try again.")
        
        print("\nTo proceed with agent deployment, please use the Azure Portal to create the agents manually.")
        print("Go to the Azure AI Studio (https://ai.azure.com) and create the following agents:")
        print("1. Chat Agent - A general purpose assistant")
        print("2. Weather Agent - A specialized agent for US weather information")
        
        print("\nAfter creating the agents, you can use the interactive client with:")
        print("python src/scripts/interact_deployed_agents.py")
            
    except Exception as e:
        print(f"Error during deployment exploration: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    deploy_agents()