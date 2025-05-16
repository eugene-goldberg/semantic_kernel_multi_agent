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
./setup.py
```

### Local Development

```bash
# Run the local chat client (for testing without deployment)
python src/scripts/local_chat.py

# Run tests
python src/scripts/run_tests.py
```

### Azure Infrastructure Setup

```bash
# Automated setup of all required Azure resources
./src/scripts/setup_azure_infrastructure.sh
```

### Deployment

```bash
# Deploy agents to Azure AI Agent Service
python src/scripts/deploy_agents.py
```

### Remote Testing

```bash
# Start API server
python src/scripts/run_api_server.py

# Chat with deployed agents
python src/scripts/remote_chat.py

# Use the API client
python src/scripts/api_client.py info
python src/scripts/api_client.py message --agent chat --message "Hello"

# Use HTTP client
python src/scripts/http_client.py chat --agent chat
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