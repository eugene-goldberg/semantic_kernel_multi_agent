#!/bin/bash
# CLI script for deploying agents to Azure AI Agent Service

set -e

echo "===== Azure AI Agent Service Deployment ====="
echo "This script will deploy agents to Azure AI Agent Service."

# Load environment variables
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(grep -v '^#' .env | xargs)
fi

# Check login status
echo "Checking Azure CLI login status..."
az account show > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "You are not logged in to Azure CLI. Logging in now..."
    az login
else 
    echo "You are already logged in to Azure CLI."
    account=$(az account show --query name -o tsv)
    echo "Current account: $account"
fi

# Set subscription
if [ -n "$AZURE_SUBSCRIPTION_ID" ]; then
    echo "Setting subscription to $AZURE_SUBSCRIPTION_ID..."
    az account set --subscription "$AZURE_SUBSCRIPTION_ID"
fi

# Create service principal if requested
if [ "$1" == "--create-sp" ]; then
    echo "Creating service principal for deployment..."
    bash src/scripts/create_service_principal.sh
    if [ -f .env.service_principal ]; then
        echo "Adding service principal credentials to environment..."
        source .env.service_principal
        cat .env.service_principal >> .env
    fi
    shift
fi

# Determine authentication method
auth_flag=""
if [ -n "$AZURE_CLIENT_ID" ] && [ -n "$AZURE_CLIENT_SECRET" ] && [ -n "$AZURE_TENANT_ID" ]; then
    echo "Service Principal credentials found. Using Service Principal authentication."
    auth_flag="--use-service-principal"
else
    echo "Using Default Azure authentication."
fi

# Get the correct endpoint
if [ -n "$AZURE_AI_PROJECT_HOST" ]; then
    endpoint="https://$AZURE_AI_PROJECT_HOST/"
    echo "Using endpoint: $endpoint"
    endpoint_flag="--endpoint $endpoint"
fi

# Run the Python deployment script
echo "Deploying agents to Azure AI Agent Service..."
python3 src/scripts/deploy_agents_sdk.py $auth_flag $endpoint_flag $@

# Test the deployment
if [ -f deployment_info.json ]; then
    echo "Would you like to test the deployed agents? (y/n)"
    read -r test_deployment
    if [[ "$test_deployment" =~ ^[Yy]$ ]]; then
        echo "Starting interactive chat with deployed agents..."
        python src/scripts/interact_deployed_agents.py
    fi
fi