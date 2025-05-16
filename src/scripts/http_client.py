#!/usr/bin/env python3
import argparse
import httpx
import json
import sys

API_URL = "http://localhost:8000"

async def get_agents():
    """Get information about deployed agents"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}/agents")
        if response.status_code == 200:
            data = response.json()
            print("Deployed Agents:")
            for agent in data["agents"]:
                print(f"  {agent['name']} (Type: {agent['type']}, ID: {agent['id']})")
                print(f"    Model: {agent['model']}")
                print(f"    Created: {agent['created_at']}")
                print()
        else:
            print(f"Error: {response.status_code} - {response.text}")

async def send_message(agent_type, message, thread_id=None):
    """Send a message to an agent"""
    request_data = {
        "message": message,
        "agent_type": agent_type
    }
    
    if thread_id:
        request_data["thread_id"] = thread_id
        
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_URL}/message", json=request_data)
        if response.status_code == 200:
            data = response.json()
            print(f"Thread ID: {data['thread_id']}")
            print(f"Agent ID: {data['agent_id']}")
            print(f"Response: {data['response']}")
            
            # Return thread ID for continued conversation
            return data["thread_id"]
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

async def interactive_chat(agent_type):
    """Start an interactive chat with an agent"""
    print(f"Starting interactive chat with {agent_type} agent...")
    print("Type 'exit' to quit.")
    
    thread_id = None
    
    while True:
        try:
            user_input = input("User:> ")
        except (KeyboardInterrupt, EOFError):
            print("\n\nExiting chat...")
            break
            
        if user_input.lower().strip() == "exit":
            print("\n\nExiting chat...")
            break
            
        thread_id = await send_message(agent_type, user_input, thread_id)
        if not thread_id:
            print("Error in conversation. Exiting.")
            break

async def main():
    """Main entry point for the HTTP client"""
    parser = argparse.ArgumentParser(description="HTTP Client for Multi-Agent API")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Agents command
    subparsers.add_parser("agents", help="Get information about deployed agents")
    
    # Message command
    message_parser = subparsers.add_parser("message", help="Send a message to an agent")
    message_parser.add_argument("--agent", "-a", type=str, required=True, choices=["chat", "weather"],
                               help="Agent type to message (chat or weather)")
    message_parser.add_argument("--message", "-m", type=str, required=True,
                              help="Message to send")
    message_parser.add_argument("--thread", "-t", type=str, default=None,
                              help="Thread ID for continued conversation")
    
    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Start an interactive chat with an agent")
    chat_parser.add_argument("--agent", "-a", type=str, required=True, choices=["chat", "weather"],
                            help="Agent type to chat with (chat or weather)")
    
    args = parser.parse_args()
    
    if args.command == "agents":
        await get_agents()
    elif args.command == "message":
        await send_message(args.agent, args.message, args.thread)
    elif args.command == "chat":
        await interactive_chat(args.agent)
    else:
        parser.print_help()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())