#!/usr/bin/env python3
import asyncio
import os
import sys

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from semantic_kernel.agents import ChatHistoryAgentThread
from src.utils.local_agent_factory import LocalAgentFactory

async def chat():
    """
    Continuously prompt the user for input and show the assistant's response.
    Type 'exit' to exit.
    """
    try:
        user_input = input("User:> ")
    except (KeyboardInterrupt, EOFError):
        print("\n\nExiting chat...")
        return False

    if user_input.lower().strip() == "exit":
        print("\n\nExiting chat...")
        return False

    response = await orchestrator_agent.get_agent().get_response(
        messages=user_input,
        thread=thread,
    )

    if response:
        print(f"Agent :> {response}")

    return True

async def main():
    """Main entry point for the local chat client."""
    global orchestrator_agent, thread
    
    print("Initializing agents...")
    orchestrator_agent = LocalAgentFactory.create_orchestrator_agent()
    
    # Create a thread for the conversation
    thread = ChatHistoryAgentThread()
    
    print("Welcome to the multi-agent chat system!")
    print("  Type 'exit' to exit.")
    print("  You can ask general questions or about the weather.")
    
    chatting = True
    while chatting:
        chatting = await chat()

if __name__ == "__main__":
    orchestrator_agent = None
    thread = None
    asyncio.run(main())