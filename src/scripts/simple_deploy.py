#!/usr/bin/env python3
import asyncio
import os
import sys
import json

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from src.config.settings import (
    AZURE_AI_PROJECT_NAME, 
    AZURE_RESOURCE_GROUP, 
    AZURE_SUBSCRIPTION_ID,
    AZURE_AI_PROJECT_HOST
)

async def deploy_simple_agent():
    """
    Deploy a simple agent to Azure AI Agent Service using the API directly
    rather than the Semantic Kernel integration
    """
    try:
        print("Connecting to Azure AI Foundry...")
        
        # Construct full endpoint URL
        endpoint = f"https://{AZURE_AI_PROJECT_HOST}"
        print(f"Using endpoint: {endpoint}")
        
        credential = DefaultAzureCredential()
        
        # Initialize the client directly with project details
        client = AIProjectClient(
            endpoint=endpoint,
            subscription_id=AZURE_SUBSCRIPTION_ID,
            resource_group=AZURE_RESOURCE_GROUP,
            workspace_name=AZURE_AI_PROJECT_NAME,
            credential=credential
        )
        
        print(f"Connected to Project: {AZURE_AI_PROJECT_NAME}")
        
        print("Creating Chat Agent...")
        chat_agent = await client.agents.create_agent(
            model="gpt-35-turbo",
            name="ChatAgent",
            instructions=(
                "You are a helpful assistant that provides friendly, concise, and accurate information. "
                "You should be conversational but prioritize accuracy and brevity over verbosity. "
                "If you don't know something, admit it clearly rather than making guesses."
            )
        )
        
        print("Creating Weather Agent...")
        weather_agent = await client.agents.create_agent(
            model="gpt-35-turbo",
            name="WeatherAgent",
            instructions=(
                "You are a weather specialist agent that provides accurate and helpful weather information "
                "for locations in the United States. "
                "You have access to real-time US weather data through the National Weather Service API. "
                "Provide your answers in a friendly, concise manner, focusing on the most relevant information. "
                "If asked about weather outside the United States, politely explain that your weather data "
                "is currently limited to US locations only."
            )
        )
        
        # Create a deployment info file for future reference
        deployment_info = {
            "chat_agent_id": chat_agent.id,
            "weather_agent_id": weather_agent.id
        }
        
        # Save deployment info to file
        with open("deployment_info.json", "w") as f:
            json.dump(deployment_info, f, indent=2)
        
        print("\nDeployment complete!")
        print(f"Chat Agent ID: {chat_agent.id}")
        print(f"Weather Agent ID: {weather_agent.id}")
        print("\nDeployment info saved to deployment_info.json")
        
    except Exception as e:
        print(f"Error during deployment: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(deploy_simple_agent())