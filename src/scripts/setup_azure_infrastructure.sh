#!/bin/bash
# Azure AI Foundry infrastructure setup script
# This script automates the creation of all necessary Azure resources for the multi-agent app

# Exit on error
set -e

# Default values (can be overridden by env vars)
RESOURCE_GROUP=${RESOURCE_GROUP:-"semantic-kernel-multi-agent-rg"}
LOCATION=${LOCATION:-"eastus"}
OPENAI_NAME=${OPENAI_NAME:-"sk-multi-agent-openai"}
# Default OpenAI model to deploy - can be overridden with env var
# Using gpt-35-turbo-1106 as it has wide availability
OPENAI_DEPLOYMENT=${OPENAI_DEPLOYMENT:-"gpt-35-turbo-1106"}
HUB_NAME=${HUB_NAME:-"sk-multi-agent-hub"}
PROJECT_NAME=${PROJECT_NAME:-"sk-multi-agent-project"}

# Get subscription ID
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
if [ -z "$SUBSCRIPTION_ID" ]; then
    echo "Error: Could not determine subscription ID. Please login using 'az login' first."
    exit 1
fi

echo "Using subscription: $SUBSCRIPTION_ID"
echo "Setting up resources in: $RESOURCE_GROUP"

# 1. Create resource group
echo "Creating resource group: $RESOURCE_GROUP in $LOCATION..."
az group create \
  --name "$RESOURCE_GROUP" \
  --location "$LOCATION"

# 2. Create Azure OpenAI Service
echo "Creating Azure OpenAI service: $OPENAI_NAME..."
az cognitiveservices account create \
  --name "$OPENAI_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --kind OpenAI \
  --sku S0 \
  --location "$LOCATION" \
  --custom-domain "$OPENAI_NAME"

# 3. Deploy OpenAI model
echo "Deploying OpenAI model: $OPENAI_DEPLOYMENT..."
# First list available models to check availability
echo "Available models in your region:"
az cognitiveservices account list-models \
  --name "$OPENAI_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query "[].{Model:id}" -o table || echo "Unable to list models, proceeding with deployment anyway"

# Try to deploy models in sequence, starting with the most capable but falling back to widely available options
deploy_model() {
    local model_name=$1
    local model_version=$2
    local deployment_name=$model_name
    
    echo "Attempting to deploy $model_name (version: $model_version)..."
    
    if az cognitiveservices account deployment create \
        --name "$OPENAI_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --deployment-name "$deployment_name" \
        --model-name "$model_name" \
        --model-version "$model_version" \
        --model-format OpenAI \
        --sku-capacity 1 \
        --sku-name Standard; then
        
        echo "Successfully deployed $model_name!"
        OPENAI_DEPLOYMENT=$deployment_name
        return 0
    else
        echo "Failed to deploy $model_name."
        return 1
    fi
}

# Try to deploy the model specified in OPENAI_DEPLOYMENT
if ! deploy_model "$OPENAI_DEPLOYMENT" "1106"; then
    # Try to deploy other models in succession
    echo "Attempting to deploy alternative models..."
    
    if deploy_model "gpt-35-turbo" "1106"; then
        echo "Successfully deployed gpt-35-turbo-1106"
    elif deploy_model "gpt-35-turbo" "0125"; then
        echo "Successfully deployed gpt-35-turbo-0125"
    elif deploy_model "gpt-35-turbo" "0613"; then
        echo "Successfully deployed gpt-35-turbo-0613"
    elif deploy_model "gpt-35-turbo" "0301"; then
        echo "Successfully deployed gpt-35-turbo-0301"
    elif deploy_model "text-embedding-ada-002" "2"; then
        echo "Successfully deployed text-embedding-ada-002"
    else
        echo "Error: Failed to deploy any model. Please check available models in your region with:"
        echo "az cognitiveservices account list-models --name \"$OPENAI_NAME\" --resource-group \"$RESOURCE_GROUP\""
        exit 1
    fi
fi

echo "Model deployment successful: $OPENAI_DEPLOYMENT"

# 4. Create Azure AI Foundry Hub
echo "Creating Azure AI Foundry Hub: $HUB_NAME..."

# Create a temporary ARM template file
TEMPLATE_FILE=$(mktemp)
cat > "$TEMPLATE_FILE" << 'EOF'
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "hubName": {
      "type": "string",
      "metadata": {
        "description": "The name of the Azure AI Foundry Hub to create."
      }
    },
    "location": {
      "type": "string",
      "defaultValue": "[resourceGroup().location]",
      "metadata": {
        "description": "The location in which to create the Azure AI Foundry Hub."
      }
    }
  },
  "resources": [
    {
      "type": "Microsoft.MachineLearningServices/workspaces",
      "apiVersion": "2024-01-01-preview",
      "name": "[parameters('hubName')]",
      "location": "[parameters('location')]",
      "kind": "Hub",
      "identity": {
        "type": "SystemAssigned"
      },
      "properties": {
        "friendlyName": "[parameters('hubName')]",
        "description": "Azure AI Foundry Hub for semantic kernel multi-agent app"
      }
    }
  ],
  "outputs": {
    "hubId": {
      "type": "string",
      "value": "[resourceId('Microsoft.MachineLearningServices/workspaces', parameters('hubName'))]"
    }
  }
}
EOF

# Deploy the hub using the local template file
az deployment group create \
  --resource-group "$RESOURCE_GROUP" \
  --template-file "$TEMPLATE_FILE" \
  --parameters hubName="$HUB_NAME" location="$LOCATION"

# Remove the temporary file
rm "$TEMPLATE_FILE"

# 5. Create Azure AI Foundry Project
echo "Creating Azure AI Foundry Project: $PROJECT_NAME..."

# Create a temporary ARM template for the project
PROJECT_TEMPLATE=$(mktemp)
cat > "$PROJECT_TEMPLATE" << EOF
{
  "\$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "projectName": {
      "type": "string",
      "metadata": {
        "description": "The name of the Azure AI Foundry Project to create."
      }
    },
    "hubName": {
      "type": "string",
      "metadata": {
        "description": "The name of the Azure AI Foundry Hub."
      }
    },
    "location": {
      "type": "string",
      "defaultValue": "[resourceGroup().location]",
      "metadata": {
        "description": "The location in which to create the Azure AI Foundry Project."
      }
    }
  },
  "resources": [
    {
      "type": "Microsoft.MachineLearningServices/workspaces",
      "apiVersion": "2024-01-01-preview",
      "name": "[parameters('projectName')]",
      "location": "[parameters('location')]",
      "kind": "Project",
      "identity": {
        "type": "SystemAssigned"
      },
      "properties": {
        "friendlyName": "[parameters('projectName')]",
        "description": "Azure AI Foundry Project for semantic kernel multi-agent app",
        "hubResourceId": "[resourceId('Microsoft.MachineLearningServices/workspaces', parameters('hubName'))]"
      }
    }
  ],
  "outputs": {
    "projectId": {
      "type": "string",
      "value": "[resourceId('Microsoft.MachineLearningServices/workspaces', parameters('projectName'))]"
    }
  }
}
EOF

# Try to create the project using the ARM template first
if az deployment group create \
  --resource-group "$RESOURCE_GROUP" \
  --template-file "$PROJECT_TEMPLATE" \
  --parameters projectName="$PROJECT_NAME" hubName="$HUB_NAME" location="$LOCATION"; then
  
  echo "Project created successfully using ARM template"
else
  # Fallback to ml workspace create command
  echo "ARM template deployment failed, trying alternative approach..."
  
  # Try the ml workspace create command
  az ml workspace create \
    --name "$PROJECT_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --hub-name "$HUB_NAME" || {
      echo "Error: Failed to create the Azure AI Foundry Project. You may need to create it manually from the Azure portal."
      # Continue with the script but set a flag
      PROJECT_CREATION_FAILED=true
    }
fi

# Remove the temporary template file
rm "$PROJECT_TEMPLATE"

# 6. Link Azure OpenAI to the Project
echo "Linking Azure OpenAI service to the project..."

# Check if project creation failed
if [ "${PROJECT_CREATION_FAILED:-false}" = "true" ]; then
  echo "Skipping OpenAI service linking since project creation failed."
else
  # Get the OpenAI resource ID
  OPENAI_ID=$(az cognitiveservices account show \
    --name "$OPENAI_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query id -o tsv)

  # Create connection template
  CONNECTION_TEMPLATE=$(mktemp)
  cat > "$CONNECTION_TEMPLATE" << EOF
  {
    "\$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
      "projectName": {
        "type": "string"
      },
      "connectionName": {
        "type": "string"
      },
      "openAIResourceId": {
        "type": "string"
      }
    },
    "resources": [
      {
        "type": "Microsoft.MachineLearningServices/workspaces/connections",
        "apiVersion": "2024-01-01-preview",
        "name": "[concat(parameters('projectName'), '/', parameters('connectionName'))]",
        "properties": {
          "category": "AzureOpenAI",
          "target": "[parameters('openAIResourceId')]",
          "authType": "ResourceId"
        }
      }
    ]
  }
EOF

  # Try to create the connection using the ARM template
  if az deployment group create \
    --resource-group "$RESOURCE_GROUP" \
    --template-file "$CONNECTION_TEMPLATE" \
    --parameters projectName="$PROJECT_NAME" connectionName="openai-connection" openAIResourceId="$OPENAI_ID"; then
    
    echo "OpenAI connection created successfully using ARM template"
  else
    # Fallback to ml connection create command
    echo "ARM template deployment failed for connection, trying alternative approach..."
    
    # Try the ml connection create command
    az ml connection create ai-service \
      --name "openai-connection" \
      --workspace-name "$PROJECT_NAME" \
      --resource-group "$RESOURCE_GROUP" \
      --target-resource-id "$OPENAI_ID" \
      --category "AzureOpenAI" || {
        echo "Error: Failed to link Azure OpenAI to the project. You may need to do this manually from the Azure portal."
      }
  fi

  # Remove the temporary template file
  rm "$CONNECTION_TEMPLATE"
fi

# 7. Get connection information
echo "Retrieving connection information..."

# Get OpenAI endpoint
OPENAI_ENDPOINT=$(az cognitiveservices account show \
  --name "$OPENAI_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query properties.endpoint -o tsv)

# Get OpenAI key
OPENAI_KEY=$(az cognitiveservices account keys list \
  --name "$OPENAI_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query key1 -o tsv)

# Get discovery URL for project connection string
DISCOVERY_URL=$(az ml workspace show \
  --name "$PROJECT_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query discovery_url -o tsv)

# Extract hostname from discovery URL
# Remove https:// and /discovery/* to get hostname
HOSTNAME=$(echo $DISCOVERY_URL | sed -e 's|https://||' -e 's|/discovery/.*||')

# Create connection string
CONNECTION_STRING="$HOSTNAME;$SUBSCRIPTION_ID;$RESOURCE_GROUP;$HUB_NAME/$PROJECT_NAME"

# 8. Create .env file from template
echo "Creating .env file with connection information..."
if [ -f ".env.example" ]; then
    cp .env.example .env
    
    # Update .env file with actual values
    sed -i.bak "s|AZURE_OPENAI_ENDPOINT=.*|AZURE_OPENAI_ENDPOINT=$OPENAI_ENDPOINT|g" .env
    sed -i.bak "s|AZURE_OPENAI_API_KEY=.*|AZURE_OPENAI_API_KEY=$OPENAI_KEY|g" .env
    sed -i.bak "s|AZURE_OPENAI_DEPLOYMENT_NAME=.*|AZURE_OPENAI_DEPLOYMENT_NAME=$OPENAI_DEPLOYMENT|g" .env
    
    sed -i.bak "s|AZURE_AI_HUB_NAME=.*|AZURE_AI_HUB_NAME=$HUB_NAME|g" .env
    sed -i.bak "s|AZURE_AI_PROJECT_NAME=.*|AZURE_AI_PROJECT_NAME=$PROJECT_NAME|g" .env
    sed -i.bak "s|AZURE_AI_PROJECT_HOST=.*|AZURE_AI_PROJECT_HOST=$HOSTNAME|g" .env
    sed -i.bak "s|AZURE_SUBSCRIPTION_ID=.*|AZURE_SUBSCRIPTION_ID=$SUBSCRIPTION_ID|g" .env
    sed -i.bak "s|AZURE_RESOURCE_GROUP=.*|AZURE_RESOURCE_GROUP=$RESOURCE_GROUP|g" .env
    sed -i.bak "s|AZURE_AI_PROJECT_CONNECTION_STRING=.*|AZURE_AI_PROJECT_CONNECTION_STRING=$CONNECTION_STRING|g" .env
    
    # Remove backup file
    rm .env.bak
    
    echo "Created and updated .env file with connection information"
else
    echo "Error: .env.example file not found. Please create .env file manually with following values:"
    echo "AZURE_OPENAI_ENDPOINT=$OPENAI_ENDPOINT"
    echo "AZURE_OPENAI_API_KEY=$OPENAI_KEY"
    echo "AZURE_OPENAI_DEPLOYMENT_NAME=$OPENAI_DEPLOYMENT"
    echo "AZURE_AI_HUB_NAME=$HUB_NAME"
    echo "AZURE_AI_PROJECT_NAME=$PROJECT_NAME"
    echo "AZURE_AI_PROJECT_HOST=$HOSTNAME"
    echo "AZURE_SUBSCRIPTION_ID=$SUBSCRIPTION_ID"
    echo "AZURE_RESOURCE_GROUP=$RESOURCE_GROUP"
    echo "AZURE_AI_PROJECT_CONNECTION_STRING=$CONNECTION_STRING"
fi

echo ""
echo "Setup complete! Resource information:"
echo "Resource Group: $RESOURCE_GROUP"
echo "OpenAI Service: $OPENAI_NAME"
echo "OpenAI Deployment: $OPENAI_DEPLOYMENT"
echo "AI Foundry Hub: $HUB_NAME"
echo "AI Foundry Project: $PROJECT_NAME"
echo "Project Connection String: $CONNECTION_STRING"
echo ""
echo "Next steps:"
echo "1. Make sure the Weather API key is set in your .env file"
echo "2. Deploy agents: python src/scripts/deploy_agents.py"
echo "3. Test agents: python src/scripts/remote_chat.py"
echo ""