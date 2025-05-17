# Azure OpenAI Scripts (Legacy)

This directory contains scripts that were previously used for deploying and interacting with agents using Azure OpenAI service. These files have been moved here as part of our migration to Azure AI Foundry.

## Directory Structure

### Azure OpenAI Scripts

The `src/scripts/` directory contains scripts that directly use Azure OpenAI API:

- `check_openai_resources.py` - Verifies OpenAI resources in Azure
- `deploy_azure_rest.py` - Exploratory script using Azure REST API
- `deploy_openai_assistants.py` - Deploys agents as OpenAI Assistants
- `deploy_orchestration.py` - Creates an orchestrator using Azure OpenAI
- `deploy_orchestration_openai.py` - Creates orchestrator with OpenAI Assistants API
- `interact_openai_agents.py` - Interface for Azure OpenAI agents
- `interact_openai_assistants.py` - Interface for OpenAI assistants
- `interact_orchestrated_agents.py` - For OpenAI orchestrated agents

### Transitional Scripts

The `transitional/` directory contains scripts that may still be partially relevant:

- `transitional/src/scripts/deploy_orchestrator.py` - Deploys orchestrator to Azure AI Service
- `transitional/src/scripts/interact_sk_agents.py` - For SK-based agents

## Current Approach

The project has migrated from using Azure OpenAI service directly to Azure AI Foundry. The current implementation uses:

- `src/scripts/deploy_ai_foundry_agents.py` - For deploying agents
- `src/utils/ai_foundry_deployment_manager.py` - For managing deployments
- `src/scripts/interact_ai_foundry_agents.py` - For interacting with deployed agents

These files have been moved here for reference but are not actively used in the current implementation.