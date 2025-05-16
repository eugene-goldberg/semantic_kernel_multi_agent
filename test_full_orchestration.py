#!/usr/bin/env python3
"""
Test script for full orchestration with all agents including Calculator.
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

def get_agent_response(client, agent_id, query, timeout=20):
    """Get a response from a specific agent"""
    try:
        # Create a thread
        thread = client.beta.threads.create()
        thread_id = thread.id
        
        # Add a message to the thread
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=query
        )
        
        # Run the agent
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=agent_id
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
            print(f"Run didn't complete. Status: {run_status.status}")
            return None
        
        # Get messages
        messages = client.beta.threads.messages.list(
            thread_id=thread_id,
            order="desc"
        )
        
        # Find the agent's response
        for message in messages.data:
            if message.role == "assistant":
                return message.content[0].text.value if message.content else None
        
        return None
        
    except Exception as e:
        print(f"Error getting agent response: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_orchestration(client, agent_ids, query):
    """Test the full orchestration chain for a specific query"""
    print(f"\n\n--- TESTING ORCHESTRATION: '{query}' ---\n")
    
    # Step 1: Send query to Orchestrator
    print("1. Sending to Orchestrator Agent:")
    orchestrator_response = get_agent_response(client, agent_ids["orchestrator"], query)
    
    if not orchestrator_response:
        print("Failed to get response from Orchestrator")
        return False
        
    print(f"Orchestrator response: {orchestrator_response}")
    
    # Step 2: Determine which agent the Orchestrator recommends
    recommended_agent = None
    if "weather agent" in orchestrator_response.lower():
        recommended_agent = "weather"
    elif "calculator agent" in orchestrator_response.lower():
        recommended_agent = "calculator"
    else:
        recommended_agent = "chat"
    
    print(f"\nOrchestrator recommends: {recommended_agent.upper()} Agent\n")
    
    # Step 3: Send query to the recommended agent
    print(f"2. Sending to {recommended_agent.capitalize()} Agent:")
    agent_response = get_agent_response(client, agent_ids[recommended_agent], query)
    
    if not agent_response:
        print(f"Failed to get response from {recommended_agent.capitalize()} Agent")
        return False
        
    print(f"{recommended_agent.capitalize()} Agent response: {agent_response}")
    return True

def main():
    """Main test function"""
    try:
        # Get OpenAI client
        client = get_client()
        
        # Load agent IDs
        agent_ids = load_agent_ids()
        
        # Verify all agent IDs are available
        missing_agents = [name for name, id in agent_ids.items() if not id]
        if missing_agents:
            print(f"Missing agent IDs: {', '.join(missing_agents)}")
            return
            
        print("Testing full orchestration with all agents")
        print(f"Agent IDs: {json.dumps(agent_ids, indent=2)}")
        
        # Test queries covering all agent types
        test_queries = [
            "What's the weather like in Seattle?",
            "What is the square root of 144?",
            "Who wrote the novel Moby Dick?",
            "Calculate the determinant of matrix [[1,2],[3,4]]",
            "What's the temperature in Miami right now?",
            "Solve the equation x^2 - 5x + 6 = 0"
        ]
        
        # Run tests
        for query in test_queries:
            test_orchestration(client, agent_ids, query)
            
        print("\n\nFull orchestration testing complete!")
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()