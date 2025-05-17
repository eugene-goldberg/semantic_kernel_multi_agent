# Deploying Semantic Kernel Agents to Azure AI Service

This guide explains how to deploy the Semantic Kernel (SK) based agents to Azure AI Service.

## Prerequisites

1. Azure subscription
2. Azure CLI installed and configured
3. Required permissions to create Azure AI resources
4. Python 3.9+ with the required packages installed

## Setup Process

### 1. Environment Setup

First, set up your Azure AI Service environment using the provided script:

```bash
# Make the script executable if needed
chmod +x src/scripts/setup_azure_ai_service.sh

# Run the setup script
./src/scripts/setup_azure_ai_service.sh
```

This script will:
- Create a resource group if it doesn't exist
- Create an Azure AI Hub
- Create an Azure AI Project
- Configure the necessary connection settings in your `.env` file

### 2. Verify Environment Configuration

After running the setup script, your `.env` file should contain:

```
AZURE_AI_HUB_NAME=sk-multi-agent-hub
AZURE_AI_PROJECT_NAME=sk-multi-agent-project
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=sk-multi-agent-rg
AZURE_AI_PROJECT_HOST=westus.ai.projects.azure.com
AZURE_AI_PROJECT_CONNECTION_STRING=westus.ai.projects.azure.com;your-subscription-id;your-resource-group;sk-multi-agent-hub/sk-multi-agent-project
AI_MODEL_NAME=gpt-35-turbo
```

Ensure these values are correct for your environment.

### 3. Deploy Agents

Deploy all agents to Azure AI Service:

```bash
python src/scripts/deploy_sk_agents.py
```

To deploy a specific agent type:

```bash
python src/scripts/deploy_sk_agents.py chat
python src/scripts/deploy_sk_agents.py weather
python src/scripts/deploy_sk_agents.py calculator
python src/scripts/deploy_sk_agents.py orchestrator
```

To view agent configurations:

```bash
python src/scripts/deploy_sk_agents.py info
```

### 4. Verify Deployment

Check the generated `sk_deployment_info.json` file to see the Azure AI Service agent IDs. Example:

```json
{
  "project_host": "westus.ai.projects.azure.com",
  "project_name": "sk-multi-agent-project",
  "chat_agent_id": "asst_sk_chat_1234",
  "weather_agent_id": "asst_sk_weather_5678",
  "calculator_agent_id": "asst_sk_calculator_9012",
  "orchestrator_agent_id": "asst_sk_orchestrator_3456"
}
```

## Interacting with Deployed Agents

Use the interactive chat client to interact with your deployed agents:

```bash
python src/scripts/interact_sk_agents.py
```

Within the interactive chat:
- `switch chat/weather/calculator/orchestrator` - Switch between agent types
- `clear` - Clear the conversation thread
- `exit` - Exit the chat

## Troubleshooting

### Authentication Issues

If you encounter authentication errors:

1. Ensure you're logged in using the Azure CLI: `az login`
2. Check that your account has necessary permissions for the resource group
3. Verify the connection string format is correct

### Deployment Failures

1. Check Azure quota limits for AI resources
2. Verify the model name is valid and available in your region
3. Examine logs for specific error messages

### Connection Issues

If the client can't connect to deployed agents:

1. Verify deployment was successful by checking the deployment info file
2. Ensure the provided agent IDs are correct
3. Check network connectivity to the Azure AI Service endpoints

## Differences from Azure OpenAI Deployment

This deployment method uses Azure AI Service instead of Azure OpenAI Service directly. Key differences:

1. Uses Azure AI Service agents with function calling capabilities
2. Simplifies agent deployment and management through Azure AI Projects
3. Provides a more structured conversation thread model
4. Leverages Azure DefaultAzureCredential for authentication

## Next Steps

After successful deployment:

1. Test the orchestration functionality by switching to the orchestrator agent
2. Try various queries to ensure each specialized agent works correctly
3. Consider implementing additional specialized agents using this pattern
4. Explore integrating your agents with external applications through the Azure AI Service REST API