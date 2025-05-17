#!/usr/bin/env python3
"""
Deploy and set up remote orchestration using Azure OpenAI Assistants.
This script creates an orchestrator agent that can delegate to specialized agents.
"""

import os
import sys
import json
from openai import AzureOpenAI
from dotenv import load_dotenv

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from src.config.settings import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_DEPLOYMENT_NAME
)

def get_openai_client():
    """Get the Azure OpenAI client"""
    # Load environment variables
    load_dotenv()
    
    # Try to load from .env.deploy if it exists, but don't fail if it doesn't
    try:
        if os.path.exists(".env.deploy"):
            with open(".env.deploy", "r") as f:
                for line in f:
                    if line.strip() and not line.startswith("#"):
                        key, value = line.strip().split("=", 1)
                        os.environ[key] = value
    except Exception as e:
        print(f"Note: Could not load .env.deploy: {str(e)}. Using environment variables instead.")
    
    # Check required variables
    if not all([AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT_NAME]):
        raise ValueError("Missing required environment variables for Azure OpenAI")
    
    try:
        # Initialize OpenAI client
        client = AzureOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            api_version="2024-02-15-preview"  # Use version that works with Azure
        )
        print(f"Successfully connected to Azure OpenAI at {AZURE_OPENAI_ENDPOINT}")
        return client
    except Exception as e:
        print(f"Error creating Azure OpenAI client: {str(e)}")
        print(f"ENDPOINT: {AZURE_OPENAI_ENDPOINT}")
        print(f"DEPLOYMENT: {AZURE_OPENAI_DEPLOYMENT_NAME}")
        print(f"API KEY: {AZURE_OPENAI_API_KEY[:5]}...")
        raise

def load_existing_agents():
    """Load existing agent IDs from deployment_info.json"""
    try:
        with open("deployment_info.json", "r") as f:
            deployment_info = json.load(f)
        
        chat_agent_id = deployment_info.get("chat_agent_id")
        weather_agent_id = deployment_info.get("weather_agent_id")
        calculator_agent_id = deployment_info.get("calculator_agent_id")
        
        if not chat_agent_id or not weather_agent_id:
            print("Missing required agent IDs in deployment_info.json")
            return None, None, None
        
        print(f"Loaded agent IDs: Chat={chat_agent_id}, Weather={weather_agent_id}, Calculator={calculator_agent_id or 'Not found'}")
        return chat_agent_id, weather_agent_id, calculator_agent_id
    except Exception as e:
        print(f"Error loading deployment info: {str(e)}")
        return None, None, None

def create_orchestrator_agent(client, model_name, chat_agent_id, weather_agent_id, calculator_agent_id=None):
    """Create an orchestrator agent that delegates to specialized agents"""
    try:
        print(f"Creating OrchestratorAgent with model {model_name}...")
        
        # Prepare instructions based on available agents
        if calculator_agent_id:
            # Define orchestrator instructions with calculator agent
            orchestrator_instructions = """
            You are an orchestrator agent that intelligently routes user requests to specialized agents
            based on the content of the request.

            Available Agents:
            1. Chat Agent (asst_{0}) - For general questions and conversation
            2. Weather Agent (asst_{1}) - For weather-related questions
            3. Calculator Agent (asst_{2}) - For mathematical calculations and operations

            When a user sends a request:
            1. Analyze the content of the request
            2. Determine which agent is best suited to handle it:
               - Weather Agent for questions about weather, forecasts, temperature, etc.
               - Calculator Agent for mathematical calculations, equations, matrices, statistics, etc.
               - Chat Agent for general questions or if uncertain
            3. Provide your routing decision and explain why

            Example routing:
            - User: "What's the weather like in Seattle?" -> Weather Agent
            - User: "Calculate the determinant of [[1,2],[3,4]]" -> Calculator Agent
            - User: "Solve the equation 2x^2 + 5x - 3 = 0" -> Calculator Agent
            - User: "Tell me about quantum physics" -> Chat Agent
            
            Always make a clear decision and briefly explain your reasoning.
            """.format(chat_agent_id, weather_agent_id, calculator_agent_id)
        else:
            # Original instructions without calculator agent
            orchestrator_instructions = """
            You are an orchestrator agent that intelligently routes user requests to specialized agents
            based on the content of the request.

            Available Agents:
            1. Chat Agent (asst_{0}) - For general questions and conversation
            2. Weather Agent (asst_{1}) - For weather-related questions

            When a user sends a request:
            1. Analyze the content of the request
            2. Determine which agent is best suited to handle it:
               - Weather Agent for questions about weather, forecasts, temperature, etc.
               - Chat Agent for general questions or if uncertain
            3. Provide your routing decision and explain why

            Example routing:
            - User: "What's the weather like in Seattle?" -> Weather Agent
            - User: "Tell me about quantum physics" -> Chat Agent
            
            Always make a clear decision and briefly explain your reasoning.
            """.format(chat_agent_id, weather_agent_id)
        
        # Create the orchestrator assistant
        assistant = client.beta.assistants.create(
            name="OrchestratorAgent",
            instructions=orchestrator_instructions,
            model=model_name,
            tools=[]  # No special tools for orchestrator
        )
        
        print(f"OrchestratorAgent created successfully with ID: {assistant.id}")
        return assistant.id
    except Exception as e:
        print(f"Error creating orchestrator assistant: {str(e)}")
        return None

def save_deployment_info(chat_agent_id, weather_agent_id, orchestrator_id, calculator_agent_id=None):
    """Save deployment information to a file"""
    try:
        deployment_info = {
            "chat_agent_id": chat_agent_id,
            "weather_agent_id": weather_agent_id,
            "orchestrator_agent_id": orchestrator_id,
            "project_host": AZURE_OPENAI_ENDPOINT.replace("https://", "").replace("/", ""),
            "project_name": "azure-openai-assistants"
        }
        
        # Add calculator agent ID if it exists
        if calculator_agent_id:
            deployment_info["calculator_agent_id"] = calculator_agent_id
        
        with open("orchestration_deployment_info.json", "w") as f:
            json.dump(deployment_info, f, indent=2)
        
        print("\nDeployment info saved to orchestration_deployment_info.json")
    except Exception as e:
        print(f"Error saving deployment info: {str(e)}")

def main():
    """Main deployment function"""
    try:
        # Get OpenAI client
        client = get_openai_client()
        
        # Load existing agents
        chat_agent_id, weather_agent_id, calculator_agent_id = load_existing_agents()
        
        if not chat_agent_id or not weather_agent_id:
            print("Failed to load required agent IDs")
            return
        
        # Create orchestrator agent with all available agents
        orchestrator_id = create_orchestrator_agent(
            client, 
            AZURE_OPENAI_DEPLOYMENT_NAME,
            chat_agent_id, 
            weather_agent_id,
            calculator_agent_id
        )
        
        if not orchestrator_id:
            print("Failed to create orchestrator agent")
            return
        
        # Save deployment info with all available agents
        save_deployment_info(chat_agent_id, weather_agent_id, orchestrator_id, calculator_agent_id)
        
        print("\nOrchestration deployment complete!")
        if calculator_agent_id:
            print("Orchestrator includes Calculator Agent capabilities!")
        print("\nTo interact with the deployed orchestration system, run:")
        print("python3 src/scripts/interact_orchestrated_agents.py")
    except Exception as e:
        print(f"Error during deployment: {str(e)}")

if __name__ == "__main__":
    main()