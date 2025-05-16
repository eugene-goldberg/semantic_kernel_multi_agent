# Azure Authentication Without Browser Access

In environments without browser access (like remote servers, CI/CD pipelines, or headless environments), you can authenticate to Azure using service principals. Here's how to set it up:

## Creating a Service Principal

On a system with browser access to Azure, run:

```bash
# Create a service principal and configure its access to Azure resources
az ad sp create-for-rbac --name "semantic-kernel-sp" --role contributor --scopes /subscriptions/your-subscription-id

# This command will output something like:
# {
#   "appId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
#   "displayName": "semantic-kernel-sp",
#   "password": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
#   "tenant": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
# }

# Save this information securely - you'll need it for authentication
```

## Authentication Methods

### 1. Environment Variables

Set these environment variables before running Azure CLI commands:

```bash
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_ID="your-app-id"
export AZURE_CLIENT_SECRET="your-password"

# Now you can run Azure CLI commands without interactive login
az account show
```

### 2. Service Principal Login

```bash
# Log in with service principal credentials
az login --service-principal --username APP_ID --password PASSWORD --tenant TENANT_ID

# Example:
az login --service-principal --username "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" \
  --password "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
  --tenant "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

### 3. Using az CLI with Default Credentials

If you've already set the environment variables, you can use them implicitly:

```bash
# For scripts that use the Azure CLI with service principal credentials
az account set --subscription "your-subscription-id"
```

## For the Semantic Kernel Multi-Agent Application

For this project, you can create a `.env` file with these credentials:

```
# Azure service principal authentication
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-app-id
AZURE_CLIENT_SECRET=your-password
AZURE_SUBSCRIPTION_ID=your-subscription-id

# Other settings for Azure OpenAI
AZURE_OPENAI_ENDPOINT=your-azure-openai-endpoint
AZURE_OPENAI_API_KEY=your-azure-openai-key
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name

# Azure AI Foundry settings
AZURE_AI_HUB_NAME=your-hub-name
AZURE_AI_PROJECT_NAME=your-project-name
AZURE_AI_PROJECT_HOST=your-project-host
AZURE_RESOURCE_GROUP=your-resource-group
```

Then you can use Azure credentials through the `DefaultAzureCredential` which will pick up these environment variables.

## Checking Authentication Status

After logging in with service principal, check your authentication status:

```bash
# Verify current account
az account show

# List available subscriptions
az account list --output table
```

## Using the Service Principal with deploy_agents.py

The project's `deploy_agents.py` script is designed to work with the DefaultAzureCredential, which can use service principal credentials from environment variables.

Simply set up your `.env` file with the credentials above and run:

```bash
python src/scripts/deploy_agents.py
```

## Using with Service Principal Script

The project includes a specific script for deploying with service principal in `src/scripts/deploy_with_service_principal.py`.

This script is specifically designed to use service principal authentication for deploying agents to Azure AI Agent Service.