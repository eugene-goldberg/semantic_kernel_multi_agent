# Azure AI Studio Setup Guide

This guide explains how to set up Azure AI resources for deploying Semantic Kernel agents using Azure AI Studio instead of using the command-line tools.

## Prerequisites

- An Azure account with an active subscription
- Appropriate permissions to create resources in Azure

## Steps

### 1. Create a Resource Group

1. Sign in to the [Azure Portal](https://portal.azure.com)
2. Navigate to Resource Groups
3. Click "Create" to create a new resource group
4. Name it `sk-multi-agent-rg` (or your preferred name)
5. Select a suitable region (e.g., East US or West US)
6. Click "Review + create" and then "Create"

### 2. Navigate to Azure AI Studio

1. Open [Azure AI Studio](https://ai.azure.com)
2. Sign in with your Azure account
3. Click "Create a new project" or equivalent option

### 3. Create a New AI Hub

1. In Azure AI Studio, navigate to the Hub section
2. Click "Create new hub"
3. Enter the following details:
   - Hub name: `sk-multi-agent-hub`
   - Subscription: Select your subscription
   - Resource group: Select the resource group you created
   - Region: Select a region that supports Azure AI services
4. Click "Create"

### 4. Create a New AI Project

1. In your newly created Hub, click "Create new project"
2. Enter the following details:
   - Project name: `sk-multi-agent-project`
   - Description: Optional
   - Default model: Select `gpt-35-turbo` (or the desired model)
3. Click "Create"

### 5. Get Connection Information

1. In your project, look for "Connection information" or "Settings"
2. Copy the following information:
   - Connection string
   - Project endpoint
   - Subscription ID

### 6. Update Environment Variables

1. Open the `.env.ai_service` file in your project
2. Update the following values:
   ```
   AZURE_SUBSCRIPTION_ID=your-subscription-id
   AZURE_RESOURCE_GROUP=sk-multi-agent-rg
   AZURE_AI_HUB_NAME=sk-multi-agent-hub
   AZURE_AI_PROJECT_NAME=sk-multi-agent-project
   AZURE_AI_PROJECT_HOST=your-region.ai.projects.azure.com
   AZURE_AI_PROJECT_CONNECTION_STRING=your-full-connection-string
   ```

## Next Steps

After setting up the Azure AI resources, you can proceed with deploying your agents:

```bash
python src/scripts/deploy_sk_agents.py
```

This will deploy all agents to your Azure AI Service project, and you can then interact with them using:

```bash
python src/scripts/interact_sk_agents.py
```

## Troubleshooting

- If you encounter errors related to authentication, run `az login` from the command line
- Make sure you have selected the correct subscription
- Verify that the selected region supports all required Azure AI services
- Check that your service principal or user account has the necessary permissions