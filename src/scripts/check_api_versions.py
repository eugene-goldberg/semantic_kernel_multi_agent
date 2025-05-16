#!/usr/bin/env python3
"""
Check which Azure OpenAI API version supports the assistants API.
"""

import os
import sys
from openai import AzureOpenAI, OpenAI
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

def try_api_version(version):
    """Try a specific API version"""
    print(f"\nTrying API version: {version}")
    
    try:
        # Initialize OpenAI client
        client = AzureOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            api_version=version
        )
        
        # Try a simple chat completion
        try:
            print("Testing chat completions...")
            response = client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say 'Hello from API version " + version + "'"}
                ],
                max_tokens=30
            )
            print(f"Chat completions successful: {response.choices[0].message.content}")
        except Exception as e:
            print(f"Error with chat completions: {str(e)}")
        
        # Try to access assistants API
        try:
            print("Testing assistants API...")
            assistants = client.beta.assistants.list(limit=10)
            print(f"Assistants API successful! Found {len(assistants.data)} assistants.")
            return True
        except Exception as e:
            print(f"Error with assistants API: {str(e)}")
            return False
            
    except Exception as e:
        print(f"Error initializing client: {str(e)}")
        return False

def try_openai_client():
    """Try using the standard OpenAI client"""
    print("\nTrying standard OpenAI client (non-Azure)...")
    
    # Check if OPENAI_API_KEY is set
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("OPENAI_API_KEY environment variable not set. Skipping this test.")
        return
    
    try:
        # Initialize standard OpenAI client
        client = OpenAI(
            api_key=openai_api_key
        )
        
        # Try assistants API
        try:
            print("Testing assistants API with standard OpenAI client...")
            assistants = client.beta.assistants.list(limit=10)
            print(f"Assistants API successful! Found {len(assistants.data)} assistants.")
        except Exception as e:
            print(f"Error with assistants API: {str(e)}")
            
    except Exception as e:
        print(f"Error initializing standard OpenAI client: {str(e)}")

def main():
    """Main function"""
    # Load environment variables
    load_dotenv()
    
    # Check required variables
    if not all([AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT_NAME]):
        print("ERROR: Missing required environment variables for Azure OpenAI")
        return
    
    print(f"Checking API versions for Azure OpenAI endpoint: {AZURE_OPENAI_ENDPOINT}")
    print(f"Using deployment: {AZURE_OPENAI_DEPLOYMENT_NAME}")
    
    # Try different API versions
    versions = [
        "2023-07-01-preview",
        "2023-09-15-preview",
        "2023-10-01-preview",
        "2023-12-01-preview",
        "2024-02-01-preview",
        "2024-03-01-preview",
        "2024-04-01-preview",
        "2024-05-01-preview"
    ]
    
    success = False
    for version in versions:
        if try_api_version(version):
            print(f"\n✅ API version {version} supports the assistants API!")
            success = True
        else:
            print(f"\n❌ API version {version} does not support the assistants API.")
    
    if not success:
        print("\nNone of the tested API versions support the assistants API. Trying standard OpenAI client...")
        try_openai_client()
        
        print("\nRecommendations:")
        print("1. Check Azure OpenAI documentation for the latest API version that supports assistants")
        print("2. Verify that your Azure OpenAI resource has assistants API enabled")
        print("3. Consider using the chat completions API directly with function calling instead")

if __name__ == "__main__":
    main()