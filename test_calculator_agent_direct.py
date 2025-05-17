#!/usr/bin/env python3
"""
Direct test script for the Calculator Agent on Azure.
"""

import os
import sys
import json
import time
from openai import AzureOpenAI
from dotenv import load_dotenv

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from src.config.settings import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY
)

def get_client():
    """Initialize OpenAI client with Azure credentials"""
    # Load environment variables
    load_dotenv()
    
    # Try to load from .env.deploy if it exists, but don't fail if it doesn't
    try:
        if os.path.exists(".env.deploy"):
            with open(".env.deploy", "r") as f:
                for line in f:
                    if line.strip() and not line.startswith("#"):
                        key, value = line.strip().split("=", 1)
                        os.environ[key] = value
    except Exception as e:
        print(f"Note: Could not load .env.deploy: {str(e)}. Using environment variables instead.")
    
    # Check required variables
    if not all([AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY]):
        raise ValueError("Missing required environment variables for Azure OpenAI")
    
    # Set up Azure OpenAI client
    client = AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version="2024-02-15-preview"
    )
    return client

def get_calculator_agent_id():
    """Get the Calculator Agent ID from deployment file"""
    try:
        with open("orchestration_deployment_info.json", "r") as f:
            info = json.load(f)
            return info.get("calculator_agent_id")
    except Exception as e:
        print(f"Error loading agent ID: {e}")
        return None

def test_calculator_agent(client, agent_id, query):
    """Test the Calculator Agent with a specific query"""
    print(f"\n--- Testing Calculator Agent with: '{query}' ---\n")
    
    try:
        # Create a new thread
        thread = client.beta.threads.create()
        thread_id = thread.id
        print(f"Created thread with ID: {thread_id}")
        
        # Add the message to the thread
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=query
        )
        print("Added message to thread")
        
        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=agent_id
        )
        run_id = run.id
        print(f"Started run with ID: {run_id}")
        
        # Wait for completion
        print("Waiting for response...", end="")
        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id
            )
            
            if run_status.status in ["completed", "failed", "cancelled", "expired"]:
                print(f" Done! Status: {run_status.status}")
                break
            
            print(".", end="", flush=True)
            time.sleep(1)
        
        # Get the messages
        messages = client.beta.threads.messages.list(
            thread_id=thread_id,
            order="desc"
        )
        
        # Find the assistant's response
        for message in messages.data:
            if message.role == "assistant":
                content = message.content[0].text.value if message.content else "No content"
                print(f"\nCalculator response: {content}")
                return content
        
        print("\nNo assistant response found in the thread")
        return None
        
    except Exception as e:
        print(f"\nError testing Calculator Agent: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main test function"""
    try:
        # Get OpenAI client
        client = get_client()
        
        # Get Calculator Agent ID
        calculator_id = get_calculator_agent_id()
        if not calculator_id:
            print("Calculator Agent ID not found")
            return
            
        print(f"Using Calculator Agent ID: {calculator_id}")
        
        # Test queries
        test_queries = [
            "Calculate the square root of 144",
            "What is the determinant of matrix [[1,2],[3,4]]?",
            "Solve the equation x^2 - 5x + 6 = 0",
            "What is 2 + 2?",
            "What is the derivative of x^2 with respect to x?"
        ]
        
        # Run tests
        for query in test_queries:
            test_calculator_agent(client, calculator_id, query)
            
        print("\nCalculator Agent testing complete!")
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()