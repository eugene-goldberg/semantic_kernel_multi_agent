#!/usr/bin/env python3
"""
Deploy a Calculator Agent to Azure OpenAI as an Assistant.
This agent specializes in advanced mathematical calculations.
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

def create_calculator_assistant(client, model_name):
    """Create a calculator assistant for advanced mathematical operations"""
    try:
        print(f"Creating CalculatorAgent with model {model_name}...")
        
        calculator_instructions = """
        You are a specialized calculator agent that performs mathematical calculations.
        Your role is to:
        
        1. Perform basic arithmetic (addition, subtraction, multiplication, division)
        2. Calculate square roots, exponents, and other basic functions
        3. Solve simple equations
        4. Perform matrix calculations if needed
        5. Calculate statistical measures like mean, median, and standard deviation
        
        Always show your steps clearly and explain the process in simple terms.
        Respond promptly with accurate calculations.
        
        If asked about non-mathematical topics, politely explain that you specialize in calculations.
        """
        
        # Create the calculator assistant - no tools for simpler implementation
        assistant = client.beta.assistants.create(
            name="CalculatorAgent",
            instructions=calculator_instructions,
            model=model_name
        )
        
        print(f"CalculatorAgent created successfully with ID: {assistant.id}")
        return assistant.id
    except Exception as e:
        print(f"Error creating calculator assistant: {str(e)}")
        return None

def update_deployment_info(calculator_agent_id):
    """Update deployment information with the calculator agent ID"""
    try:
        # First check if we have existing deployment info
        if os.path.exists("deployment_info.json"):
            with open("deployment_info.json", "r") as f:
                deployment_info = json.load(f)
        else:
            deployment_info = {
                "project_host": AZURE_OPENAI_ENDPOINT.replace("https://", "").replace("/", ""),
                "project_name": "azure-openai-assistants"
            }
        
        # Add the calculator agent ID
        deployment_info["calculator_agent_id"] = calculator_agent_id
        
        # Save the updated deployment info
        with open("deployment_info.json", "w") as f:
            json.dump(deployment_info, f, indent=2)
        
        print(f"Calculator Agent ID saved to deployment_info.json")
        
        # Also update orchestration deployment info if it exists
        if os.path.exists("orchestration_deployment_info.json"):
            with open("orchestration_deployment_info.json", "r") as f:
                orchestration_info = json.load(f)
            
            # Add the calculator agent ID
            orchestration_info["calculator_agent_id"] = calculator_agent_id
            
            # Save the updated orchestration info
            with open("orchestration_deployment_info.json", "w") as f:
                json.dump(orchestration_info, f, indent=2)
            
            print(f"Calculator Agent ID also saved to orchestration_deployment_info.json")
            
    except Exception as e:
        print(f"Error updating deployment info: {str(e)}")

def main():
    """Main deployment function"""
    try:
        # Get OpenAI client
        client = get_openai_client()
        
        # Create calculator assistant
        calculator_agent_id = create_calculator_assistant(client, AZURE_OPENAI_DEPLOYMENT_NAME)
        
        if calculator_agent_id:
            # Update deployment info
            update_deployment_info(calculator_agent_id)
            
            print("\nCalculator Agent deployment complete!")
            print("\nTo interact with the deployed agents, run:")
            print("python3 src/scripts/interact_openai_assistants.py")
        else:
            print("Failed to deploy Calculator Agent.")
            
    except Exception as e:
        print(f"Error during deployment: {str(e)}")

if __name__ == "__main__":
    main()