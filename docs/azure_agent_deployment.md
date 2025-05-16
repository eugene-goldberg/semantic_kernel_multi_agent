# Azure AI Agent Service Deployment Guide

This guide explains how to deploy and interact with agents on Azure AI Agent Service.

## Prerequisites

1. Azure subscription
2. Azure OpenAI service with a deployment
3. Azure AI Foundry Hub and Project
4. All required environment variables set in `.env` file

## Environment Variables

Ensure your `.env` file contains the following variables:

```
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-openai-service.openai.azure.com/
AZURE_OPENAI_API_KEY=your-openai-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=your-model-deployment-name

# Azure AI Foundry Configuration
AZURE_AI_HUB_NAME=your-hub-name
AZURE_AI_PROJECT_NAME=your-project-name
AZURE_AI_PROJECT_HOST=your-project-host.aiagent.azure.net
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=your-resource-group
```

## Service Principal Authentication

For reliable authentication, we use a Service Principal with Contributor access to your Azure subscription.

### Creating a Service Principal

Run the following script to create a service principal:

```bash
bash src/scripts/create_service_principal.sh
```

This will create a file called `.env.service_principal` with the required credentials. You can add these to your `.env` file with:

```bash
cat .env.service_principal >> .env
```

## Deploying Agents

To deploy the agents to Azure AI Agent Service, run:

```bash
python src/scripts/deploy_with_service_principal.py
```

This will:
1. Authenticate using your service principal
2. Deploy a Chat Agent and a Weather Agent
3. Save the deployment information to `deployment_info.json`

## Interacting with Deployed Agents

To start an interactive chat session with your deployed agents, run:

```bash
python src/scripts/interact_deployed_agents.py
```

In the chat interface:
- Type `exit` to quit
- Type `switch` to change between Chat and Weather agents
- Type `clear` to start a new conversation thread

## All-in-One Script

For convenience, you can use the all-in-one script to deploy and start chatting:

```bash
bash src/scripts/deploy_and_chat.sh
```

This script will:
1. Create a service principal if needed
2. Deploy the agents
3. Start an interactive chat session

## Troubleshooting

If you encounter authentication errors:

1. Ensure your service principal has Contributor access to the subscription
2. Verify your Azure AI Project exists and is accessible
3. Check that your OpenAI model deployment is available

If you see deployment errors:

1. Verify your Azure OpenAI deployment name is correct
2. Check for API version compatibility issues
3. Ensure your Azure AI Project host URL is correct