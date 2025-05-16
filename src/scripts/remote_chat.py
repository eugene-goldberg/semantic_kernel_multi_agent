#!/usr/bin/env python3
import asyncio
import os
import json
from src.utils.azure_agent_factory import AzureAgentFactory

class RemoteAgentChat:
    """Client for communicating with agents deployed to Azure AI Agent Service"""
    
    def __init__(self):
        self.client = None
        self.thread_id = None
        self.agent_id = None
    
    async def initialize(self):
        """Initialize the remote chat client"""
        self.client = await AzureAgentFactory.create_client()
        
        # Create a new thread for the conversation
        thread = await AzureAgentFactory.create_thread(self.client)
        self.thread_id = thread.id
        
        # Load deployment info
        try:
            with open("deployment_info.json", "r") as f:
                deployment_info = json.load(f)
                
            # For this simple example, we'll use the chat agent
            self.agent_id = deployment_info.get("chat_agent_id")
            
            if not self.agent_id:
                raise ValueError("Chat agent ID not found in deployment_info.json")
                
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Error loading deployment info: {str(e)}")
        
        print(f"Remote chat initialized with agent ID: {self.agent_id}")
        print(f"Thread ID: {self.thread_id}")
    
    async def send_message(self, message):
        """Send a message to the agent"""
        # Add the message to the thread
        await AzureAgentFactory.add_message_to_thread(
            thread_id=self.thread_id,
            content=message,
            client=self.client
        )
        
        # Run the agent
        await AzureAgentFactory.run_agent(
            thread_id=self.thread_id,
            agent_id=self.agent_id,
            client=self.client
        )
        
        # Get the messages from the thread
        messages = await AzureAgentFactory.get_messages(
            thread_id=self.thread_id,
            client=self.client
        )
        
        # Get the latest assistant message
        for message in reversed(messages):
            if message.role == "assistant":
                return message.content
        
        return None
    
    async def cleanup(self):
        """Clean up resources"""
        if self.thread_id:
            try:
                await AzureAgentFactory.delete_thread(
                    thread_id=self.thread_id,
                    client=self.client
                )
                print(f"Thread {self.thread_id} deleted")
            except Exception as e:
                print(f"Error deleting thread: {str(e)}")

async def main():
    """Main entry point for the remote chat client"""
    chat_client = RemoteAgentChat()
    
    try:
        await chat_client.initialize()
        
        print("Welcome to the remote agent chat!")
        print("  Type 'exit' to exit.")
        
        while True:
            try:
                user_input = input("User:> ")
            except (KeyboardInterrupt, EOFError):
                print("\n\nExiting chat...")
                break
                
            if user_input.lower().strip() == "exit":
                print("\n\nExiting chat...")
                break
                
            print("Waiting for response...")
            response = await chat_client.send_message(user_input)
            
            if response:
                print(f"Agent:> {response}")
            else:
                print("Agent:> No response received")
    
    finally:
        # Clean up resources
        await chat_client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())