#!/usr/bin/env python3
"""
Factory class for creating Semantic Kernel based agents.
This provides a standardized way to create and configure agents.
"""

import os
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from dotenv import load_dotenv

from src.agents.chat_agent import ChatAgent
from src.agents.weather_agent import WeatherAgent
from src.agents.calculator_agent_sk import CalculatorAgent
from src.agents.orchestrator_agent_updated import OrchestratorAgent

class SkAgentFactory:
    """
    Factory class for creating SK-based agents.
    """
    
    @staticmethod
    def create_service():
        """
        Create an Azure OpenAI chat service with environment settings.
        
        Returns:
            AzureChatCompletion: The configured service
        """
        # Load environment variables
        load_dotenv()
        
        # Get Azure OpenAI configuration
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        
        if not all([endpoint, api_key, deployment]):
            raise ValueError("Azure OpenAI configuration not found in environment")
        
        return AzureChatCompletion(
            service_id="chat",
            deployment_name=deployment,
            endpoint=endpoint,
            api_key=api_key,
            api_version="2024-02-15-preview"
        )
    
    @staticmethod
    def create_kernel():
        """
        Create a kernel with Azure OpenAI service.
        
        Returns:
            Kernel: The configured kernel
        """
        # Create a kernel
        kernel = Kernel()
        
        # Add service to kernel
        service = SkAgentFactory.create_service()
        kernel.add_service(service)
        
        return kernel
    
    @staticmethod
    def create_agent(agent_type):
        """
        Create an agent of the specified type.
        
        Args:
            agent_type (str): The type of agent to create ('chat', 'weather', 'calculator', 'orchestrator')
            
        Returns:
            Agent: The created agent
            
        Raises:
            ValueError: If an unknown agent type is specified
        """
        # Create service for agent
        service = SkAgentFactory.create_service()
        
        # Create the specified agent
        if agent_type == "chat":
            return ChatAgent(service=service)
        elif agent_type == "weather":
            return WeatherAgent(service=service)
        elif agent_type == "calculator":
            return CalculatorAgent(service=service)
        elif agent_type == "orchestrator":
            return OrchestratorAgent(service=service)
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")
    
    @staticmethod
    def create_all_agents():
        """
        Create all agent types.
        
        Returns:
            dict: Dictionary of all created agents
        """
        return {
            "chat": SkAgentFactory.create_agent("chat"),
            "weather": SkAgentFactory.create_agent("weather"),
            "calculator": SkAgentFactory.create_agent("calculator"),
            "orchestrator": SkAgentFactory.create_agent("orchestrator")
        }