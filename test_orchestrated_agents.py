#!/usr/bin/env python3
"""
Non-interactive test script for orchestrated agents on Azure.
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

def get_client():
    """Initialize OpenAI client with Azure credentials"""
    # Set up Azure OpenAI client
    client = AzureOpenAI(
        azure_endpoint="https://sk-multi-agent-openai.openai.azure.com/",
        api_key="48d4df6c7b5a49f38d7675620f8e3aa0",
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
                "weather": info.get("weather_agent_id")
            }
    except:
        print("Error loading agent IDs")
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
    client = get_client()
    agent_ids = load_agent_ids()
    
    print("Testing orchestrated agents on Azure")
    print(f"Agent IDs: {json.dumps(agent_ids, indent=2)}")
    
    # Test messages for the different agents
    test_messages = [
        "What's the weather like in Seattle?",
        "Tell me about the Golden Gate Bridge",
        "What's the temperature in Miami right now?",
        "Who invented the lightbulb?"
    ]
    
    for i, message in enumerate(test_messages):
        print(f"\n\n--- TEST {i+1}: '{message}' ---\n")
        
        # First, send to orchestrator
        print(f"1. Sending to orchestrator...")
        orchestrator_response = send_message_to_agent(client, agent_ids["orchestrator"], message)
        print(f"Orchestrator response: {orchestrator_response}")
        
        # Based on message content, determine right agent to contact
        if any(word in message.lower() for word in ["weather", "temperature", "forecast", "rain", "sunny"]):
            agent_type = "weather"
        else:
            agent_type = "chat"
            
        # Send to the appropriate agent
        print(f"\n2. Sending to {agent_type} agent...")
        agent_response = send_message_to_agent(client, agent_ids[agent_type], message)
        print(f"{agent_type.capitalize()} agent response: {agent_response}")
    
    print("\n\nTest complete!")

if __name__ == "__main__":
    main()