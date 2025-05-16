#!/bin/bash
# This script logs in to Azure using a service principal and sets up the environment
# for the Semantic Kernel Multi-Agent Application

# Check if required environment variables are set
if [ -z "$AZURE_CLIENT_ID" ] || [ -z "$AZURE_CLIENT_SECRET" ] || [ -z "$AZURE_TENANT_ID" ]; then
    echo "Error: Required environment variables are not set."
    echo "Please set the following environment variables:"
    echo "  - AZURE_CLIENT_ID"
    echo "  - AZURE_CLIENT_SECRET"
    echo "  - AZURE_TENANT_ID"
    echo "  - AZURE_SUBSCRIPTION_ID (optional, but recommended)"
    exit 1
fi

# Login with service principal
echo "Logging in to Azure with service principal..."
az login --service-principal \
  --username "$AZURE_CLIENT_ID" \
  --password "$AZURE_CLIENT_SECRET" \
  --tenant "$AZURE_TENANT_ID"

# Check login status
if [ $? -ne 0 ]; then
    echo "Error: Failed to login with service principal."
    exit 1
fi

echo "Successfully logged in to Azure with service principal."

# Set subscription if provided
if [ ! -z "$AZURE_SUBSCRIPTION_ID" ]; then
    echo "Setting default subscription..."
    az account set --subscription "$AZURE_SUBSCRIPTION_ID"
    
    if [ $? -ne 0 ]; then
        echo "Error: Failed to set subscription."
        echo "Available subscriptions:"
        az account list --output table
        exit 1
    fi
    
    echo "Default subscription set to $AZURE_SUBSCRIPTION_ID"
else
    echo "No subscription ID provided. Using default subscription."
    echo "Current subscription:"
    az account show --output table
fi

# List available Azure OpenAI resources
echo -e "\nAvailable Azure OpenAI resources:"
az cognitiveservices account list --output table

# Check if we can access Azure AI resources
echo -e "\nChecking access to Azure AI resources..."
az extension add --name ml --yes

echo -e "\nAvailable AI workspaces:"
az ml workspace list --output table

# Done
echo -e "\nSetup complete. You can now run the deployment scripts."
echo "For example:"
echo "  python src/scripts/deploy_with_service_principal.py"
echo "  or"
echo "  bash src/scripts/deploy_agents_az_cli.sh"