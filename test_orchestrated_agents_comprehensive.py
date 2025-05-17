#!/usr/bin/env python3
"""
Comprehensive test script for orchestrated agents on Azure.
Tests all agent types: Chat, Weather, Calculator, and Orchestrator
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

def wait_for_run(client, thread_id, run_id):
    """Wait for a run to complete"""
    print("Waiting for response...", end="")
    while True:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
        )
        
        if run.status in ["completed", "failed", "cancelled", "expired"]:
            print(" Done!")
            return run
        
        print(".", end="", flush=True)
        time.sleep(1)

def get_response(client, thread_id):
    """Get the assistant's response from the thread"""
    messages = client.beta.threads.messages.list(
        thread_id=thread_id,
        order="desc",
        limit=1
    )
    
    if not messages.data:
        return "No response received"
    
    message = messages.data[0]
    if message.role != "assistant":
        return "No assistant response found"
    
    return message.content[0].text.value

def send_message_to_agent(client, agent_id, message):
    """Send a message to a specific agent and get the response"""
    # Create a new thread
    thread = client.beta.threads.create()
    thread_id = thread.id
    
    # Add message to the thread
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message
    )
    
    # Run the assistant on the thread
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=agent_id
    )
    
    # Wait for completion
    run = wait_for_run(client, thread_id, run.id)
    
    # Get the response
    return get_response(client, thread_id)

def main():
    """Main test function"""
    try:
        client = get_client()
        agent_ids = load_agent_ids()
        
        if not all(agent_ids.values()):
            raise ValueError("Missing agent IDs. Please check orchestration_deployment_info.json")
        
        print("Testing orchestrated agents with comprehensive tests")
        print(f"Agent IDs: {json.dumps(agent_ids, indent=2)}")
        
        # Test messages covering all agent types
        test_messages = [
            # Weather tests
            {"message": "What's the weather like in Seattle today?", "expected_agent": "weather"},
            {"message": "Is it going to rain in New York tomorrow?", "expected_agent": "weather"},
            
            # Calculator tests
            {"message": "Calculate the determinant of matrix [[1,2],[3,4]]", "expected_agent": "calculator"},
            {"message": "What's the derivative of x^2 + 3x + 2?", "expected_agent": "calculator"},
            {"message": "Solve the equation x^2 - 5x + 6 = 0", "expected_agent": "calculator"},
            {"message": "What's the square root of 144?", "expected_agent": "calculator"},
            
            # Chat tests
            {"message": "Tell me about the history of the internet", "expected_agent": "chat"},
            {"message": "What is artificial intelligence?", "expected_agent": "chat"},
            
            # Ambiguous tests
            {"message": "I'm planning a trip to Chicago and want to know about the weather and history", "expected_agent": "chat"}
        ]
        
        print("\n=== TESTING ORCHESTRATOR ROUTING ===\n")
        
        # First test: Check if orchestrator correctly identifies agent to use
        for i, test in enumerate(test_messages):
            message = test["message"]
            expected = test["expected_agent"]
            
            print(f"\n--- TEST {i+1}: '{message}' ---\n")
            print(f"Expected agent: {expected}")
            
            # Send to orchestrator
            print(f"Sending to orchestrator...")
            orchestrator_response = send_message_to_agent(client, agent_ids["orchestrator"], message)
            print(f"Orchestrator response: {orchestrator_response}")
            
            # Determine if orchestrator chose correctly
            correct_routing = False
            if expected == "weather" and "weather agent" in orchestrator_response.lower():
                correct_routing = True
            elif expected == "calculator" and "calculator agent" in orchestrator_response.lower():
                correct_routing = True
            elif expected == "chat" and "chat agent" in orchestrator_response.lower():
                correct_routing = True
            
            if correct_routing:
                print("✓ Orchestrator correctly identified the appropriate agent")
            else:
                print("✗ Orchestrator may have chosen a different agent than expected")
        
        print("\n=== TESTING DIRECT AGENT RESPONSES ===\n")
        
        # Second test: Check each specialized agent directly
        specialized_tests = [
            {"agent": "chat", "message": "What are the three laws of robotics?"},
            {"agent": "weather", "message": "What's the weather like in Miami?"},
            {"agent": "calculator", "message": "Calculate the mean of 10, 20, 30, 40, 50"}
        ]
        
        for test in specialized_tests:
            agent_type = test["agent"]
            message = test["message"]
            
            print(f"\n--- Testing {agent_type.upper()} agent directly ---")
            print(f"Query: {message}")
            
            response = send_message_to_agent(client, agent_ids[agent_type], message)
            print(f"{agent_type.capitalize()} agent response: {response}")
            
            if response and "error" not in response.lower():
                print(f"✓ {agent_type.capitalize()} agent responded successfully")
            else:
                print(f"✗ {agent_type.capitalize()} agent may have had issues")
        
        print("\n\nComprehensive testing complete!")
        
    except Exception as e:
        print(f"\nError during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()