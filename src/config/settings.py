import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

# Azure AI Foundry Configuration
AZURE_AI_HUB_NAME = os.getenv("AZURE_AI_HUB_NAME")
AZURE_AI_PROJECT_NAME = os.getenv("AZURE_AI_PROJECT_NAME")
AZURE_AI_PROJECT_HOST = os.getenv("AZURE_AI_PROJECT_HOST")
AZURE_SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID")
AZURE_RESOURCE_GROUP = os.getenv("AZURE_RESOURCE_GROUP")
AZURE_AI_PROJECT_CONNECTION_STRING = os.getenv("AZURE_AI_PROJECT_CONNECTION_STRING")

# Weather API Configuration
# Using National Weather Service API which doesn't require API key
# This service only provides weather data for locations in the United States

def get_project_connection_string():
    """
    Get the Azure AI Project connection string.
    
    Returns:
        str: The connection string, either directly from env var or constructed from components
    """
    if AZURE_AI_PROJECT_CONNECTION_STRING:
        return AZURE_AI_PROJECT_CONNECTION_STRING
    
    # If no connection string provided, construct from components
    if (AZURE_AI_PROJECT_HOST and AZURE_SUBSCRIPTION_ID and 
        AZURE_RESOURCE_GROUP and AZURE_AI_PROJECT_NAME and AZURE_AI_HUB_NAME):
        # Format: <HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>/<ProjectName>
        return f"{AZURE_AI_PROJECT_HOST};{AZURE_SUBSCRIPTION_ID};{AZURE_RESOURCE_GROUP};{AZURE_AI_HUB_NAME}/{AZURE_AI_PROJECT_NAME}"
    
    raise ValueError("Azure AI Project connection information is missing. Please provide either AZURE_AI_PROJECT_CONNECTION_STRING or all required components including Hub name.")