#!/usr/bin/env python3
"""
Test script to check only the Orchestrator's routing decisions.
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

def get_orchestrator_id():
    """Get the Orchestrator Agent ID from deployment file"""
    try:
        with open("orchestration_deployment_info.json", "r") as f:
            info = json.load(f)
            return info.get("orchestrator_agent_id")
    except Exception as e:
        print(f"Error loading orchestrator ID: {e}")
        return None

def test_routing(client, orchestrator_id, query, expected_agent, timeout=30):
    """Test the Orchestrator's routing for a specific query"""
    print(f"\n--- Testing routing for: '{query}' ---")
    print(f"Expected agent: {expected_agent}")
    
    try:
        # Create a thread
        thread = client.beta.threads.create()
        thread_id = thread.id
        print(f"Created thread: {thread_id}")
        
        # Add a message to the thread
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=query
        )
        print("Added message to thread")
        
        # Run the orchestrator
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=orchestrator_id
        )
        run_id = run.id
        print(f"Started run: {run_id}")
        
        # Wait for the run to complete (with timeout)
        start_time = time.time()
        run_status = None
        print("Waiting for response", end="")
        
        while time.time() - start_time < timeout:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id
            )
            
            if run_status.status in ["completed", "failed", "cancelled", "expired"]:
                print(" Done!")
                break
                
            print(".", end="", flush=True)
            time.sleep(1)
        
        # Check if we timed out
        if run_status is None or run_status.status not in ["completed"]:
            print(f" Timed out! Final status: {run_status.status if run_status else 'unknown'}")
            return False
        
        # Get the messages
        messages = client.beta.threads.messages.list(
            thread_id=thread_id,
            order="desc"
        )
        
        # Find the orchestrator's response
        for message in messages.data:
            if message.role == "assistant":
                content = message.content[0].text.value if message.content else "No content"
                print(f"\nOrchestrator response: {content}")
                
                # Check if the response mentions the expected agent
                if expected_agent.lower() in content.lower():
                    print(f"✓ Correctly identified {expected_agent} agent")
                    return True
                else:
                    print(f"✗ Did not identify {expected_agent} agent")
                    return False
        
        print("\nNo assistant response found")
        return False
        
    except Exception as e:
        print(f"\nError testing routing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    try:
        # Get OpenAI client
        client = get_client()
        
        # Get Orchestrator Agent ID
        orchestrator_id = get_orchestrator_id()
        if not orchestrator_id:
            print("Orchestrator Agent ID not found")
            return
            
        print(f"Using Orchestrator Agent ID: {orchestrator_id}")
        
        # Test queries with expected routing
        test_queries = [
            {"query": "What's the weather like in Seattle?", "expected": "weather"},
            {"query": "Tell me about the Golden Gate Bridge", "expected": "chat"},
            {"query": "Calculate the square root of 144", "expected": "calculator"},
            {"query": "What is the determinant of matrix [[1,2],[3,4]]?", "expected": "calculator"},
            {"query": "Solve the equation x^2 - 5x + 6 = 0", "expected": "calculator"},
            {"query": "Who invented the lightbulb?", "expected": "chat"}
        ]
        
        # Track results
        results = {
            "total": len(test_queries),
            "passed": 0,
            "failed": 0
        }
        
        # Run tests
        for test in test_queries:
            success = test_routing(client, orchestrator_id, test["query"], test["expected"])
            if success:
                results["passed"] += 1
            else:
                results["failed"] += 1
        
        # Print summary
        print("\n=== ROUTING TEST SUMMARY ===")
        print(f"Total tests: {results['total']}")
        print(f"Passed: {results['passed']}")
        print(f"Failed: {results['failed']}")
        print(f"Success rate: {results['passed'] / results['total'] * 100:.1f}%")
        print("===========================")
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()