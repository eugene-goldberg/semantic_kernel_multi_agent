#!/bin/bash
# List Azure resources relevant to the project

set -e

echo "===== Azure Resources for Semantic Kernel Multi-Agent Project ====="

# Load environment variables
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(grep -v '^#' .env | xargs)
fi

# Check environment variables
if [ -z "$AZURE_SUBSCRIPTION_ID" ]; then
    echo "ERROR: AZURE_SUBSCRIPTION_ID is not set in .env file"
    exit 1
fi

if [ -z "$AZURE_RESOURCE_GROUP" ]; then
    echo "ERROR: AZURE_RESOURCE_GROUP is not set in .env file"
    exit 1
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
echo "Setting subscription to $AZURE_SUBSCRIPTION_ID..."
az account set --subscription "$AZURE_SUBSCRIPTION_ID"

# List resource groups
echo -e "\n===== Resource Groups ====="
az group list --query "[?name=='$AZURE_RESOURCE_GROUP']" --output table

# List all resources in the resource group
echo -e "\n===== All Resources in $AZURE_RESOURCE_GROUP ====="
az resource list --resource-group $AZURE_RESOURCE_GROUP --output table

# List Cognitive Services accounts (which include OpenAI resources)
echo -e "\n===== Cognitive Services Accounts ====="
az cognitiveservices account list --resource-group $AZURE_RESOURCE_GROUP --output table

# Get details of OpenAI deployment
if [ -n "$AZURE_OPENAI_DEPLOYMENT_NAME" ]; then
    echo -e "\n===== OpenAI Deployment: $AZURE_OPENAI_DEPLOYMENT_NAME ====="
    OPENAI_ACCOUNT=$(az cognitiveservices account list --resource-group $AZURE_RESOURCE_GROUP --query "[?kind=='OpenAI'].name" -o tsv)
    
    if [ -n "$OPENAI_ACCOUNT" ]; then
        echo "Found OpenAI account: $OPENAI_ACCOUNT"
        
        # List deployments
        echo -e "\n===== OpenAI Deployments ====="
        az cognitiveservices account deployment list \
            --name $OPENAI_ACCOUNT \
            --resource-group $AZURE_RESOURCE_GROUP \
            --output table
    else
        echo "No OpenAI account found in resource group $AZURE_RESOURCE_GROUP"
    fi
fi

# Look for Machine Learning Services workspace
echo -e "\n===== Machine Learning Services Workspaces ====="
az ml workspace list --resource-group $AZURE_RESOURCE_GROUP --output table 2>/dev/null || echo "No Machine Learning workspaces found"

# Summary of findings
echo -e "\n===== Summary ====="
echo "Resource Group: $AZURE_RESOURCE_GROUP"

OPENAI_ACCOUNT=$(az cognitiveservices account list --resource-group $AZURE_RESOURCE_GROUP --query "[?kind=='OpenAI'].name" -o tsv)
if [ -n "$OPENAI_ACCOUNT" ]; then
    echo "OpenAI Account: $OPENAI_ACCOUNT"
    echo "OpenAI Endpoint: $(az cognitiveservices account show --name $OPENAI_ACCOUNT --resource-group $AZURE_RESOURCE_GROUP --query properties.endpoint -o tsv)"
    
    # Check if the deployment exists
    DEPLOYMENT_EXISTS=$(az cognitiveservices account deployment list \
        --name $OPENAI_ACCOUNT \
        --resource-group $AZURE_RESOURCE_GROUP \
        --query "[?name=='$AZURE_OPENAI_DEPLOYMENT_NAME'].name" -o tsv)
    
    if [ -n "$DEPLOYMENT_EXISTS" ]; then
        echo "OpenAI Deployment: $AZURE_OPENAI_DEPLOYMENT_NAME ✓"
    else
        echo "OpenAI Deployment: $AZURE_OPENAI_DEPLOYMENT_NAME ✗ (not found)"
    fi
else
    echo "OpenAI Account: Not found"
fi

echo ""
echo "To deploy agents, you would need to:"
echo "1. Have an Azure AI Project (AI Hub/Project) provisioned"
echo "2. Have an Azure OpenAI deployment available"
echo "3. Update your .env file with the correct resource names"
echo ""
echo "For manual deployment, go to the Azure AI Studio at https://ai.azure.com"