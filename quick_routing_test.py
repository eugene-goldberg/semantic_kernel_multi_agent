#!/usr/bin/env python3
"""
Quick test script to verify routing to all deployed agents.
Tests one query for each agent type.
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

def load_agent_ids():
    """Load agent IDs from deployment files"""
    try:
        with open("orchestration_deployment_info.json", "r") as f:
            info = json.load(f)
            return {
                "orchestrator": info.get("orchestrator_agent_id"),
                "chat": info.get("chat_agent_id"),
                "weather": info.get("weather_agent_id"),
                "calculator": info.get("calculator_agent_id")
            }
    except Exception as e:
        print(f"Error loading agent IDs: {e}")
        return {}

def test_routing(client, orchestrator_id, query, expected_agent):
    """Test the Orchestrator's routing for a specific query"""
    print(f"\n--- Testing routing for: '{query}' ---")
    print(f"Expected agent: {expected_agent}")
    
    try:
        # Create a thread
        thread = client.beta.threads.create()
        
        # Add a message to the thread
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=query
        )
        
        # Run the orchestrator
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=orchestrator_id
        )
        
        # Wait for the run to complete
        print("Waiting for response", end="")
        max_wait = 30  # seconds
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            
            if run_status.status in ["completed", "failed", "cancelled", "expired"]:
                print(f" Done! Status: {run_status.status}")
                break
                
            print(".", end="", flush=True)
            time.sleep(1)
        
        # Check for timeout
        if run_status.status not in ["completed"]:
            print(f"\nRun didn't complete. Status: {run_status.status}")
            return False
            
        # Get messages
        messages = client.beta.threads.messages.list(
            thread_id=thread.id,
            order="desc"
        )
        
        # Find orchestrator's response
        for message in messages.data:
            if message.role == "assistant":
                content = message.content[0].text.value if message.content else "No content"
                print(f"\nResponse: {content}")
                
                # Check if the expected agent is mentioned
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
    # Get OpenAI client
    client = get_client()
    
    # Load agent IDs
    agent_ids = load_agent_ids()
    orchestrator_id = agent_ids.get("orchestrator")
    
    if not orchestrator_id:
        print("Orchestrator Agent ID not found")
        return
    
    print(f"Using Orchestrator Agent: {orchestrator_id}")
    
    # Test one query for each agent type
    test_cases = [
        {"query": "What is the capital of France?", "expected_agent": "chat"},
        {"query": "What's the weather like in New York?", "expected_agent": "weather"},
        {"query": "Calculate 25 × 4", "expected_agent": "calculator"}
    ]
    
    # Run the tests
    results = []
    for test in test_cases:
        success = test_routing(client, orchestrator_id, test["query"], test["expected_agent"])
        results.append({"query": test["query"], "expected": test["expected_agent"], "success": success})
    
    # Print summary
    print("\n=== TEST SUMMARY ===")
    for result in results:
        status = "✓" if result["success"] else "✗"
        print(f"{status} {result['query']} -> {result['expected']}")
    
    success_count = sum(1 for r in results if r["success"])
    print(f"\nResults: {success_count}/{len(results)} tests passed")

if __name__ == "__main__":
    main()