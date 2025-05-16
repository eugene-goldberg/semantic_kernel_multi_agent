#!/usr/bin/env python3
"""
Deploy agents as OpenAI Assistants directly using the Azure OpenAI API.
This leverages the 'assistants' capability of the gpt-35-turbo deployment.
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
    
    # Set environment variables from .env.deploy file
    with open(".env.deploy", "r") as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ[key] = value
                
    # Check required variables
    if not all([os.getenv("AZURE_OPENAI_ENDPOINT"), os.getenv("AZURE_OPENAI_API_KEY"), os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")]):
        raise ValueError("Missing required environment variables for Azure OpenAI")
    
    try:
        # Initialize OpenAI client
        client = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-02-15-preview"  # Use version that works for Azure
        )
        print(f"Successfully connected to Azure OpenAI at {os.getenv('AZURE_OPENAI_ENDPOINT')}")
        return client
    except Exception as e:
        print(f"Error creating Azure OpenAI client: {str(e)}")
        print(f"ENDPOINT: {os.getenv('AZURE_OPENAI_ENDPOINT')}")
        print(f"DEPLOYMENT: {os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')}")
        print(f"API KEY: {os.getenv('AZURE_OPENAI_API_KEY')[:5]}...")
        raise

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

def create_chat_assistant(client, model_name):
    """Create a general chat assistant"""
    try:
        print(f"Creating ChatAgent with model {model_name}...")
        
        chat_instructions = (
            "You are a helpful assistant that provides friendly, concise, and accurate information. "
            "You should be conversational but prioritize accuracy and brevity over verbosity. "
            "If you don't know something, admit it clearly rather than making guesses."
        )
        
        assistant = client.beta.assistants.create(
            name="ChatAgent",
            instructions=chat_instructions,
            model=model_name,
            tools=[]  # No special tools for chat agent
        )
        
        print(f"ChatAgent created successfully with ID: {assistant.id}")
        return assistant.id
    except Exception as e:
        print(f"Error creating chat assistant: {str(e)}")
        return None

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

def main():
    """Main deployment function"""
    try:
        # Get OpenAI client
        client = get_openai_client()
        
        # List existing assistants
        list_existing_assistants(client)
        
        # Create chat assistant
        chat_agent_id = create_chat_assistant(client, AZURE_OPENAI_DEPLOYMENT_NAME)
        
        # Create weather assistant
        weather_agent_id = create_weather_assistant(client, AZURE_OPENAI_DEPLOYMENT_NAME)
        
        # Save deployment info
        if chat_agent_id or weather_agent_id:
            deployment_info = {
                "chat_agent_id": chat_agent_id,
                "weather_agent_id": weather_agent_id,
                "project_host": AZURE_OPENAI_ENDPOINT.replace("https://", "").replace("/", ""),
                "project_name": "azure-openai-assistants"
            }
            
            with open("deployment_info.json", "w") as f:
                json.dump(deployment_info, f, indent=2)
            
            print("\nDeployment info saved to deployment_info.json")
            print("\nTo interact with the deployed assistants, run:")
            print("python3 src/scripts/interact_openai_assistants.py")
        else:
            print("Failed to deploy one or both assistants.")
            
    except Exception as e:
        print(f"Error during deployment: {str(e)}")

if __name__ == "__main__":
    main()