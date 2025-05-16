# GitHub Secrets Setup Guide

This guide explains how to set up GitHub secrets for the Semantic Kernel Multi-Agent application to secure sensitive information such as API keys.

## Required Secrets

The following secrets need to be configured in your GitHub repository:

1. `AZURE_OPENAI_ENDPOINT` - Your Azure OpenAI Service endpoint URL
2. `AZURE_OPENAI_API_KEY` - Your Azure OpenAI API key
3. `AZURE_OPENAI_DEPLOYMENT_NAME` - Your Azure OpenAI model deployment name
4. `AZURE_SUBSCRIPTION_ID` - Your Azure Subscription ID
5. `AZURE_RESOURCE_GROUP` - The resource group containing your Azure OpenAI resources
6. `AZURE_AI_HUB_NAME` - Your Azure AI Hub name
7. `AZURE_AI_PROJECT_NAME` - Your Azure AI Project name

## Setting Up Secrets in GitHub

1. Navigate to your GitHub repository
2. Click on "Settings" tab
3. In the left sidebar, click on "Secrets and variables" > "Actions"
4. Click on "New repository secret"
5. Add each of the secrets listed above with their corresponding values:

   - Name: `AZURE_OPENAI_ENDPOINT`
     Value: `https://sk-multi-agent-openai.openai.azure.com/`

   - Name: `AZURE_OPENAI_API_KEY`
     Value: Your API key (keep this confidential)

   - Name: `AZURE_OPENAI_DEPLOYMENT_NAME`
     Value: `gpt-35-turbo`

   - Name: `AZURE_SUBSCRIPTION_ID`
     Value: Your Azure Subscription ID

   - Name: `AZURE_RESOURCE_GROUP`
     Value: `semantic-kernel-multi-agent-rg`

   - Name: `AZURE_AI_HUB_NAME`
     Value: `sk-multi-agent-hub`

   - Name: `AZURE_AI_PROJECT_NAME`
     Value: `sk-multi-agent-project`

## Using the GitHub Actions Workflow

Once the secrets are set up, you can use the GitHub Actions workflow to deploy the agents:

1. Navigate to the "Actions" tab in your repository
2. Select the "Deploy to Azure OpenAI" workflow
3. Click "Run workflow"
4. Choose the deployment type:
   - `agents` - Deploy only the individual agents
   - `orchestration` - Deploy only the orchestration system
   - `both` - Deploy both agents and orchestration

5. Click "Run workflow" to start the deployment

The workflow will use the secrets you've configured to securely deploy the agents without exposing sensitive information in the code.

## Local Development

For local development, copy the `.env.sample` file to `.env` and add your values:

```
# Azure OpenAI Service Configuration
AZURE_OPENAI_ENDPOINT=your-endpoint-here
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name-here

# Azure AI Foundry Configuration
AZURE_AI_HUB_NAME=your-hub-name-here
AZURE_AI_PROJECT_NAME=your-project-name-here
AZURE_SUBSCRIPTION_ID=your-subscription-id-here
AZURE_RESOURCE_GROUP=your-resource-group-here
```

**IMPORTANT**: Never commit your `.env` file containing actual secrets to the repository. It is included in `.gitignore` to prevent accidental commits.