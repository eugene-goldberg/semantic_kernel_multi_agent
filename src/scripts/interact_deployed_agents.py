#!/usr/bin/env python3
import asyncio
import os
import sys
import json
import requests
from azure.identity import DefaultAzureCredential, ClientSecretCredential

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from src.config.settings import (
    AZURE_AI_PROJECT_NAME, 
    AZURE_AI_PROJECT_HOST
)

# Service Principal Authentication - to be set in environment variables
AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")

class DeployedAgentClient:
    """Client for interacting with deployed agents"""
    
    def __init__(self):
        # Try service principal auth first, then fall back to default auth
        if all([AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID]):
            print("Using Service Principal authentication...")
            self.credential = ClientSecretCredential(
                tenant_id=AZURE_TENANT_ID,
                client_id=AZURE_CLIENT_ID,
                client_secret=AZURE_CLIENT_SECRET
            )
        else:
            print("Using Default Azure authentication...")
            self.credential = DefaultAzureCredential()
        
        # Try multiple scopes as the API might require different scopes
        possible_scopes = [
            "https://management.azure.com/.default",  # Azure Management API
            "https://api.aiagent.azure.net/.default",  # Try another endpoint
            "https://aiagent.azure.net/.default"  # Original endpoint
        ]
        
        token_acquired = False
        for scope in possible_scopes:
            try:
                print(f"Trying to authenticate with scope: {scope}")
                self.token = self.credential.get_token(scope)
                print(f"Successfully authenticated with scope: {scope}")
                token_acquired = True
                break
            except Exception as e:
                print(f"Authentication failed with scope {scope}: {str(e)}")
        
        if not token_acquired:
            print("Could not acquire token with any scope. Trying Azure CLI login...")
            try:
                import subprocess
                subprocess.run(["az", "login", "--scope", "https://aiagent.azure.net/.default"], check=True)
                print("Azure CLI login successful. Trying DefaultAzureCredential again...")
                self.credential = DefaultAzureCredential()
                self.token = self.credential.get_token("https://aiagent.azure.net/.default")
                token_acquired = True
            except Exception as e:
                print(f"Azure CLI login failed: {str(e)}")
                print("Please login manually with: az login --scope https://aiagent.azure.net/.default")
                raise Exception("Failed to authenticate. Please login to Azure CLI manually.")
        self.base_url = f"https://{AZURE_AI_PROJECT_HOST}/projects/{AZURE_AI_PROJECT_NAME}"
        self.headers = {
            "Authorization": f"Bearer {self.token.token}",
            "Content-Type": "application/json"
        }
        self.agents = {}
        self.current_thread_id = None
        
        # Print URL that we're connecting to for debugging
        print(f"Connecting to: {self.base_url}")
    
    def load_deployed_agents(self):
        """Load deployed agent IDs from file"""
        try:
            with open("deployment_info.json", "r") as f:
                deployment_info = json.load(f)
                
            self.agents = {
                "chat": deployment_info.get("chat_agent_id"),
                "weather": deployment_info.get("weather_agent_id")
            }
            
            return True
        except Exception as e:
            print(f"Error loading deployed agents: {str(e)}")
            return False
    
    def list_available_agents(self):
        """List all available agents"""
        try:
            response = requests.get(f"{self.base_url}/agents", headers=self.headers)
            
            if response.status_code == 200:
                agents = response.json()
                print(f"Found {len(agents)} agent(s):")
                
                # Update agent dictionary
                self.agents = {}
                
                for agent in agents:
                    agent_id = agent.get("id")
                    name = agent.get("name", "Unknown")
                    print(f"  - {name} (ID: {agent_id})")
                    
                    # Add to agents dictionary based on name
                    if "chat" in name.lower():
                        self.agents["chat"] = agent_id
                    elif "weather" in name.lower():
                        self.agents["weather"] = agent_id
                
                return True
            else:
                print(f"Failed to list agents: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"Error listing agents: {str(e)}")
            return False
    
    def create_thread(self):
        """Create a new thread for conversation"""
        try:
            response = requests.post(f"{self.base_url}/threads", headers=self.headers)
            
            if response.status_code in (200, 201):
                thread = response.json()
                self.current_thread_id = thread.get("id")
                print(f"Created thread with ID: {self.current_thread_id}")
                return True
            else:
                print(f"Failed to create thread: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"Error creating thread: {str(e)}")
            return False
    
    def send_message(self, agent_type, message):
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
            # First add message to thread
            message_payload = {
                "role": "user",
                "content": message
            }
            
            message_response = requests.post(
                f"{self.base_url}/threads/{self.current_thread_id}/messages",
                headers=self.headers,
                json=message_payload
            )
            
            if message_response.status_code not in (200, 201):
                print(f"Failed to add message: {message_response.status_code}")
                print(f"Response: {message_response.text}")
                return False
            
            # Then run the agent
            run_payload = {
                "agent_id": agent_id
            }
            
            run_response = requests.post(
                f"{self.base_url}/threads/{self.current_thread_id}/runs",
                headers=self.headers,
                json=run_payload
            )
            
            if run_response.status_code not in (200, 201):
                print(f"Failed to run agent: {run_response.status_code}")
                print(f"Response: {run_response.text}")
                return False
            
            run = run_response.json()
            run_id = run.get("id")
            
            print(f"Started run with ID: {run_id}")
            
            # Poll for completion
            max_attempts = 60  # 60 x 1s = 60 seconds max wait
            attempts = 0
            
            while attempts < max_attempts:
                run_status_response = requests.get(
                    f"{self.base_url}/threads/{self.current_thread_id}/runs/{run_id}",
                    headers=self.headers
                )
                
                if run_status_response.status_code != 200:
                    print(f"Failed to check run status: {run_status_response.status_code}")
                    break
                
                run_status = run_status_response.json()
                status = run_status.get("status")
                
                if status in ("completed", "failed", "cancelled"):
                    break
                
                print(f"Run status: {status}, waiting...")
                attempts += 1
                # Use regular sleep since this function isn't async
                import time
                time.sleep(1)
            
            if attempts >= max_attempts:
                print("Run timed out. Taking too long to complete.")
                return False
            
            # Get messages
            messages_response = requests.get(
                f"{self.base_url}/threads/{self.current_thread_id}/messages",
                headers=self.headers
            )
            
            if messages_response.status_code != 200:
                print(f"Failed to get messages: {messages_response.status_code}")
                print(f"Response: {messages_response.text}")
                return False
            
            messages = messages_response.json()
            
            # Find the latest assistant message
            assistant_messages = [m for m in messages if m.get("role") == "assistant"]
            
            if assistant_messages:
                latest_message = assistant_messages[-1]
                print(f"\nAgent: {latest_message.get('content')}")
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
    client = DeployedAgentClient()
    
    # First try to load from deployment info
    if not client.load_deployed_agents():
        # If that fails, try to discover agents
        if not client.list_available_agents():
            print("No agents found. Please deploy agents first.")
            return
    
    # Create initial thread
    client.create_thread()
    
    # Start interactive chat
    client.interactive_chat()

if __name__ == "__main__":
    main()