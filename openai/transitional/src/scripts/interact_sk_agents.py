#!/usr/bin/env python3
"""
Interactive client for SK-based agents deployed to Azure AI Service.
This script provides a unified interface for interacting with deployed agents.
"""

import os
import sys
import json
import asyncio
import logging
from dotenv import load_dotenv

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import *

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SkAgentClient:
    """Client for interacting with SK-based agents deployed to Azure AI Service."""
    
    def __init__(self):
        """Initialize the client with Azure credentials."""
        # Load environment variables
        load_dotenv()
        
        # Azure AI Service settings
        self.ai_project_host = os.getenv("AZURE_AI_PROJECT_HOST")
        self.subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        self.resource_group = os.getenv("AZURE_RESOURCE_GROUP")
        self.ai_hub_name = os.getenv("AZURE_AI_HUB_NAME")
        self.ai_project_name = os.getenv("AZURE_AI_PROJECT_NAME")
        self.connection_string = os.getenv("AZURE_AI_PROJECT_CONNECTION_STRING")
        
        # Azure credential and client
        self.credential = DefaultAzureCredential()
        self.client = self._create_ai_client()
        
        # Load agent information
        self.agents = self._load_agent_info()
        self.current_agent = "orchestrator"  # Default agent
        
        # Initialize conversation thread
        self.thread_id = None
    
    def _create_ai_client(self):
        """Create an Azure AI Project client."""
        try:
            # Determine endpoint if not provided
            endpoint = self.ai_project_host
            if not endpoint:
                # Use default format if not provided
                region = "westus"  # Default region
                endpoint = f"https://{region}.projectsai.azure.com"
            elif not endpoint.startswith("https://"):
                endpoint = f"https://{endpoint}"
                
            logger.info(f"Creating client for Hub '{self.ai_hub_name}', Project '{self.ai_project_name}'")
            logger.info(f"Using endpoint: {endpoint}")
            
            # Create client
            client = AIProjectClient(
                endpoint=endpoint,
                credential=self.credential
            )
            
            # Set project context if provided
            if self.subscription_id and self.resource_group and self.ai_hub_name and self.ai_project_name:
                logger.info(f"Setting project context: {self.subscription_id}/{self.resource_group}/{self.ai_hub_name}/{self.ai_project_name}")
                client._scope = f"/subscriptions/{self.subscription_id}/resourceGroups/{self.resource_group}/providers/Microsoft.MachineLearningServices/aigalleries/{self.ai_hub_name}/aiprojects/{self.ai_project_name}"
            
            return client
            
        except Exception as e:
            logger.error(f"Failed to create AI Project client: {str(e)}")
            raise
    
    def _load_agent_info(self):
        """Load agent information from deployment file."""
        try:
            # Try to load from SK deployment info
            if os.path.exists("sk_deployment_info.json"):
                with open("sk_deployment_info.json", "r") as f:
                    deployment_info = json.load(f)
            # Fall back to regular deployment info
            elif os.path.exists("orchestration_deployment_info.json"):
                with open("orchestration_deployment_info.json", "r") as f:
                    deployment_info = json.load(f)
            else:
                logger.warning("No deployment info found. Using placeholder agent IDs.")
                return {
                    "chat": {"id": "chat_agent_placeholder"},
                    "weather": {"id": "weather_agent_placeholder"},
                    "calculator": {"id": "calculator_agent_placeholder"},
                    "orchestrator": {"id": "orchestrator_agent_placeholder"}
                }
            
            # Extract agent IDs
            agents = {
                "chat": {"id": deployment_info.get("chat_agent_id")},
                "weather": {"id": deployment_info.get("weather_agent_id")},
                "calculator": {"id": deployment_info.get("calculator_agent_id")},
                "orchestrator": {"id": deployment_info.get("orchestrator_agent_id")}
            }
            
            logger.info("Loaded agent IDs:")
            for agent_type, agent_info in agents.items():
                if agent_info["id"]:
                    logger.info(f"- {agent_type.capitalize()}: {agent_info['id']}")
                else:
                    logger.warning(f"- {agent_type.capitalize()}: Not found")
            
            return agents
        except Exception as e:
            logger.error(f"Error loading agent information: {str(e)}")
            raise
    
    async def send_message(self, message):
        """
        Send a message to the current agent.
        
        Args:
            message: User message text
            
        Returns:
            Agent response text
        """
        # Get current agent ID
        agent_id = self.agents[self.current_agent]["id"]
        if not agent_id:
            return f"Error: No {self.current_agent} agent found"
        
        try:
            # Create or get thread if needed
            if not self.thread_id:
                thread = await self.client.agents.create_thread()
                self.thread_id = thread.id
                logger.info(f"Created new thread: {self.thread_id}")
            
            # Add message to thread
            await self.client.agents.create_message(
                thread_id=self.thread_id,
                role="user",
                content=message
            )
            
            # Run the agent on the thread
            run = await self.client.agents.create_run(
                thread_id=self.thread_id,
                agent_id=agent_id
            )
            
            # Wait for the run to complete
            print("Agent processing...", end="\r")
            while run.status not in ["completed", "failed", "cancelled"]:
                run = await self.client.agents.get_run(
                    thread_id=self.thread_id,
                    run_id=run.id
                )
            
            # Clear processing message
            print("                   ", end="\r")
            
            # Check if run failed
            if run.status == "failed":
                return f"Error: Agent run failed - {run.failure_reason if hasattr(run, 'failure_reason') else 'Unknown error'}"
            
            # Get messages from thread
            messages = await self.client.agents.list_messages(thread_id=self.thread_id)
            
            # Find the latest assistant message
            assistant_messages = [msg for msg in messages if msg.role == "assistant"]
            if not assistant_messages:
                return "Error: No response from agent"
            
            # Get the latest assistant message
            latest_message = assistant_messages[-1]
            response_text = latest_message.content[0].text if latest_message.content else "No response"
            
            return response_text
            
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"Error communicating with agent: {str(e)}"
    
    def switch_agent(self, agent_type):
        """
        Switch to a different agent.
        
        Args:
            agent_type: Type of agent to switch to
            
        Returns:
            Message indicating the switch
        """
        if agent_type not in self.agents:
            return f"Unknown agent type: {agent_type}"
        
        if not self.agents[agent_type]["id"]:
            return f"Error: {agent_type.capitalize()} agent not found in deployment info"
        
        # Switch agent
        self.current_agent = agent_type
        
        # Thread will be cleared on next message
        self.thread_id = None
        
        return f"Switched to {agent_type.capitalize()} Agent"
    
    async def clear_history(self):
        """Clear conversation history by creating a new thread."""
        self.thread_id = None
        thread = await self.client.agents.create_thread()
        self.thread_id = thread.id
        return f"Conversation thread cleared for {self.current_agent.capitalize()} Agent"

async def interactive_chat():
    """Run an interactive chat session with deployed agents."""
    try:
        client = SkAgentClient()
        
        print("\n=== SK Agent Interactive Chat (Azure AI Service) ===")
        print(f"Currently using: {client.current_agent.capitalize()} Agent")
        print("Commands:")
        print("  'exit' - Exit the chat")
        print("  'switch chat/weather/calculator/orchestrator' - Switch to a different agent")
        print("  'clear' - Clear conversation thread")
        
        while True:
            try:
                user_input = input("\nYou: ")
            except (KeyboardInterrupt, EOFError):
                print("\nExiting chat...")
                break
            
            # Process commands
            if user_input.lower() == "exit":
                print("Exiting chat...")
                break
            elif user_input.lower() == "clear":
                result = await client.clear_history()
                print(f"System: {result}")
                continue
            elif user_input.lower().startswith("switch "):
                agent_type = user_input.lower().split(" ", 1)[1].strip()
                result = client.switch_agent(agent_type)
                print(f"System: {result}")
                continue
            elif not user_input.strip():
                continue
            
            # Process regular message
            response = await client.send_message(user_input)
            print(f"{client.current_agent.capitalize()} Agent: {response}")
            
    except Exception as e:
        logger.error(f"Error in interactive chat: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    """Main entry point."""
    try:
        await interactive_chat()
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())