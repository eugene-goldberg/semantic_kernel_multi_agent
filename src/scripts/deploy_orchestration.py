#!/usr/bin/env python3
"""
Deploy agents with orchestration capabilities - the Chat Agent can delegate to the Weather Agent.
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
    
    # Check required variables
    if not all([AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT_NAME]):
        raise ValueError("Missing required environment variables for Azure OpenAI")
    
    try:
        # Initialize OpenAI client
        client = AzureOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            api_version="2024-05-01-preview"
        )
        return client
    except Exception as e:
        print(f"Error creating Azure OpenAI client: {str(e)}")
        raise

def create_weather_function_tool():
    """Create a function definition for the weather tool"""
    return {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather information for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA or New York, NY"
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

def list_existing_assistants(client):
    """List existing assistants"""
    try:
        print("Checking for existing assistants...")
        assistants = client.beta.assistants.list(limit=100)
        
        if len(assistants.data) > 0:
            print(f"Found {len(assistants.data)} existing assistants:")
            for assistant in assistants.data:
                print(f"  - {assistant.name} (ID: {assistant.id})")
                
            # Ask if we should remove existing assistants
            if input("Do you want to remove existing assistants? (y/n): ").lower() == 'y':
                for assistant in assistants.data:
                    print(f"Deleting assistant: {assistant.name}...")
                    client.beta.assistants.delete(assistant.id)
                print("All existing assistants deleted.")
        else:
            print("No existing assistants found.")
    except Exception as e:
        print(f"Error listing assistants: {str(e)}")

def create_weather_assistant(client, model_name):
    """Create a weather specialist assistant"""
    try:
        print(f"Creating WeatherAgent with model {model_name}...")
        
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
        
        assistant = client.beta.assistants.create(
            name="WeatherAgent",
            instructions=weather_instructions,
            model=model_name,
            tools=[]  # No API tools yet, but could be added later
        )
        
        print(f"WeatherAgent created successfully with ID: {assistant.id}")
        return assistant.id
    except Exception as e:
        print(f"Error creating weather assistant: {str(e)}")
        return None

def create_orchestrator_agent(client, model_name, weather_agent_id):
    """Create an orchestrator agent that can delegate to the weather agent"""
    try:
        print(f"Creating OrchestratorAgent with model {model_name}...")
        
        # Create a function tool for weather queries
        weather_tool = create_weather_function_tool()
        
        orchestrator_instructions = (
            "You are a helpful assistant that provides friendly, concise, and accurate information. "
            "You should be conversational but prioritize accuracy and brevity over verbosity. "
            "If you don't know something, admit it clearly rather than making guesses.\n\n"
            
            f"When the user asks about weather, use the get_weather function to delegate to the weather specialist agent. "
            f"The weather agent has ID {weather_agent_id} and specializes in providing accurate weather information "
            f"for locations in the United States.\n\n"
            
            "Always extract the location from the user's question when dealing with weather queries. "
            "For example, if they ask 'What's the weather like in Seattle?', you should call get_weather with location='Seattle, WA'.\n\n"
            
            "For weather forecasts, set type='forecast', and for current weather, set type='current'."
        )
        
        assistant = client.beta.assistants.create(
            name="OrchestratorAgent",
            instructions=orchestrator_instructions,
            model=model_name,
            tools=[weather_tool]
        )
        
        print(f"OrchestratorAgent created successfully with ID: {assistant.id}")
        return assistant.id
    except Exception as e:
        print(f"Error creating orchestrator agent: {str(e)}")
        return None

def main():
    """Main deployment function"""
    try:
        # Get OpenAI client
        client = get_openai_client()
        
        # List existing assistants
        list_existing_assistants(client)
        
        # Create weather assistant first
        weather_agent_id = create_weather_assistant(client, AZURE_OPENAI_DEPLOYMENT_NAME)
        
        # Create orchestrator agent that can delegate to the weather agent
        orchestrator_agent_id = create_orchestrator_agent(client, AZURE_OPENAI_DEPLOYMENT_NAME, weather_agent_id)
        
        # Save deployment info
        if orchestrator_agent_id and weather_agent_id:
            deployment_info = {
                "orchestrator_agent_id": orchestrator_agent_id,
                "weather_agent_id": weather_agent_id,
                "project_host": AZURE_OPENAI_ENDPOINT.replace("https://", "").replace("/", ""),
                "project_name": "azure-openai-assistants"
            }
            
            with open("orchestration_deployment_info.json", "w") as f:
                json.dump(deployment_info, f, indent=2)
            
            print("\nDeployment info saved to orchestration_deployment_info.json")
            print("\nTo interact with the orchestrated agents, run:")
            print("python3 src/scripts/interact_orchestrated_agents.py")
        else:
            print("Failed to deploy one or both agents.")
            
    except Exception as e:
        print(f"Error during deployment: {str(e)}")

if __name__ == "__main__":
    main()