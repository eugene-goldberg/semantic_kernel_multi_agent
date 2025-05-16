#!/usr/bin/env python3
import asyncio
import os
import sys
import requests

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from azure.identity import DefaultAzureCredential
from src.config.settings import (
    AZURE_AI_PROJECT_NAME, 
    AZURE_RESOURCE_GROUP, 
    AZURE_SUBSCRIPTION_ID,
    AZURE_AI_PROJECT_HOST,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_DEPLOYMENT_NAME
)

def test_openai_connectivity():
    """Test connectivity to Azure OpenAI service"""
    print(f"\nTesting Azure OpenAI connectivity...")
    print(f"Endpoint: {AZURE_OPENAI_ENDPOINT}")
    
    # Test simple completion API call
    url = f"{AZURE_OPENAI_ENDPOINT}openai/deployments/{AZURE_OPENAI_DEPLOYMENT_NAME}/chat/completions?api-version=2024-02-15-preview"
    
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_OPENAI_API_KEY
    }
    
    data = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello!"}
        ],
        "max_tokens": 50
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            message = result["choices"][0]["message"]["content"].strip()
            print(f"OpenAI API test successful!")
            print(f"Response: {message}")
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

def test_foundry_connectivity():
    """Test connection to Azure AI Foundry"""
    print(f"\nTesting Azure AI Foundry connectivity...")
    endpoint = f"https://{AZURE_AI_PROJECT_HOST}"
    print(f"Endpoint: {endpoint}")
    print(f"Project: {AZURE_AI_PROJECT_NAME}")
    
    credential = DefaultAzureCredential()
    token = credential.get_token("https://management.azure.com/.default")
    
    # Test API call to list workspaces
    url = f"https://management.azure.com/subscriptions/{AZURE_SUBSCRIPTION_ID}/resourceGroups/{AZURE_RESOURCE_GROUP}/providers/Microsoft.MachineLearningServices/workspaces/{AZURE_AI_PROJECT_NAME}?api-version=2024-01-01-preview"
    
    headers = {
        "Authorization": f"Bearer {token.token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            print("Azure AI Foundry API test successful!")
            print(f"Project details retrieved successfully")
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_openai_connectivity()
    test_foundry_connectivity()