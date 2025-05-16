#!/usr/bin/env python3
"""
Test script for the simplified Calculator Agent.
Uses a shorter timeout and simpler queries.
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

def get_calculator_id():
    """Get the Calculator Agent ID from deployment file"""
    try:
        with open("orchestration_deployment_info.json", "r") as f:
            info = json.load(f)
            return info.get("calculator_agent_id")
    except Exception as e:
        print(f"Error loading agent ID: {e}")
        return None

def test_calculator(client, calculator_id, query, timeout=15):
    """Test the Calculator Agent with a specific query"""
    print(f"\n--- Testing Calculator Agent with: '{query}' ---")
    
    try:
        # Create a thread
        thread = client.beta.threads.create()
        thread_id = thread.id
        print(f"Thread ID: {thread_id}")
        
        # Add a message to the thread
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=query
        )
        
        # Run the calculator
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=calculator_id
        )
        run_id = run.id
        
        # Wait for response with timeout
        print("Waiting for response", end="")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id
            )
            
            if run_status.status in ["completed", "failed", "cancelled", "expired"]:
                print(f" Done! Status: {run_status.status}")
                break
                
            print(".", end="", flush=True)
            time.sleep(1)
        
        # Check if we timed out
        if run_status.status != "completed":
            print(f"\nTimed out or error. Final status: {run_status.status}")
            return False
        
        # Get messages
        messages = client.beta.threads.messages.list(
            thread_id=thread_id,
            order="desc"
        )
        
        # Print calculator response
        for message in messages.data:
            if message.role == "assistant":
                content = message.content[0].text.value if message.content else "No content"
                print(f"\nCalculator response: {content}")
                return True
        
        print("\nNo assistant response found")
        return False
        
    except Exception as e:
        print(f"\nError testing calculator: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    try:
        # Get OpenAI client
        client = get_client()
        
        # Get Calculator Agent ID
        calculator_id = get_calculator_id()
        if not calculator_id:
            print("Calculator Agent ID not found")
            return
            
        print(f"Using Calculator Agent ID: {calculator_id}")
        
        # Test queries - simple operations first
        test_queries = [
            "What is 2 + 2?",
            "What is the square root of 25?",
            "What is 7 * 8?",
            "Calculate 15% of 200",
            "What is 10 squared?",
            "What is the mean of 10, 20, 30, 40, 50?"
        ]
        
        # Track results
        results = {
            "total": len(test_queries),
            "passed": 0,
            "failed": 0
        }
        
        # Run tests
        for query in test_queries:
            success = test_calculator(client, calculator_id, query)
            if success:
                results["passed"] += 1
            else:
                results["failed"] += 1
        
        # Print summary
        print("\n=== CALCULATOR TEST SUMMARY ===")
        print(f"Total tests: {results['total']}")
        print(f"Passed: {results['passed']}")
        print(f"Failed: {results['failed']}")
        print(f"Success rate: {results['passed'] / results['total'] * 100:.1f}%")
        print("===============================")
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()