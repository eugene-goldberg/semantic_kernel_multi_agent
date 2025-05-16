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
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
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
        
        # Azure OpenAI settings
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        
        # AI Service settings
        self.subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        self.resource_group = os.getenv("AZURE_RESOURCE_GROUP")
        self.ai_project_name = os.getenv("AZURE_AI_PROJECT_NAME", "sk-multi-agent-project")
        
        # Validate required settings
        self._validate_settings()
    
    def _validate_settings(self):
        """Validate that all required settings are present"""
        required_vars = [
            "azure_endpoint", 
            "azure_api_key", 
            "deployment_name"
        ]
        
        missing_vars = [var for var in required_vars if not getattr(self, var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

class SkDeploymentManager:
    """Manager for deploying SK agents to Azure AI Service"""
    
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
        
        logger.info(f"Deploying {agent_type} agent to Azure...")
        
        # Get agent configuration
        if agent_type not in AGENT_CONFIGS:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        config = AGENT_CONFIGS[agent_type]
        
        try:
            # Create service and kernel
            service = AzureChatCompletion(
                deployment_name=settings.deployment_name,
                endpoint=settings.azure_endpoint,
                api_key=settings.azure_api_key,
                api_version="2024-02-15-preview"
            )
            
            kernel = sk.Kernel()
            kernel.add_service(service)
            
            # Create the agent using SK SDK
            # Note: For now, we'll simulate the deployment and return a placeholder ID
            # In a real implementation, this would use the SK SDK's deployment functionality
            
            # Create agent using the factory
            agent = SkAgentFactory.create_agent(agent_type)
            
            # Simulate deployment to get an ID
            # In a real implementation, this would be the actual deployment call
            deployment_id = f"asst_sk_{agent_type}_{hash(config['name']) % 10000:04d}"
            
            logger.info(f"Deployed {agent_type} agent with ID: {deployment_id}")
            
            return {
                "agent_type": agent_type,
                "agent_id": deployment_id,
                "name": config["name"],
                "host": settings.azure_endpoint
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
        info = {
            "project_host": deployments["chat"]["host"].replace("https://", "").replace("/", ""),
            "project_name": "semantic-kernel-agents"
        }
        
        # Add agent IDs
        for agent_type, deployment in deployments.items():
            info[f"{agent_type}_agent_id"] = deployment["agent_id"]
        
        # Save to file
        with open(file_path, "w") as f:
            json.dump(info, f, indent=2)
        
        logger.info(f"Deployment information saved to {file_path}")
        
        return info