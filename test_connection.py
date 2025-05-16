#!/usr/bin/env python3
import os
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env.deploy")

# Get environment variables
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

print(f"Azure OpenAI Endpoint: {azure_endpoint}")
print(f"API Key: {api_key[:5]}...")
print(f"Deployment Name: {deployment_name}")

try:
    # Initialize OpenAI client
    client = AzureOpenAI(
        azure_endpoint=azure_endpoint,
        api_key=api_key,
        api_version="2024-02-15-preview"  # Try different API version
    )
    
    # Test with a simple completion
    print("\nTesting simple completion...")
    response = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, world!"}
        ]
    )
    
    print(f"Response: {response.choices[0].message.content}")
    print("Connection successful!")
    
except Exception as e:
    print(f"Error: {str(e)}")