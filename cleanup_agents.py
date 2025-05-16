#!/usr/bin/env python3
"""
Cleanup script to remove older agent versions from Azure OpenAI.
"""

import os
import json
from openai import AzureOpenAI

def get_client():
    """Initialize OpenAI client with Azure credentials"""
    # Set up Azure OpenAI client
    client = AzureOpenAI(
        azure_endpoint="https://sk-multi-agent-openai.openai.azure.com/",
        api_key="48d4df6c7b5a49f38d7675620f8e3aa0",
        api_version="2024-02-15-preview"
    )
    return client

def get_current_agent_ids():
    """Get the IDs of the current agents we want to keep"""
    current_ids = set()
    
    try:
        # Load orchestration deployment info
        with open("orchestration_deployment_info.json", "r") as f:
            info = json.load(f)
            current_ids.add(info.get("orchestrator_agent_id"))
            current_ids.add(info.get("chat_agent_id"))
            current_ids.add(info.get("weather_agent_id"))
    except Exception as e:
        print(f"Warning: Could not load orchestration deployment info: {e}")
    
    # Remove None values
    current_ids = {id for id in current_ids if id}
    
    return current_ids

def list_and_delete_agents():
    """List all agents and delete the ones not in current use"""
    client = get_client()
    current_ids = get_current_agent_ids()
    
    print(f"Current agent IDs to keep: {current_ids}")
    
    # List all assistants
    assistants = client.beta.assistants.list(limit=100)
    
    print(f"\nFound {len(assistants.data)} agents:")
    
    for assistant in assistants.data:
        assistant_id = assistant.id
        name = assistant.name
        
        if assistant_id in current_ids:
            print(f"  - {name} (ID: {assistant_id}) - KEEPING")
        else:
            print(f"  - {name} (ID: {assistant_id}) - DELETING")
            try:
                client.beta.assistants.delete(assistant_id)
                print(f"    ✓ Deleted successfully")
            except Exception as e:
                print(f"    ✗ Error deleting: {e}")
    
    # List remaining assistants
    print("\nRemaining agents after cleanup:")
    remaining = client.beta.assistants.list(limit=100)
    for assistant in remaining.data:
        print(f"  - {assistant.name} (ID: {assistant.id})")
    
    print(f"\nCleanup complete. {len(assistants.data) - len(remaining.data)} agents deleted, {len(remaining.data)} agents remain.")

if __name__ == "__main__":
    list_and_delete_agents()