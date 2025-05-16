#!/usr/bin/env python3
import argparse
import asyncio
import json
import os
from src.utils.azure_agent_factory import AzureAgentFactory

async def get_agent_info():
    """Get information about deployed agents"""
    try:
        # Load deployment info
        if not os.path.exists("deployment_info.json"):
            print("No deployment info found. Please deploy agents first.")
            return
            
        with open("deployment_info.json", "r") as f:
            deployment_info = json.load(f)
        
        # Create client
        client = await AzureAgentFactory.create_client()
        
        # Get agent details
        for agent_key, agent_id in deployment_info.items():
            try:
                agent = await client.agents.get_agent(agent_id)
                print(f"{agent_key}: {agent.name} (ID: {agent.id})")
                print(f"  Model: {agent.model}")
                print(f"  Created: {agent.created_at}")
                print()
            except Exception as e:
                print(f"Error retrieving {agent_key} (ID: {agent_id}): {str(e)}")
        
    except Exception as e:
        print(f"Error getting agent info: {str(e)}")

async def send_message(agent_type, message):
    """Send a message to a specific agent"""
    try:
        # Load deployment info
        if not os.path.exists("deployment_info.json"):
            print("No deployment info found. Please deploy agents first.")
            return
            
        with open("deployment_info.json", "r") as f:
            deployment_info = json.load(f)
        
        # Determine agent ID based on type
        agent_key = f"{agent_type}_agent_id"
        if agent_key not in deployment_info:
            print(f"No agent found with type: {agent_type}")
            return
            
        agent_id = deployment_info[agent_key]
        
        # Create client
        client = await AzureAgentFactory.create_client()
        
        # Create a thread
        thread = await AzureAgentFactory.create_thread(client)
        
        try:
            # Add message to thread
            await AzureAgentFactory.add_message_to_thread(
                thread_id=thread.id,
                content=message,
                client=client
            )
            
            # Run the agent
            await AzureAgentFactory.run_agent(
                thread_id=thread.id,
                agent_id=agent_id,
                client=client
            )
            
            # Get the messages
            messages = await AzureAgentFactory.get_messages(
                thread_id=thread.id,
                client=client
            )
            
            # Print the conversation
            print("\nConversation:")
            for msg in messages:
                print(f"{msg.role}: {msg.content}")
                
        finally:
            # Clean up the thread
            await AzureAgentFactory.delete_thread(
                thread_id=thread.id,
                client=client
            )
        
    except Exception as e:
        print(f"Error sending message: {str(e)}")

async def main():
    """Main entry point for the API client"""
    parser = argparse.ArgumentParser(description="Interact with deployed agents")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Get information about deployed agents")
    
    # Message command
    message_parser = subparsers.add_parser("message", help="Send a message to an agent")
    message_parser.add_argument("--agent", "-a", type=str, required=True, choices=["chat", "weather"],
                               help="Agent type to message (chat or weather)")
    message_parser.add_argument("--message", "-m", type=str, required=True,
                              help="Message to send")
    
    args = parser.parse_args()
    
    if args.command == "info":
        await get_agent_info()
    elif args.command == "message":
        await send_message(args.agent, args.message)
    else:
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main())