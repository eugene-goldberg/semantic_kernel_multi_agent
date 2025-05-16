# Semantic Kernel Multi-Agent Deployment Guide

This guide summarizes the current status of the project and provides recommendations for proceeding with deployment.

## Current Status Summary

1. **Working Components**
   - Weather Service: Successfully retrieves US weather data using National Weather Service API
   - Project Structure: Well-organized with proper separation of concerns
   - Azure OpenAI: Successfully set up with gpt-35-turbo model
   - Local Testing: Weather service works with hardcoded coordinates

2. **Deployment Challenges**
   - Azure AI Agent Service authentication issues:
     - DefaultAzureCredential token expiration: "refresh token has expired due to inactivity"
     - Service Principal authentication errors: "resource principal named https://aiagent.azure.net was not found"
   - API version compatibility issues with Azure AI Agent Service

## Recommended Deployment Approach

Based on our exploration, we recommend the following approaches:

### Option 1: Use Azure Portal (Recommended)

1. Go to Azure AI Studio at https://ai.azure.com
2. Navigate to your project
3. Create two new agents manually:
   - Chat Agent: A general-purpose assistant
   - Weather Agent: A specialized weather agent for US locations

After creating the agents through the portal, you can interact with them using:
```bash
python src/scripts/interact_deployed_agents.py
```

### Option 2: Use Local Development

Run the application locally without deployment:
```bash
python src/scripts/local_chat.py
```

This runs the agents locally using your Azure OpenAI service.

### Option 3: Fix Authentication and Try Again

If you want to continue with programmatic deployment:

1. Refresh Azure CLI credentials:
```bash
az login
```

2. Ensure proper API permissions are set for your service principal
```bash
az role assignment create --assignee <principal-id> --role "AI Service Azure OpenAI Contributor" --scope /subscriptions/<subscription-id>
```

3. Try deployment again:
```bash
python src/scripts/deploy_with_service_principal.py
```

## Diagnosing Azure Resources

To explore your Azure resources and diagnose issues:

```bash
python src/scripts/deploy_azure_rest.py
```

This script will analyze available resources and provide information about:
- Azure OpenAI deployments
- AI workspaces and projects
- Resource access and API compatibility

## Weather Service Functionality

To verify that the weather service is working correctly:

```bash
python src/scripts/test_weather_direct.py
```

This script tests the weather service with hardcoded coordinates for US cities, demonstrating that the core functionality works even when deployed agents are not available.

## Next Steps

1. Complete deployment through Azure Portal manually
2. Test interaction with deployed agents
3. Add the Weather plugin to deployed agents
4. Refine agent instructions for optimal performance