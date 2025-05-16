#!/usr/bin/env python3
"""
Deploy agents to Azure AI Agent Service using the Azure AI Projects SDK.
This script provides a command-line interface for deploying agents.
"""

import os
import sys
import argparse
import json
from azure.ai.projects import AIProjectClient
from azure.ai.agents import AgentsClient
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from dotenv import load_dotenv

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from src.config.settings import (
    AZURE_OPENAI_DEPLOYMENT_NAME,
    AZURE_AI_PROJECT_NAME, 
    AZURE_RESOURCE_GROUP, 
    AZURE_SUBSCRIPTION_ID,
    AZURE_AI_PROJECT_HOST,
    get_project_connection_string
)

def deploy_agent(
    endpoint: str,
    agent_name: str,
    agent_instructions: str,
    model_deployment_name: str,
    use_service_principal: bool = False
):
    """
    Deploy a single agent to Azure AI Agent Service
    
    Args:
        endpoint: The Azure AI Agent Service endpoint
        agent_name: Name of the agent to create
        agent_instructions: Instructions for the agent
        model_deployment_name: Name of the Azure OpenAI model deployment
        use_service_principal: Whether to use service principal authentication
    """
    try:
        # Choose authentication method
        if use_service_principal and all([
            os.getenv("AZURE_CLIENT_ID"),
            os.getenv("AZURE_CLIENT_SECRET"),
            os.getenv("AZURE_TENANT_ID")
        ]):
            print(f"Using Service Principal authentication for {agent_name}...")
            credential = ClientSecretCredential(
                tenant_id=os.getenv("AZURE_TENANT_ID"),
                client_id=os.getenv("AZURE_CLIENT_ID"),
                client_secret=os.getenv("AZURE_CLIENT_SECRET")
            )
        else:
            print(f"Using Default Azure authentication for {agent_name}...")
            credential = DefaultAzureCredential()
        
        # Create Agents client
        print(f"Connecting to Azure AI Agent Service at: {endpoint}")
        agents_client = AgentsClient(endpoint=endpoint, credential=credential)
        
        # Deploy agent
        print(f"Creating/updating agent '{agent_name}'...")
        created_agent = agents_client.create_agent(
            model=model_deployment_name,
            name=agent_name,
            instructions=agent_instructions
        )
        
        print(f"Agent '{created_agent.get('name')}' successfully created with ID: {created_agent.get('id')}")
        return created_agent.get("id")
        
    except Exception as e:
        print(f"Error deploying agent '{agent_name}': {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def deploy_agents(args):
    """Deploy both chat and weather agents"""
    endpoint = args.endpoint or f"https://{AZURE_AI_PROJECT_HOST}/"
    model_deployment = args.model_deployment or AZURE_OPENAI_DEPLOYMENT_NAME
    
    # Print deployment information
    print("Deploying agents with the following configuration:")
    print(f"  Endpoint: {endpoint}")
    print(f"  Model Deployment: {model_deployment}")
    print(f"  Authentication: {'Service Principal' if args.use_service_principal else 'Default Azure'}")
    
    # Deploy Chat Agent
    chat_instructions = (
        "You are a helpful assistant that provides friendly, concise, and accurate information. "
        "You should be conversational but prioritize accuracy and brevity over verbosity. "
        "If you don't know something, admit it clearly rather than making guesses."
    )
    
    chat_id = deploy_agent(
        endpoint=endpoint,
        agent_name="ChatAgent",
        agent_instructions=chat_instructions,
        model_deployment_name=model_deployment,
        use_service_principal=args.use_service_principal
    )
    
    # Deploy Weather Agent
    weather_instructions = (
        "You are a weather specialist agent that provides accurate and helpful weather information "
        "for locations in the United States. "
        "You have access to real-time US weather data through the National Weather Service API. "
        "When asked about weather, use the coordinates of the city to get accurate data. "
        "For example, Seattle is at 47.6062, -122.3321. New York is at 40.7128, -74.0060. "
        "Provide your answers in a friendly, concise manner, focusing on the most relevant information. "
        "If asked about weather outside the United States, politely explain that your weather data "
        "is currently limited to US locations only."
    )
    
    weather_id = deploy_agent(
        endpoint=endpoint,
        agent_name="WeatherAgent",
        agent_instructions=weather_instructions,
        model_deployment_name=model_deployment,
        use_service_principal=args.use_service_principal
    )
    
    # Save deployment info
    if chat_id or weather_id:
        deployment_info = {
            "chat_agent_id": chat_id,
            "weather_agent_id": weather_id,
            "project_host": AZURE_AI_PROJECT_HOST,
            "project_name": AZURE_AI_PROJECT_NAME
        }
        
        with open("deployment_info.json", "w") as f:
            json.dump(deployment_info, f, indent=2)
        
        print("\nDeployment info saved to deployment_info.json")
        print("\nYou can now interact with your agents using:")
        print("python3 src/scripts/interact_deployed_agents.py")

def main():
    """Main entry point with argument parsing"""
    # Load environment variables
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Deploy agents to Azure AI Agent Service")
    parser.add_argument("--endpoint", type=str, help="Azure AI Agent Service endpoint")
    parser.add_argument("--model-deployment", type=str, help="Azure OpenAI model deployment name")
    parser.add_argument("--use-service-principal", action="store_true", help="Use Service Principal authentication")
    
    args = parser.parse_args()
    deploy_agents(args)

if __name__ == "__main__":
    main()