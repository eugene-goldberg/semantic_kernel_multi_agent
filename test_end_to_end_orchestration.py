#!/usr/bin/env python3
"""
End-to-end orchestration test that validates:
1. Orchestrator correctly routes requests to specialized agents
2. Each specialized agent returns a valid response for its domain
3. The entire orchestration flow works cohesively
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

def test_orchestration_flow(client, orchestrator_id, query, expected_agent_type):
    """Test the full orchestration flow for a query, including routing and specialized agent response"""
    print(f"\n*** Testing Orchestration Flow: '{query}' ***")
    print(f"Expected agent type: {expected_agent_type}")
    
    try:
        # Step 1: Send query to Orchestrator
        print("\n1. ORCHESTRATOR ROUTING:")
        
        # Create a thread for orchestrator
        thread = client.beta.threads.create()
        print(f"Thread ID: {thread.id}")
        
        # Add the query message to the thread
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
        
        # Wait for orchestrator response
        print("Waiting for orchestrator response", end="")
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
        
        # Check for timeout or failure
        if run_status.status != "completed":
            print(f"Orchestrator run didn't complete. Status: {run_status.status}")
            return False
        
        # Get orchestrator's message
        messages = client.beta.threads.messages.list(
            thread_id=thread.id,
            order="desc"
        )
        
        orchestrator_message = None
        for message in messages.data:
            if message.role == "assistant":
                orchestrator_message = message.content[0].text.value if message.content else "No content"
                break
        
        if not orchestrator_message:
            print("No response from Orchestrator")
            return False
        
        print(f"Orchestrator response: {orchestrator_message}")
        
        # Check if orchestrator mentions expected agent type
        routing_correct = expected_agent_type.lower() in orchestrator_message.lower()
        if routing_correct:
            print(f"✓ Orchestrator correctly routed to {expected_agent_type} Agent")
        else:
            print(f"✗ Orchestrator did not route to expected {expected_agent_type} Agent")
            return False
        
        # Step 2: Send query to the specialized agent
        print(f"\n2. {expected_agent_type.upper()} AGENT RESPONSE:")
        
        # Get specialized agent's ID
        agent_ids = load_agent_ids()
        specialized_agent_id = agent_ids.get(expected_agent_type.lower())
        
        if not specialized_agent_id:
            print(f"Missing ID for {expected_agent_type} Agent")
            return False
        
        # Create a new thread for specialized agent
        specialized_thread = client.beta.threads.create()
        
        # Add the query message to the thread
        client.beta.threads.messages.create(
            thread_id=specialized_thread.id,
            role="user",
            content=query
        )
        
        # Run the specialized agent
        specialized_run = client.beta.threads.runs.create(
            thread_id=specialized_thread.id,
            assistant_id=specialized_agent_id
        )
        
        # Wait for specialized agent response
        print(f"Waiting for {expected_agent_type} agent response", end="")
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=specialized_thread.id,
                run_id=specialized_run.id
            )
            
            if run_status.status in ["completed", "failed", "cancelled", "expired"]:
                print(f" Done! Status: {run_status.status}")
                break
                
            print(".", end="", flush=True)
            time.sleep(1)
        
        # Check for timeout or failure
        if run_status.status != "completed":
            print(f"{expected_agent_type} agent run didn't complete. Status: {run_status.status}")
            return False
        
        # Get specialized agent's message
        specialized_messages = client.beta.threads.messages.list(
            thread_id=specialized_thread.id,
            order="desc"
        )
        
        specialized_message = None
        for message in specialized_messages.data:
            if message.role == "assistant":
                specialized_message = message.content[0].text.value if message.content else "No content"
                break
        
        if not specialized_message:
            print(f"No response from {expected_agent_type} Agent")
            return False
        
        print(f"{expected_agent_type} Agent response: {specialized_message}")
        
        # Check if specialized agent provided a valid response
        if specialized_message and len(specialized_message) > 10:
            print(f"✓ {expected_agent_type} Agent provided a valid response")
            return True
        else:
            print(f"✗ {expected_agent_type} Agent response was invalid or too short")
            return False
        
    except Exception as e:
        print(f"\nError testing orchestration flow: {str(e)}")
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
    print("Testing end-to-end orchestration flow")
    
    # Test cases for each agent type
    test_cases = [
        {"query": "Who wrote Pride and Prejudice?", "expected_agent": "chat"},
        {"query": "What's the weather like in Chicago?", "expected_agent": "weather"},
        {"query": "Calculate the square root of 64", "expected_agent": "calculator"}
    ]
    
    # Run tests
    results = []
    for test in test_cases:
        success = test_orchestration_flow(client, orchestrator_id, test["query"], test["expected_agent"])
        results.append({
            "query": test["query"],
            "expected_agent": test["expected_agent"], 
            "success": success
        })
    
    # Print summary
    print("\n=== END-TO-END ORCHESTRATION TEST SUMMARY ===")
    for result in results:
        status = "✓" if result["success"] else "✗"
        print(f"{status} '{result['query']}' -> {result['expected_agent']} Agent")
    
    success_count = sum(1 for r in results if r["success"])
    print(f"\nResults: {success_count}/{len(results)} tests passed")

if __name__ == "__main__":
    main()