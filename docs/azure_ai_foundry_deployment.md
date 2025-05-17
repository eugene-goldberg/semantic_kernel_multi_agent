# Azure AI Foundry Deployment Guide

This guide explains how to deploy Semantic Kernel agents to Azure AI Foundry using our deployment scripts.

## Prerequisites

1. **Azure Account and Subscription**
   - Active Azure subscription
   - Appropriate permissions to create and manage resources

2. **Azure CLI**
   - Install the Azure CLI: [https://docs.microsoft.com/en-us/cli/azure/install-azure-cli](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
   - Log in to Azure: `az login`

3. **Azure AI Foundry Setup**
   - Azure AI Foundry workspace must be created and accessible
   - Reference: [https://ai.azure.com/](https://ai.azure.com/)
   - Required workspace name: `sk-multi-agent-project`
   - Required resource group: `semantic-kernel-multi-agent-rg`

## Environment Configuration

1. **Configure .env.ai_foundry**
   - Copy the template below to `.env.ai_foundry`
   - Update with your Azure subscription ID and resource group name

```
# Azure AI Foundry Configuration
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=semantic-kernel-multi-agent-rg
AZURE_WORKSPACE_NAME=sk-multi-agent-project
AZURE_REGION=westus
AI_FOUNDRY_API_VERSION=2024-12-01-preview
AI_MODEL_NAME=gpt-35-turbo
```

## Deployment Process

1. **Deploy All Agents**
   ```bash
   python src/scripts/deploy_ai_foundry_agents.py
   ```

2. **Deploy Specific Agent**
   ```bash
   # Deploy the chat agent
   python src/scripts/deploy_ai_foundry_agents.py chat

   # Deploy the weather agent
   python src/scripts/deploy_ai_foundry_agents.py weather

   # Deploy the calculator agent
   python src/scripts/deploy_ai_foundry_agents.py calculator

   # Deploy the orchestrator agent
   python src/scripts/deploy_ai_foundry_agents.py orchestrator
   ```

3. **View Agent Information**
   ```bash
   python src/scripts/deploy_ai_foundry_agents.py info
   ```

## Interacting with Deployed Agents

1. **Interactive Chat**
   ```bash
   python src/scripts/interact_ai_foundry_agents.py
   ```

2. **Commands During Chat**
   - `switch <agent-type>` - Switch to a different agent (chat, weather, calculator, orchestrator)
   - `clear` - Clear the conversation history
   - `exit` - Exit the chat session

## Azure AI Foundry REST API Details

Our implementation uses the Azure AI Foundry REST API directly. The key endpoints used are:

1. **Create Agent**
   - Endpoint: `/assistants`
   - Method: POST
   - Required Parameters: `name`, `instructions`, `model`, `tools` (optional)

2. **Create Thread**
   - Endpoint: `/threads`
   - Method: POST

3. **Add Message to Thread**
   - Endpoint: `/threads/{thread_id}/messages`
   - Method: POST
   - Required Parameters: `role`, `content`

4. **Run Thread with Agent**
   - Endpoint: `/threads/{thread_id}/runs`
   - Method: POST
   - Required Parameters: `assistant_id`

5. **Check Run Status**
   - Endpoint: `/threads/{thread_id}/runs/{run_id}`
   - Method: GET

6. **Get Thread Messages**
   - Endpoint: `/threads/{thread_id}/messages`
   - Method: GET

## Deployment Files

1. **ai_foundry_deployment_info.json**
   - Contains the deployed agent IDs and workspace information
   - Created after successful deployment

2. **orchestration_deployment_info.json**
   - Compatibility file for existing scripts
   - Contains the same information as ai_foundry_deployment_info.json

## Troubleshooting

1. **Authentication Issues**
   - Run `az login` to ensure you're authenticated with Azure
   - Verify your Azure account has access to the specified subscription

2. **Deployment Failures**
   - Check that the workspace exists and is accessible
   - Verify that the model specified in .env.ai_foundry is available in your Azure region
   - Check the logs for specific error messages

3. **Connectivity Issues**
   - Verify network connectivity to the Azure AI Foundry API endpoint
   - Check for any firewall or proxy settings that might block connections