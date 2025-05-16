# Azure AI Foundry Setup Guide Using Azure CLI

> **Note**: Model availability depends on your Azure subscription and region. The commands in this guide use `gpt-35-turbo-1106` as the default model since it has wider availability. 
>
> As of May 2025, the most widely available models include:
> - `gpt-35-turbo-1106`: Generally widely available across regions
> - `gpt-35-turbo-0125`: Alternative version of GPT-3.5 Turbo
> - `gpt-35-turbo-0613`: Slightly older but stable version
> - `text-embedding-ada-002`: Very widely available embedding model
>
> If you have access to more advanced models like GPT-4o or o-series models, you can substitute those instead.

This guide provides step-by-step Azure CLI commands to set up the entire infrastructure needed for our multi-agent application with Azure AI Foundry, including Hub creation, Project setup, OpenAI model deployment, and agent configuration.

## Prerequisites

Before you begin, ensure you have:

1. Azure CLI installed: [Installation Guide](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
2. Required extensions installed:
   ```bash
   az extension add --name ml
   az extension add --name ai
   az extension add --name cognitiveservices
   ```
3. Authenticated with Azure:
   ```bash
   az login
   ```
4. Set your subscription:
   ```bash
   # List available subscriptions
   az account list --output table
   
   # Set the subscription you want to use
   az account set --subscription "Your-Subscription-Name-or-ID"
   ```

## Step 1: Create Resource Group

```bash
# Create a new resource group
az group create \
  --name "semantic-kernel-multi-agent-rg" \
  --location "eastus"
```

## Step 2: Create Azure OpenAI Service

```bash
# Create Azure OpenAI Service
az cognitiveservices account create \
  --name "sk-multi-agent-openai" \
  --resource-group "semantic-kernel-multi-agent-rg" \
  --kind OpenAI \
  --sku S0 \
  --location "eastus" \
  --custom-domain "sk-multi-agent-openai"
```

## Step 3: Deploy OpenAI Models

First, check which models are available in your region:

```bash
# List available models
az cognitiveservices account list-models \
  --name "sk-multi-agent-openai" \
  --resource-group "semantic-kernel-multi-agent-rg" \
  --query "[].{Model:id}" -o table
```

Then deploy a model that's available in your region. Try models in this recommended order:

```bash
# Deploy GPT-3.5 Turbo 1106 model (widely available)
az cognitiveservices account deployment create \
  --name "sk-multi-agent-openai" \
  --resource-group "semantic-kernel-multi-agent-rg" \
  --deployment-name "gpt-35-turbo" \
  --model-name "gpt-35-turbo" \
  --model-version "1106" \
  --model-format OpenAI \
  --sku-capacity 1 \
  --sku-name Standard
```

If the above model isn't available in your region, try these alternatives:

```bash
# Alternative: GPT-3.5 Turbo 0125
az cognitiveservices account deployment create \
  --name "sk-multi-agent-openai" \
  --resource-group "semantic-kernel-multi-agent-rg" \
  --deployment-name "gpt-35-turbo" \
  --model-name "gpt-35-turbo" \
  --model-version "0125" \
  --model-format OpenAI \
  --sku-capacity 1 \
  --sku-name Standard

# Alternative: GPT-3.5 Turbo 0613
az cognitiveservices account deployment create \
  --name "sk-multi-agent-openai" \
  --resource-group "semantic-kernel-multi-agent-rg" \
  --deployment-name "gpt-35-turbo" \
  --model-name "gpt-35-turbo" \
  --model-version "0613" \
  --model-format OpenAI \
  --sku-capacity 1 \
  --sku-name Standard

# Last resort: Text-Embedding-Ada-002 (basic but widely available)
az cognitiveservices account deployment create \
  --name "sk-multi-agent-openai" \
  --resource-group "semantic-kernel-multi-agent-rg" \
  --deployment-name "text-embedding-ada-002" \
  --model-name "text-embedding-ada-002" \
  --model-version "2" \
  --model-format OpenAI \
  --sku-capacity 1 \
  --sku-name Standard
```

If you have access to newer models in your subscription, you could use one of these:

```bash
# For GPT-4o (if available)
az cognitiveservices account deployment create \
  --name "sk-multi-agent-openai" \
  --resource-group "semantic-kernel-multi-agent-rg" \
  --deployment-name "gpt-4o" \
  --model-name "gpt-4o" \
  --model-version "2024-05-13" \
  --model-format OpenAI \
  --sku-capacity 1 \
  --sku-name Standard

# For o-series models (if available)
az cognitiveservices account deployment create \
  --name "sk-multi-agent-openai" \
  --resource-group "semantic-kernel-multi-agent-rg" \
  --deployment-name "o3-mini" \
  --model-name "o3-mini" \
  --model-version "2025-01-31" \
  --model-format OpenAI \
  --sku-capacity 1 \
  --sku-name Standard
```

## Step 4: Create Azure AI Foundry Hub

```bash
# Create Azure AI Foundry Hub
az deployment group create \
  --resource-group "semantic-kernel-multi-agent-rg" \
  --template-uri "https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/quickstarts/microsoft.machinelearningservices/machine-learning-hub-create/azuredeploy.json" \
  --parameters hubName="sk-multi-agent-hub" location="eastus"
```

## Step 5: Create a Project within the Hub

```bash
# Create an Azure AI Foundry Project within the Hub
az ml workspace create \
  --name "sk-multi-agent-project" \
  --resource-group "semantic-kernel-multi-agent-rg" \
  --location "eastus" \
  --hub-name "sk-multi-agent-hub"
```

## Step 6: Link Azure OpenAI to the Project

```bash
# Link Azure OpenAI service to the project
az ml connection create ai-service \
  --name "openai-connection" \
  --workspace-name "sk-multi-agent-project" \
  --resource-group "semantic-kernel-multi-agent-rg" \
  --target-resource-id "/subscriptions/<your-subscription-id>/resourceGroups/semantic-kernel-multi-agent-rg/providers/Microsoft.CognitiveServices/accounts/sk-multi-agent-openai" \
  --category "AzureOpenAI"
```

## Step 7: Get Connection String and Credentials

```bash
# Get the connection string for your project
az ml workspace show \
  --name "sk-multi-agent-project" \
  --resource-group "semantic-kernel-multi-agent-rg" \
  --query discovery_url

# Get key for Azure OpenAI Service
az cognitiveservices account keys list \
  --name "sk-multi-agent-openai" \
  --resource-group "semantic-kernel-multi-agent-rg"
  
# Get endpoint for Azure OpenAI Service
az cognitiveservices account show \
  --name "sk-multi-agent-openai" \
  --resource-group "semantic-kernel-multi-agent-rg" \
  --query endpoint
```

## Step 8: Create a Connection String for the Project

After retrieving the discovery_url from the command above, you need to format the connection string:

1. Take the discovery_url value (e.g., https://eastus.api.azureml.ms/discovery/abcdef123456)
2. Extract the HostName by removing "https://" and "/discovery/abcdef123456" to get "eastus.api.azureml.ms"
3. Create the connection string in this format:
   ```
   <HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>/<ProjectName>
   ```

For example:
```
eastus.api.azureml.ms;xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx;semantic-kernel-multi-agent-rg;sk-multi-agent-hub/sk-multi-agent-project
```

## Step 9: Configure Project Environment Variables

Create or update your `.env` file with the following values:
```
# Azure OpenAI Service Configuration
AZURE_OPENAI_ENDPOINT=<endpoint-from-step-7>
AZURE_OPENAI_API_KEY=<key-from-step-7>
AZURE_OPENAI_DEPLOYMENT_NAME=<deployed-model-name>   # Whatever model was successfully deployed

# Azure AI Foundry Configuration
AZURE_AI_HUB_NAME=sk-multi-agent-hub
AZURE_AI_PROJECT_NAME=sk-multi-agent-project
AZURE_AI_PROJECT_HOST=eastus.api.azureml.ms
AZURE_SUBSCRIPTION_ID=<your-subscription-id>
AZURE_RESOURCE_GROUP=semantic-kernel-multi-agent-rg
AZURE_AI_PROJECT_CONNECTION_STRING=<connection-string-from-step-8>

# Weather API Configuration
WEATHER_API_KEY=<your-weather-api-key>
WEATHER_API_BASE_URL=https://api.openweathermap.org/data/2.5
```

## Step 10: Verify Setup

Verify your setup with the following commands:

```bash
# Verify Azure OpenAI service
az cognitiveservices account list \
  --resource-group "semantic-kernel-multi-agent-rg" \
  --output table

# Verify model deployment
az cognitiveservices account deployment list \
  --name "sk-multi-agent-openai" \
  --resource-group "semantic-kernel-multi-agent-rg" \
  --output table

# Verify AI Foundry Hub
az ml hub list \
  --resource-group "semantic-kernel-multi-agent-rg" \
  --output table

# Verify AI Foundry Project
az ml workspace list \
  --resource-group "semantic-kernel-multi-agent-rg" \
  --output table
```

## Step 11: Setup Identity and Permissions (Optional but Recommended)

If you're planning to use managed identities for authentication:

```bash
# Create a managed identity for your project
az identity create \
  --name "sk-multi-agent-identity" \
  --resource-group "semantic-kernel-multi-agent-rg"

# Assign OpenAI role to the identity
az role assignment create \
  --assignee-object-id $(az identity show --name "sk-multi-agent-identity" --resource-group "semantic-kernel-multi-agent-rg" --query principalId -o tsv) \
  --role "Cognitive Services OpenAI User" \
  --scope "/subscriptions/<your-subscription-id>/resourceGroups/semantic-kernel-multi-agent-rg/providers/Microsoft.CognitiveServices/accounts/sk-multi-agent-openai"

# Assign AI Developer role to the identity
az role assignment create \
  --assignee-object-id $(az identity show --name "sk-multi-agent-identity" --resource-group "semantic-kernel-multi-agent-rg" --query principalId -o tsv) \
  --role "Azure AI Developer" \
  --scope "/subscriptions/<your-subscription-id>/resourceGroups/semantic-kernel-multi-agent-rg"
```

## Next Steps

After setting up your Azure AI Foundry infrastructure with these commands, you can:

1. Deploy agents from your code:
   ```bash
   python src/scripts/deploy_agents.py
   ```

2. Interact with the deployed agents:
   ```bash
   python src/scripts/remote_chat.py
   ```

3. Start the API server for client applications:
   ```bash
   python src/scripts/run_api_server.py
   ```

## Troubleshooting

If you encounter errors during the setup process:

- **Connection Errors**: Ensure you're authenticated and using the correct subscription
- **Permission Issues**: Verify you have the required roles (Azure AI Developer, Contributor on the resource group)
- **Model Availability**: Check that the requested OpenAI model is available in your region
- **Syntax Errors**: Ensure you're using the correct format for your commands
- **Resource Name Errors**: Make sure your resource names follow Azure naming conventions

For more detailed error resolution, refer to the Azure CLI documentation or the respective service documentation.

## Cleaning Up Resources

When you're done with the resources, you can clean them up to avoid charges:

```bash
# Delete the entire resource group
az group delete \
  --name "semantic-kernel-multi-agent-rg" \
  --yes --no-wait
```