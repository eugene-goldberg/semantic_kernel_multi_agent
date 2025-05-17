#!/usr/bin/env python3
"""
Deployment manager for Semantic Kernel agents to Azure AI Service.
This handles the deployment of agents using the SK SDK.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
import semantic_kernel as sk
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from dotenv import load_dotenv

from src.config.agent_configs import AGENT_CONFIGS
from src.utils.sk_agent_factory import SkAgentFactory

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SkDeploymentSettings:
    """Settings for SK agent deployment"""
    
    def __init__(self):
        """Initialize deployment settings from environment"""
        # Load environment variables
        load_dotenv()
        
        # AI Service settings
        self.subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        self.resource_group = os.getenv("AZURE_RESOURCE_GROUP")
        self.ai_hub_name = os.getenv("AZURE_AI_HUB_NAME")
        self.ai_project_name = os.getenv("AZURE_AI_PROJECT_NAME", "sk-multi-agent-project")
        self.ai_project_host = os.getenv("AZURE_AI_PROJECT_HOST")
        self.ai_project_connection_string = os.getenv("AZURE_AI_PROJECT_CONNECTION_STRING")
        
        # Model name (not using Azure OpenAI directly)
        self.model_name = os.getenv("AI_MODEL_NAME", "gpt-35-turbo")
        
        # Validate required settings
        self._validate_settings()
    
    def _validate_settings(self):
        """Validate that all required settings are present"""
        # If connection string is provided, we don't need individual components
        if self.ai_project_connection_string:
            return
            
        # Otherwise, we need these individual settings
        required_vars = [
            "subscription_id", 
            "resource_group", 
            "ai_hub_name",
            "ai_project_name"
        ]
        
        missing_vars = [var for var in required_vars if not getattr(self, var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

class SkDeploymentManager:
    """Manager for deploying SK agents to Azure AI Service"""
    
    @staticmethod
    async def _create_project_client(settings: SkDeploymentSettings) -> AIProjectClient:
        """
        Create an Azure AI Project client using settings.
        
        Args:
            settings: Deployment settings with connection information
            
        Returns:
            AIProjectClient: Configured client for Azure AI Service
        """
        credential = DefaultAzureCredential()
        
        try:
            # First try using connection string if available
            if settings.ai_project_connection_string:
                logger.info("Using connection string to create AI Project client")
                return AIProjectClient.from_connection_string(
                    connection_string=settings.ai_project_connection_string,
                    credential=credential
                )
            
            # Otherwise construct connection string from components
            logger.info(f"Creating client for Hub '{settings.ai_hub_name}', Project '{settings.ai_project_name}'")
            
            if not (settings.subscription_id and settings.resource_group and 
                    settings.ai_hub_name and settings.ai_project_name):
                raise ValueError("Incomplete connection information. Provide either connection string or all required components.")
            
            # Determine host if not provided
            host = settings.ai_project_host
            if not host:
                # Use default format if not provided
                region = "westus"  # Default region
                host = f"{region}.ai.projects.azure.com"
            
            # Construct connection string manually
            connection_string = (f"{host};{settings.subscription_id};{settings.resource_group};" 
                                f"{settings.ai_hub_name}/{settings.ai_project_name}")
            
            return AIProjectClient.from_connection_string(
                connection_string=connection_string,
                credential=credential
            )
            
        except Exception as e:
            logger.error(f"Failed to create AI Project client: {str(e)}")
            raise
    
    @staticmethod
    async def deploy_agent(agent_type: str, settings: Optional[SkDeploymentSettings] = None) -> Dict[str, Any]:
        """
        Deploy a single agent to Azure AI Service.
        
        Args:
            agent_type: Type of agent to deploy ('chat', 'weather', 'calculator', 'orchestrator')
            settings: Optional deployment settings
            
        Returns:
            Dict containing deployment information
        """
        if settings is None:
            settings = SkDeploymentSettings()
        
        logger.info(f"Deploying {agent_type} agent to Azure AI Service...")
        
        # Get agent configuration
        if agent_type not in AGENT_CONFIGS:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        config = AGENT_CONFIGS[agent_type]
        
        try:
            # Create Azure AI Project client
            credential = DefaultAzureCredential()
            client = await SkDeploymentManager._create_project_client(settings)
            
            # Get instruction text from config
            instructions = config["instructions"]
            name = config["name"]
            model = config["deployment_model"]
            
            # Define any tools based on plugins
            tools = []
            if agent_type == "weather" or agent_type == "orchestrator":
                # Add weather tool definition
                weather_tool = {
                    "type": "function",
                    "function": {
                        "name": "GetWeather",
                        "description": "Get weather information for a US location",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "location": {
                                    "type": "string",
                                    "description": "The city and state, e.g. Seattle, WA"
                                },
                                "type": {
                                    "type": "string",
                                    "enum": ["current", "forecast"],
                                    "description": "The type of weather information to retrieve"
                                }
                            },
                            "required": ["location"]
                        }
                    }
                }
                tools.append(weather_tool)
                
            if agent_type == "calculator" or agent_type == "orchestrator":
                # Add calculator tool definition
                calculator_tool = {
                    "type": "function",
                    "function": {
                        "name": "Calculate",
                        "description": "Perform a mathematical calculation",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "expression": {
                                    "type": "string",
                                    "description": "The mathematical expression to evaluate"
                                }
                            },
                            "required": ["expression"]
                        }
                    }
                }
                tools.append(calculator_tool)
            
            # Deploy agent to Azure AI Service
            logger.info(f"Creating agent '{name}' with model '{model}'...")
            
            agent_definition = await client.agents.create_agent(
                model=model,
                name=name,
                instructions=instructions,
                tools=tools if tools else None
            )
            
            logger.info(f"Successfully deployed {agent_type} agent with ID: {agent_definition.id}")
            
            return {
                "agent_type": agent_type,
                "agent_id": agent_definition.id,
                "name": name,
                "host": settings.ai_project_host or "azure.ai.service"
            }
            
        except Exception as e:
            logger.error(f"Error deploying {agent_type} agent: {str(e)}")
            raise
    
    @staticmethod
    async def deploy_all_agents(settings: Optional[SkDeploymentSettings] = None) -> Dict[str, Dict[str, Any]]:
        """
        Deploy all agents to Azure AI Service.
        
        Args:
            settings: Optional deployment settings
            
        Returns:
            Dict mapping agent types to their deployment information
        """
        if settings is None:
            settings = SkDeploymentSettings()
        
        logger.info("Deploying all agents to Azure...")
        
        # Deploy each agent type
        deployments = {}
        
        for agent_type in AGENT_CONFIGS.keys():
            try:
                deployment = await SkDeploymentManager.deploy_agent(agent_type, settings)
                deployments[agent_type] = deployment
            except Exception as e:
                logger.error(f"Error deploying {agent_type} agent: {str(e)}")
                # Continue with other agents even if one fails
        
        return deployments
    
    @staticmethod
    def save_deployment_info(deployments: Dict[str, Dict[str, Any]], file_path: str = "sk_deployment_info.json"):
        """
        Save deployment information to a file.
        
        Args:
            deployments: Deployment information from deploy_all_agents
            file_path: Path to save the information to
        """
        # Format deployment info for storage
        first_agent = next(iter(deployments.values()))
        
        info = {
            "project_host": first_agent["host"],
            "project_name": "sk-multi-agent-project"
        }
        
        # Add agent IDs
        for agent_type, deployment in deployments.items():
            info[f"{agent_type}_agent_id"] = deployment["agent_id"]
        
        # Save to file
        with open(file_path, "w") as f:
            json.dump(info, f, indent=2)
        
        logger.info(f"Deployment information saved to {file_path}")
        
        # Also save to orchestration_deployment_info.json for compatibility
        with open("orchestration_deployment_info.json", "w") as f:
            json.dump(info, f, indent=2)
        logger.info(f"Deployment information also saved to orchestration_deployment_info.json")
        
        return info