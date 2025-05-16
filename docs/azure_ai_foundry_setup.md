# Azure AI Foundry Setup Guide

This guide provides step-by-step instructions for setting up Azure AI Foundry Hub and Project for deploying your multi-agent application.

## Azure AI Foundry Architecture

Azure AI Foundry organizes resources in a hierarchical structure:

- **Hub**: A container for AI projects, providing unified management and governance
- **Project**: A dedicated environment within a Hub for building, testing, and deploying AI agents
- **Agents**: Individual AI agents deployed within a project

## Creating Azure AI Foundry Resources

### Step 1: Create a Hub

1. Log in to the [Azure Portal](https://portal.azure.com)
2. Search for "AI Foundry" and select "AI Hub"
3. Click "Create" and fill in the details:
   - **Name**: Choose a unique name for your Hub
   - **Subscription**: Select your Azure subscription
   - **Resource Group**: Create a new or select an existing resource group
   - **Region**: Choose a region that supports Azure AI Foundry
   - **Plan**: Select a pricing plan that meets your needs
4. Click "Review + create" and then "Create" to provision the Hub

### Step 2: Create a Project

1. Navigate to your newly created Hub in the Azure Portal
2. Click "Create Project" and provide:
   - **Name**: Choose a name for your project
   - **Description**: (Optional) Add a description
3. Click "Create" to provision the project

### Step 3: Configure AI Models

1. In your project, navigate to "Models" or "AI Services"
2. Add Azure OpenAI service and configure:
   - Link to your existing Azure OpenAI resource
   - Select deployment(s) to use for your agents
   - Configure permissions and access controls

## Setting Up Connection String

After creating your Hub and Project, you'll need to configure the connection string for your application to connect to Azure AI Foundry. The connection string follows this format:

```
<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>/<ProjectName>
```

Where:
- **HostName**: Your region-specific endpoint (e.g., `westus.ai.foundry.azure.com`)
- **AzureSubscriptionId**: Your Azure subscription ID
- **ResourceGroup**: The resource group containing your Hub
- **HubName**: The name of your Hub
- **ProjectName**: The name of your Project within the Hub

Add this connection string to your `.env` file as `AZURE_AI_PROJECT_CONNECTION_STRING`.

Alternatively, you can provide the individual components:
- `AZURE_AI_PROJECT_HOST`
- `AZURE_SUBSCRIPTION_ID`
- `AZURE_RESOURCE_GROUP`
- `AZURE_AI_HUB_NAME`
- `AZURE_AI_PROJECT_NAME`

## Setting Up Authentication

For authentication to Azure AI Foundry, this application uses DefaultAzureCredential, which supports several authentication methods:

1. **Environment Variables**: If you have Azure CLI environment variables
2. **Azure CLI**: If you're logged in with `az login`
3. **Managed Identity**: If running in an Azure service with managed identity
4. **Visual Studio/VS Code**: Using credentials from these IDEs

Ensure you have the proper permissions to create and manage agents within your Project.

## Monitoring and Management

After deploying your agents:

1. Navigate to your Project in the Azure Portal
2. The "Agents" section shows all deployed agents
3. Monitor usage, performance, and errors
4. Set up logging and alerts for production monitoring

## Next Steps

After setting up your Azure AI Foundry environment:

1. Run the deployment script to deploy your agents:
   ```
   python src/scripts/deploy_agents.py
   ```

2. Test the deployed agents:
   ```
   python src/scripts/remote_chat.py
   ```

3. Set up the API server for client applications:
   ```
   python src/scripts/run_api_server.py
   ```