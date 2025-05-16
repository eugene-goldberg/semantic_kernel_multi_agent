#!/bin/bash
# This script creates a service principal for Azure AI Agent Service authentication

set -e

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(grep -v '^#' .env | xargs)
fi

if [ -z "$AZURE_SUBSCRIPTION_ID" ]; then
    echo "ERROR: AZURE_SUBSCRIPTION_ID is not set."
    echo "Please set this environment variable and try again."
    exit 1
fi

echo "Creating service principal for Azure AI Agent Service..."
echo "This service principal will have Contributor access to your subscription."

# Create the service principal
result=$(az ad sp create-for-rbac \
    --name "MultiAgentApp" \
    --role contributor \
    --scopes /subscriptions/$AZURE_SUBSCRIPTION_ID \
    --sdk-auth)

# Extract values
client_id=$(echo $result | jq -r '.clientId')
client_secret=$(echo $result | jq -r '.clientSecret')
tenant_id=$(echo $result | jq -r '.tenantId')

# Check if extraction succeeded
if [ -z "$client_id" ] || [ -z "$client_secret" ] || [ -z "$tenant_id" ]; then
    echo "ERROR: Failed to extract service principal credentials."
    echo "Raw output: $result"
    exit 1
fi

# Create .env.service_principal file
cat > .env.service_principal << EOF
# Service Principal credentials for Azure authentication
# Created on $(date)
AZURE_CLIENT_ID=$client_id
AZURE_CLIENT_SECRET=$client_secret
AZURE_TENANT_ID=$tenant_id
EOF

echo "Service principal created successfully!"
echo "Credentials saved to .env.service_principal"
echo ""
echo "To use these credentials, add them to your .env file with:"
echo "cat .env.service_principal >> .env"
echo ""
echo "Or set them as environment variables before running the deployment scripts:"
echo "export AZURE_CLIENT_ID=$client_id"
echo "export AZURE_CLIENT_SECRET=$client_secret"
echo "export AZURE_TENANT_ID=$tenant_id"
echo ""
echo "IMPORTANT: Keep these credentials secure. They grant access to your Azure resources."