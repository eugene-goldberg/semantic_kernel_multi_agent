#!/usr/bin/env python3
"""
Interact with agents deployed as Azure OpenAI Assistants.
"""

import os
import sys
import json
import time
from openai import AzureOpenAI
from dotenv import load_dotenv

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from src.config.settings import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY
)

class OpenAIAssistantClient:
    """Client for interacting with Azure OpenAI Assistants"""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Check required variables
        if not all([AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY]):
            raise ValueError("Missing required environment variables for Azure OpenAI")
        
        # Initialize OpenAI client
        self.client = AzureOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            api_version="2024-05-01-preview"
        )
        
        # Load agent IDs
        self.agents = self.load_deployed_agents()
        self.current_thread_id = None
        
        # Print API info
        print(f"Connected to Azure OpenAI at: {AZURE_OPENAI_ENDPOINT}")
    
    def load_deployed_agents(self):
        """Load deployed agent IDs from file"""
        try:
            with open("deployment_info.json", "r") as f:
                deployment_info = json.load(f)
            
            agents = {
                "chat": deployment_info.get("chat_agent_id"),
                "weather": deployment_info.get("weather_agent_id")
            }
            
            print(f"Loaded agents: Chat={agents['chat']}, Weather={agents['weather']}")
            return agents
        except Exception as e:
            print(f"Error loading agents: {str(e)}")
            return {"chat": None, "weather": None}
    
    def list_available_assistants(self):
        """List all available assistants"""
        try:
            assistants = self.client.beta.assistants.list(limit=100)
            print(f"Found {len(assistants.data)} assistants:")
            
            for assistant in assistants.data:
                print(f"  - {assistant.name} (ID: {assistant.id})")
                
                # Update agents dictionary with matching assistants
                if assistant.name.lower() == "chatagent":
                    self.agents["chat"] = assistant.id
                elif assistant.name.lower() == "weatheragent":
                    self.agents["weather"] = assistant.id
            
            return True
        except Exception as e:
            print(f"Error listing assistants: {str(e)}")
            return False
    
    def create_thread(self):
        """Create a new thread"""
        try:
            thread = self.client.beta.threads.create()
            self.current_thread_id = thread.id
            print(f"Created thread with ID: {self.current_thread_id}")
            return True
        except Exception as e:
            print(f"Error creating thread: {str(e)}")
            return False
    
    def send_message(self, agent_type, message_text):
        """Send a message to an agent"""
        if not self.current_thread_id:
            print("No active thread. Creating one...")
            if not self.create_thread():
                return False
        
        if agent_type not in self.agents or not self.agents[agent_type]:
            print(f"No {agent_type} agent found. Please check deployment.")
            return False
        
        agent_id = self.agents[agent_type]
        
        try:
            # Add message to thread
            message = self.client.beta.threads.messages.create(
                thread_id=self.current_thread_id,
                role="user",
                content=message_text
            )
            
            # Run the assistant
            run = self.client.beta.threads.runs.create(
                thread_id=self.current_thread_id,
                assistant_id=agent_id
            )
            
            # Wait for completion
            while True:
                run_status = self.client.beta.threads.runs.retrieve(
                    thread_id=self.current_thread_id,
                    run_id=run.id
                )
                
                if run_status.status in ["completed", "failed", "cancelled", "expired"]:
                    break
                
                print(f"Run status: {run_status.status}, waiting...")
                time.sleep(1)
            
            if run_status.status != "completed":
                print(f"Run failed with status: {run_status.status}")
                return False
            
            # Get messages
            messages = self.client.beta.threads.messages.list(
                thread_id=self.current_thread_id
            )
            
            # Find the latest assistant message
            assistant_messages = [m for m in messages.data if m.role == "assistant"]
            
            if assistant_messages:
                latest_message = assistant_messages[0]  # First is most recent
                content = latest_message.content[0].text.value if latest_message.content else "No content"
                print(f"\nAgent: {content}")
                return True
            else:
                print("No response from agent found.")
                return False
                
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            return False
    
    def interactive_chat(self, agent_type="chat"):
        """Start an interactive chat session"""
        print(f"Starting interactive chat with {agent_type} agent...")
        print("Type 'exit' to quit, 'switch' to change agent, or 'clear' to start a new thread.")
        
        while True:
            try:
                user_input = input("\nYou: ")
            except (KeyboardInterrupt, EOFError):
                print("\nExiting chat...")
                break
            
            if user_input.lower() == "exit":
                print("Exiting chat...")
                break
            elif user_input.lower() == "switch":
                if agent_type == "chat":
                    agent_type = "weather"
                else:
                    agent_type = "chat"
                print(f"Switched to {agent_type} agent.")
                continue
            elif user_input.lower() == "clear":
                if self.create_thread():
                    print("Started a new conversation thread.")
                continue
            
            self.send_message(agent_type, user_input)

def main():
    """Main entry point"""
    try:
        client = OpenAIAssistantClient()
        
        # First try to load from deployment info
        if None in client.agents.values():
            # If that fails, try to discover agents
            if not client.list_available_assistants():
                print("No assistants found. Please deploy assistants first.")
                return
        
        # Create initial thread
        client.create_thread()
        
        # Start interactive chat
        client.interactive_chat()
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()