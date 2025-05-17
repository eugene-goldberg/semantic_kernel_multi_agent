#!/bin/bash
# Setup script for Azure AI Service resources

# Exit on any error
set -e

# Load environment variables
if [ -f .env.ai_service ]; then
    source .env.ai_service
fi

# Set default names if not defined in environment
HUB_NAME=${AZURE_AI_HUB_NAME:-"sk-multi-agent-hub"}
PROJECT_NAME=${AZURE_AI_PROJECT_NAME:-"sk-multi-agent-project"}
RESOURCE_GROUP=${AZURE_RESOURCE_GROUP:-"sk-multi-agent-rg"}
LOCATION=${AZURE_LOCATION:-"westus"}

echo "=== Setting up Azure AI Service Resources ==="
echo "Hub Name: $HUB_NAME"
echo "Project Name: $PROJECT_NAME"
echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $LOCATION"

# Ensure user is logged in to Azure CLI
echo "Checking Azure login status..."
az account show >/dev/null 2>&1 || { 
    echo "You need to login to Azure. Running 'az login'..."
    az login
}

# Get subscription ID
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
echo "Using Subscription: $SUBSCRIPTION_ID"

# Create resource group if it doesn't exist
echo "Checking resource group..."
if ! az group show --name "$RESOURCE_GROUP" >/dev/null 2>&1; then
    echo "Creating resource group $RESOURCE_GROUP..."
    az group create --name "$RESOURCE_GROUP" --location "$LOCATION"
fi

# Create AI Hub if it doesn't exist
echo "Checking if AI Hub exists..."
if ! az resource show --resource-group "$RESOURCE_GROUP" --name "$HUB_NAME" --resource-type "Microsoft.MachineLearningServices/aigalleries" >/dev/null 2>&1; then
    echo "Creating AI Hub $HUB_NAME..."
    az resource create \
        --resource-group "$RESOURCE_GROUP" \
        --name "$HUB_NAME" \
        --resource-type "Microsoft.MachineLearningServices/aigalleries" \
        --location "$LOCATION" \
        --properties "{\"location\": \"$LOCATION\"}"
    
    echo "AI Hub creation initiated. This may take a few minutes..."
    # Wait for hub to be created
    sleep 30
fi

# Create AI Project if it doesn't exist
echo "Checking if AI Project exists..."
if ! az resource show --resource-group "$RESOURCE_GROUP" --name "$PROJECT_NAME" --resource-type "Microsoft.MachineLearningServices/aigalleries/aiprojects" --parent "aigalleries/$HUB_NAME" >/dev/null 2>&1; then
    echo "Creating AI Project $PROJECT_NAME..."
    az resource create \
        --resource-group "$RESOURCE_GROUP" \
        --name "$PROJECT_NAME" \
        --resource-type "Microsoft.MachineLearningServices/aigalleries/aiprojects" \
        --parent "aigalleries/$HUB_NAME" \
        --location "$LOCATION" \
        --properties "{\"location\": \"$LOCATION\", \"friendlyName\": \"$PROJECT_NAME\"}"
    
    echo "AI Project creation initiated. This may take a few minutes..."
    # Wait for project to be created
    sleep 30
fi

# Construct connection string
CONNECTION_STRING="$LOCATION.ai.projects.azure.com;$SUBSCRIPTION_ID;$RESOURCE_GROUP;$HUB_NAME/$PROJECT_NAME"
echo "Connection string: $CONNECTION_STRING"

# Update the .env file with new values
if [ -f .env ]; then
    # Backup the current .env file
    cp .env .env.bak
    
    # Remove any existing values we're going to set
    grep -v "AZURE_AI_" .env | grep -v "AZURE_SUBSCRIPTION_ID" | grep -v "AZURE_RESOURCE_GROUP" > .env.temp
    
    # Add new values
    echo "" >> .env.temp
    echo "# Azure AI Service Configuration" >> .env.temp
    echo "AZURE_AI_HUB_NAME=$HUB_NAME" >> .env.temp
    echo "AZURE_AI_PROJECT_NAME=$PROJECT_NAME" >> .env.temp
    echo "AZURE_SUBSCRIPTION_ID=$SUBSCRIPTION_ID" >> .env.temp
    echo "AZURE_RESOURCE_GROUP=$RESOURCE_GROUP" >> .env.temp
    echo "AZURE_AI_PROJECT_HOST=$LOCATION.ai.projects.azure.com" >> .env.temp
    echo "AZURE_AI_PROJECT_CONNECTION_STRING=$CONNECTION_STRING" >> .env.temp
    echo "AI_MODEL_NAME=gpt-35-turbo" >> .env.temp
    
    # Replace the .env file
    mv .env.temp .env
fi

echo "=== Azure AI Service Setup Complete ==="
echo "Hub: $HUB_NAME"
echo "Project: $PROJECT_NAME"
echo "Connection string has been saved to .env file"
echo ""
echo "Next steps:"
echo "1. Run 'python src/scripts/deploy_sk_agents.py' to deploy agents"
echo "2. Run 'python src/scripts/interact_sk_agents.py' to interact with deployed agents"