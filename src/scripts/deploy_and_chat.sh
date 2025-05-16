#!/bin/bash
# This script deploys agents and starts an interactive chat session

set -e

echo "===== Multi-Agent Application Deployment and Chat ====="
echo "This script will deploy agents to Azure AI Agent Service and start a chat session."

# Check if service principal credentials exist
if [ ! -f .env.service_principal ] && [ -z "$AZURE_CLIENT_ID" ]; then
    echo ""
    echo "No service principal credentials found. Creating one now..."
    bash src/scripts/create_service_principal.sh
    
    # Source the newly created credentials
    source .env.service_principal
fi

# Deploy agents
echo ""
echo "===== Deploying Agents ====="
python src/scripts/deploy_with_service_principal.py

# Check deployment result
if [ $? -ne 0 ]; then
    echo "ERROR: Agent deployment failed."
    exit 1
fi

# Wait a moment for deployment to complete
echo "Waiting for deployment to complete..."
sleep 5

# Start chat session
echo ""
echo "===== Starting Interactive Chat Session ====="
python src/scripts/interact_deployed_agents.py