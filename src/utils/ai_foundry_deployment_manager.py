#!/usr/bin/env python3
"""
Deployment manager for Semantic Kernel agents to Azure AI Foundry.
This handles the deployment of agents using the Azure AI Foundry REST API.
"""

import os
import json
import logging
import aiohttp
import subprocess
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

from src.config.agent_configs import AGENT_CONFIGS

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AiFoundrySettings:
    """Settings for Azure AI Foundry agent deployment"""
    
    def __init__(self):
        """Initialize deployment settings from environment"""
        # Load environment variables
        load_dotenv()
        load_dotenv('.env.ai_foundry')
        
        # Azure Resources
        self.subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        self.resource_group = os.getenv("AZURE_RESOURCE_GROUP")
        self.workspace_name = os.getenv("AZURE_WORKSPACE_NAME")
        self.region = os.getenv("AZURE_REGION", "westus")
        
        # API Configuration
        self.api_version = os.getenv("AI_FOUNDRY_API_VERSION", "2024-12-01-preview")
        
        # Model configuration
        self.model_name = os.getenv("AI_MODEL_NAME", "gpt-35-turbo")
        
        # Validate required settings
        self._validate_settings()
    
    def _validate_settings(self):
        """Validate that all required settings are present"""
        required_vars = [
            "subscription_id", 
            "resource_group", 
            "workspace_name"
        ]
        
        missing_vars = [var for var in required_vars if not getattr(self, var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    def get_base_url(self) -> str:
        """Get the base URL for the Azure AI Foundry API"""
        return f"https://{self.region}.api.azureml.ms/agents/v1.0/subscriptions/{self.subscription_id}/resourceGroups/{self.resource_group}/providers/Microsoft.MachineLearningServices/workspaces/{self.workspace_name}"

class AiFoundryDeploymentManager:
    """Manager for deploying agents to Azure AI Foundry"""
    
    @staticmethod
    async def _get_access_token() -> str:
        """
        Get an Azure AD access token using the Azure CLI.
        
        Returns:
            str: The access token
        """
        try:
            result = subprocess.run(
                ["az", "account", "get-access-token", "--query", "accessToken", "-o", "tsv"],
                capture_output=True,
                text=True,
                check=True
            )
            token = result.stdout.strip()
            return token
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get access token: {e.stderr}")
            raise
    
    @staticmethod
    async def deploy_agent(agent_type: str, settings: Optional[AiFoundrySettings] = None) -> Dict[str, Any]:
        """
        Deploy a single agent to Azure AI Foundry.
        
        Args:
            agent_type: Type of agent to deploy ('chat', 'weather', 'calculator', 'orchestrator')
            settings: Optional deployment settings
            
        Returns:
            Dict containing deployment information
        """
        if settings is None:
            settings = AiFoundrySettings()
        
        logger.info(f"Deploying {agent_type} agent to Azure AI Foundry...")
        
        # Get agent configuration
        if agent_type not in AGENT_CONFIGS:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        config = AGENT_CONFIGS[agent_type]
        
        try:
            # Get access token
            token = await AiFoundryDeploymentManager._get_access_token()
            
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
            
            # Create the agent payload
            agent_payload = {
                "name": name,
                "instructions": instructions,
                "model": model
            }
            
            if tools:
                agent_payload["tools"] = tools
            
            # Set up HTTP headers
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # Generate API URL
            base_url = settings.get_base_url()
            url = f"{base_url}/assistants?api-version={settings.api_version}"
            
            logger.info(f"Creating agent '{name}' with model '{model}'...")
            logger.info(f"API URL: {url}")
            
            # Send the request to create the agent
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=agent_payload) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        logger.error(f"Error creating agent: {error_text}")
                        raise Exception(f"Failed to create agent: {response.status} - {error_text}")
                    
                    agent_data = await response.json()
                    agent_id = agent_data.get("id")
                    
                    if not agent_id:
                        logger.error(f"No agent ID returned: {agent_data}")
                        raise Exception("No agent ID returned from the API")
                    
                    logger.info(f"Successfully deployed {agent_type} agent with ID: {agent_id}")
                    
                    return {
                        "agent_type": agent_type,
                        "agent_id": agent_id,
                        "name": name,
                        "workspace": settings.workspace_name,
                        "resource_group": settings.resource_group
                    }
            
        except Exception as e:
            logger.error(f"Error deploying {agent_type} agent: {str(e)}")
            raise
    
    @staticmethod
    async def deploy_all_agents(settings: Optional[AiFoundrySettings] = None) -> Dict[str, Dict[str, Any]]:
        """
        Deploy all agents to Azure AI Foundry.
        
        Args:
            settings: Optional deployment settings
            
        Returns:
            Dict mapping agent types to their deployment information
        """
        if settings is None:
            settings = AiFoundrySettings()
        
        logger.info("Deploying all agents to Azure AI Foundry...")
        
        # Deploy each agent type
        deployments = {}
        
        for agent_type in AGENT_CONFIGS.keys():
            try:
                deployment = await AiFoundryDeploymentManager.deploy_agent(agent_type, settings)
                deployments[agent_type] = deployment
            except Exception as e:
                logger.error(f"Error deploying {agent_type} agent: {str(e)}")
                # Continue with other agents even if one fails
        
        return deployments
    
    @staticmethod
    def save_deployment_info(deployments: Dict[str, Dict[str, Any]], file_path: str = "ai_foundry_deployment_info.json"):
        """
        Save deployment information to a file.
        
        Args:
            deployments: Deployment information from deploy_all_agents
            file_path: Path to save the information to
        """
        # Check if deployments is empty
        if not deployments:
            logger.warning("No successful deployments to save")
            info = {
                "workspace": "unavailable",
                "deployment_status": "failed"
            }
        else:
            # Format deployment info for storage
            first_agent = next(iter(deployments.values()))
            
            info = {
                "workspace": first_agent.get("workspace", "unavailable"),
                "resource_group": first_agent.get("resource_group", "unavailable"),
                "deployment_status": "success"
            }
            
            # Add agent IDs
            for agent_type, deployment in deployments.items():
                info[f"{agent_type}_agent_id"] = deployment.get("agent_id", "deployment_failed")
        
        # Save to file
        with open(file_path, "w") as f:
            json.dump(info, f, indent=2)
        
        logger.info(f"Deployment information saved to {file_path}")
        
        # Also save to orchestration_deployment_info.json for compatibility
        with open("orchestration_deployment_info.json", "w") as f:
            json.dump(info, f, indent=2)
        logger.info(f"Deployment information also saved to orchestration_deployment_info.json")
        
        # Also save to sk_deployment_info.json for compatibility with existing scripts
        with open("sk_deployment_info.json", "w") as f:
            json.dump(info, f, indent=2)
        logger.info(f"Deployment information also saved to sk_deployment_info.json")
        
        return info