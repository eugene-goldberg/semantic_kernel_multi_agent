#!/usr/bin/env python3
"""
Check available OpenAI resources in Azure.
"""

import os
import sys
from openai import AzureOpenAI
from dotenv import load_dotenv

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from src.config.settings import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_DEPLOYMENT_NAME
)

def main():
    """Main entry point"""
    # Load environment variables
    load_dotenv()
    
    # Check required variables
    if not all([AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY]):
        print("ERROR: Missing required environment variables for Azure OpenAI")
        return
    
    print(f"Azure OpenAI Endpoint: {AZURE_OPENAI_ENDPOINT}")
    print(f"Azure OpenAI Model: {AZURE_OPENAI_DEPLOYMENT_NAME}")
    
    try:
        # Initialize OpenAI client
        client = AzureOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            api_version="2023-07-01-preview"
        )
        
        # Check deployments
        print("\nChecking OpenAI deployments...")
        try:
            deployments = client.deployments.list()
            print(f"Deployments available: {[d.id for d in deployments.data]}")
        except Exception as e:
            print(f"Error listing deployments: {str(e)}")
        
        # Check assistants
        print("\nChecking OpenAI assistants...")
        try:
            assistants = client.beta.assistants.list()
            print(f"Assistants available: {[a.id for a in assistants.data]}")
            
            # Print details of each assistant
            for assistant in assistants.data:
                print(f"\nAssistant: {assistant.id}")
                print(f"  Name: {assistant.name}")
                print(f"  Model: {assistant.model}")
                print(f"  Instructions: {assistant.instructions[:100]}...")
        except Exception as e:
            print(f"Error listing assistants: {str(e)}")
            
        # Test simple chat completion
        print("\nTesting simple chat completion...")
        try:
            response = client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say 'Hello from Azure OpenAI'"}
                ],
                max_tokens=100
            )
            print(f"Chat response: {response.choices[0].message.content}")
        except Exception as e:
            print(f"Error with chat completion: {str(e)}")
        
    except Exception as e:
        print(f"Error connecting to Azure OpenAI: {str(e)}")

if __name__ == "__main__":
    main()