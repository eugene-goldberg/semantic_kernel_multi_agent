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

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.functions.kernel_arguments import KernelArguments

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SkAgentClient:
    """Client for interacting with SK-based agents deployed to Azure."""
    
    def __init__(self):
        """Initialize the client with Azure credentials."""
        # Load environment variables
        load_dotenv()
        
        # Azure OpenAI settings
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        
        # Validate settings
        if not all([self.azure_endpoint, self.azure_api_key, self.deployment_name]):
            raise ValueError("Missing required Azure OpenAI configuration in environment")
        
        # Create kernel
        self.kernel = self._create_kernel()
        
        # Load agent information
        self.agents = self._load_agent_info()
        self.current_agent = "orchestrator"  # Default agent
        
        # Initialize chat history
        self.chat_history = []
    
    def _create_kernel(self):
        """Create a kernel with Azure OpenAI service."""
        kernel = sk.Kernel()
        
        # Add Azure OpenAI service
        service = AzureChatCompletion(
            deployment_name=self.deployment_name,
            endpoint=self.azure_endpoint,
            api_key=self.azure_api_key,
            api_version="2024-02-15-preview"
        )
        
        kernel.add_service(service, service_id="chat")
        return kernel
    
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
            # Create chat history for context
            messages = [
                {"role": "system", "content": f"You are the {self.current_agent.capitalize()} agent."}
            ]
            messages.extend(self.chat_history)
            messages.append({"role": "user", "content": message})
            
            # In a real implementation, this would use the specific agent ID
            # For now, we'll use the SK kernel to generate a response
            chat_service = self.kernel.get_service("chat")
            if not chat_service:
                return "Error: Chat service not found in kernel"
            
            # Create completion settings (simplified for demonstration)
            from semantic_kernel.connectors.ai.open_ai import AzureChatPromptExecutionSettings
            settings = AzureChatPromptExecutionSettings()
            
            # Get response
            response_messages = await chat_service.complete_chat_async(
                messages=messages,
                settings=settings
            )
            
            if not response_messages:
                return "Error: No response from agent"
            
            # Extract response text
            response_text = response_messages[0].content if response_messages else "No response"
            
            # Update chat history
            self.chat_history.append({"role": "user", "content": message})
            self.chat_history.append({"role": "assistant", "content": response_text})
            
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
        
        # Clear chat history when switching agents
        self.chat_history = []
        
        return f"Switched to {agent_type.capitalize()} Agent"
    
    def clear_history(self):
        """Clear conversation history."""
        self.chat_history = []
        return f"Conversation history cleared for {self.current_agent.capitalize()} Agent"

async def interactive_chat():
    """Run an interactive chat session with deployed agents."""
    try:
        client = SkAgentClient()
        
        print("\n=== SK Agent Interactive Chat ===")
        print(f"Currently using: {client.current_agent.capitalize()} Agent")
        print("Commands:")
        print("  'exit' - Exit the chat")
        print("  'switch chat/weather/calculator/orchestrator' - Switch to a different agent")
        print("  'clear' - Clear conversation history")
        
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
                result = client.clear_history()
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
            print("Agent thinking...", end="\r")
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