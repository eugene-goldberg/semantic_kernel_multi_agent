#!/bin/bash
# Deploy agents to Azure AI Agent Service using Azure CLI
# This script uses the az CLI to deploy agents directly

set -e

echo "===== Azure AI Agent Service Deployment using Azure CLI ====="
echo "This script will deploy agents to Azure AI Agent Service."

# Load environment variables
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(grep -v '^#' .env | xargs)
fi

# Check environment variables
if [ -z "$AZURE_SUBSCRIPTION_ID" ]; then
    echo "ERROR: AZURE_SUBSCRIPTION_ID is not set in .env file"
    exit 1
fi

if [ -z "$AZURE_RESOURCE_GROUP" ]; then
    echo "ERROR: AZURE_RESOURCE_GROUP is not set in .env file"
    exit 1
fi

if [ -z "$AZURE_AI_PROJECT_NAME" ]; then
    echo "ERROR: AZURE_AI_PROJECT_NAME is not set in .env file"
    exit 1
fi

if [ -z "$AZURE_OPENAI_DEPLOYMENT_NAME" ]; then
    echo "ERROR: AZURE_OPENAI_DEPLOYMENT_NAME is not set in .env file"
    exit 1
fi

# Check login status
echo "Checking Azure CLI login status..."
az account show > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "You are not logged in to Azure CLI. Logging in now..."
    az login
else 
    echo "You are already logged in to Azure CLI."
    account=$(az account show --query name -o tsv)
    echo "Current account: $account"
fi

# Set subscription
echo "Setting subscription to $AZURE_SUBSCRIPTION_ID..."
az account set --subscription "$AZURE_SUBSCRIPTION_ID"

# Create temporary JSON files for agent definitions
echo "Creating agent definitions..."

# Chat agent definition
cat > chat_agent.json << EOF
{
  "name": "ChatAgent",
  "description": "A general chat agent",
  "model": "$AZURE_OPENAI_DEPLOYMENT_NAME",
  "instructions": "You are a helpful assistant that provides friendly, concise, and accurate information. You should be conversational but prioritize accuracy and brevity over verbosity. If you don't know something, admit it clearly rather than making guesses."
}
EOF

# Weather agent definition
cat > weather_agent.json << EOF
{
  "name": "WeatherAgent",
  "description": "A weather specialist agent",
  "model": "$AZURE_OPENAI_DEPLOYMENT_NAME",
  "instructions": "You are a weather specialist agent that provides accurate and helpful weather information for locations in the United States. You have access to real-time US weather data through the National Weather Service API. When asked about weather, use the coordinates of the city to get accurate data. For example, Seattle is at 47.6062, -122.3321. New York is at 40.7128, -74.0060. Provide your answers in a friendly, concise manner, focusing on the most relevant information. If asked about weather outside the United States, politely explain that your weather data is currently limited to US locations only."
}
EOF

# Deploy agents using Azure CLI
echo "Deploying Chat Agent..."
CHAT_AGENT_RESULT=$(az rest --method post \
  --url "https://management.azure.com/subscriptions/$AZURE_SUBSCRIPTION_ID/resourceGroups/$AZURE_RESOURCE_GROUP/providers/Microsoft.CognitiveServices/accounts/$AZURE_AI_PROJECT_NAME/azureAIAgents/ChatAgent?api-version=2023-05-01" \
  --body @chat_agent.json \
  --output json)

if [ $? -eq 0 ]; then
    echo "Chat Agent deployed successfully!"
    CHAT_AGENT_ID=$(echo $CHAT_AGENT_RESULT | jq -r '.id')
    echo "Chat Agent ID: $CHAT_AGENT_ID"
else
    echo "Failed to deploy Chat Agent"
    CHAT_AGENT_ID="failed"
fi

echo "Deploying Weather Agent..."
WEATHER_AGENT_RESULT=$(az rest --method post \
  --url "https://management.azure.com/subscriptions/$AZURE_SUBSCRIPTION_ID/resourceGroups/$AZURE_RESOURCE_GROUP/providers/Microsoft.CognitiveServices/accounts/$AZURE_AI_PROJECT_NAME/azureAIAgents/WeatherAgent?api-version=2023-05-01" \
  --body @weather_agent.json \
  --output json)

if [ $? -eq 0 ]; then
    echo "Weather Agent deployed successfully!"
    WEATHER_AGENT_ID=$(echo $WEATHER_AGENT_RESULT | jq -r '.id')
    echo "Weather Agent ID: $WEATHER_AGENT_ID"
else
    echo "Failed to deploy Weather Agent"
    WEATHER_AGENT_ID="failed"
fi

# Clean up temporary files
rm -f chat_agent.json weather_agent.json

# Save deployment info
echo "Saving deployment information..."
cat > deployment_info.json << EOF
{
  "chat_agent_id": "$CHAT_AGENT_ID",
  "weather_agent_id": "$WEATHER_AGENT_ID",
  "project_host": "$AZURE_AI_PROJECT_HOST",
  "project_name": "$AZURE_AI_PROJECT_NAME"
}
EOF

echo "Deployment info saved to deployment_info.json"

# List deployed agents
echo "Listing all agents..."
az rest --method get \
  --url "https://management.azure.com/subscriptions/$AZURE_SUBSCRIPTION_ID/resourceGroups/$AZURE_RESOURCE_GROUP/providers/Microsoft.CognitiveServices/accounts/$AZURE_AI_PROJECT_NAME/azureAIAgents?api-version=2023-05-01" \
  --output json | jq '.value[] | {name: .name, id: .id}'

echo ""
echo "You can now interact with your agents using:"
echo "python3 src/scripts/interact_deployed_agents.py"