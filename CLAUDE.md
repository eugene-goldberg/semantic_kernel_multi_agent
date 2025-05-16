# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project is a multi-agent application built using Microsoft Semantic Kernel SDK and Azure AI Foundry SDK, with deployment to Azure AI Agent Service. It implements a chat completion agent and a weather checking agent that can be deployed and tested through various interfaces.

## Key Commands

### Environment Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the setup script to verify environment
python setup.py

# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Local Development

```bash
# Run the local chat client (for testing without deployment)
python src/scripts/local_chat.py

# Run tests
python src/scripts/run_tests.py

# Run the simple local chat example
python src/scripts/simple_local_chat.py

# Test weather service directly
python src/scripts/test_weather_service.py

# Test weather plugin
python -m tests.test_weather_plugin
```

### Azure Infrastructure Setup

```bash
# Automated setup of all required Azure resources
bash src/scripts/setup_azure_infrastructure.sh

# Check Azure resources status
bash src/scripts/list_azure_resources.sh

# Create service principal for deployment (optional)
bash src/scripts/create_service_principal.sh
```

### Deployment

```bash
# Deploy agents to Azure AI Agent Service using DefaultAzureCredential
python src/scripts/deploy_agents.py

# Deploy agents using Azure CLI (recommended)
bash src/scripts/deploy_agents_az_cli.sh

# Deploy agents using SDK with interactive login
bash src/scripts/deploy_agents_cli.sh

# Deploy and immediately start chatting (all-in-one)
bash src/scripts/deploy_and_chat.sh

# Using Service Principal auth with REST API
python src/scripts/deploy_with_service_principal.py

# Simple deployment script
python src/scripts/simple_deploy.py
```

### Remote Testing and Interaction

```bash
# Start API server
python src/scripts/run_api_server.py

# Chat with deployed agents
python src/scripts/remote_chat.py
python src/scripts/interact_deployed_agents.py

# Use the API client
python src/scripts/api_client.py info
python src/scripts/api_client.py message --agent chat --message "Hello"

# Use HTTP client
python src/scripts/http_client.py chat --agent chat

# Test connectivity to deployed agents
python src/scripts/test_connectivity.py

# Agent orchestration (recommended)
python src/scripts/orchestrate_with_kernel.py
```

## Project Structure

The codebase is organized into several key modules:

### Agents Module

Located in `src/agents/`, this module defines agent types:
- `chat_agent.py`: Implements general conversation agent
- `weather_agent.py`: Implements weather specialist agent 
- `orchestrator_agent.py`: Routes requests to appropriate agents
- `plugins/weather_plugin.py`: SK plugin for weather functionality

### Services Module

Located in `src/services/`, this module handles external service integration:
- `weather_service.py`: Service for interacting with weather API

### Utils Module

Located in `src/utils/`, this module provides factory classes:
- `local_agent_factory.py`: Creates agents for local operation
- `azure_agent_factory.py`: Creates and deploys agents to Azure

### API Module

Located in `src/api/`, this module implements HTTP interface:
- `server.py`: FastAPI server for remote interaction

### Config Module

Located in `src/config/`, this module handles configuration:
- `settings.py`: Environment variables and configuration helpers

## Architecture Pattern

The application follows a modular agent architecture pattern:
1. Individual specialist agents with defined roles
2. Orchestrator agent for routing requests
3. Abstractions for both local operation and cloud deployment
4. HTTP API for remote interaction

## Integration Points

Key integration points to be aware of:
1. Weather API integration via `WeatherService` and `WeatherPlugin`
2. Azure AI Agent Service integration via `AzureAgentFactory`
3. Semantic Kernel integration via agent classes and plugins

## Agent Orchestration

The project includes a multi-agent orchestration system built with Semantic Kernel 1.30.0:

1. The main chat agent can delegate specialized tasks to other agents
2. For weather queries, tasks are automatically routed to the weather agent
3. The implementation uses function calling via the Semantic Kernel plugin system
4. The system is designed to be extensible with additional specialized agents

The orchestration files are:
- `src/scripts/orchestrate_with_kernel.py`: Main implementation file
- `ORCHESTRATION_GUIDE.md`: User documentation
- `ORCHESTRATION_IMPLEMENTATION.md`: Technical implementation details