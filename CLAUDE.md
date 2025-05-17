# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project is a multi-agent application built using Microsoft Semantic Kernel SDK with deployment to Azure AI Service. It implements a standardized approach for creating, testing, and deploying various specialist agents (Chat, Weather, Calculator) using the Semantic Kernel framework exclusively.

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
# Run the SK orchestration test suite
python src/scripts/test_sk_orchestration.py

# Run the SK orchestration example
python src/scripts/orchestrate_with_sk.py

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
# Deploy all SK-based agents to Azure AI Service
python src/scripts/deploy_sk_agents.py

# Deploy specific agent (chat, weather, calculator, or orchestrator)
python src/scripts/deploy_sk_agents.py [agent_type]

# Display agent configuration information
python src/scripts/deploy_sk_agents.py info
```

### Testing and Interaction

```bash
# Test local SK-based agent orchestration
python src/scripts/test_sk_orchestration.py

# Chat with deployed SK agents
python src/scripts/interact_sk_agents.py

# SK-based orchestration (local)
python src/scripts/orchestrate_with_sk.py
```

## Project Structure

The codebase is organized into several key modules:

### Agents Module

Located in `src/agents/`, this module defines SK-based agent types:
- `chat_agent.py`: Implements general conversation agent using SK
- `weather_agent.py`: Implements weather specialist agent using SK
- `calculator_agent_sk.py`: Implements calculator specialist agent using SK
- `orchestrator_agent_updated.py`: Routes requests to appropriate agents using SK
- `plugins/weather_plugin.py`: SK plugin for weather functionality
- `plugins/calculator_plugin.py`: SK plugin for calculator functionality

### Services Module

Located in `src/services/`, this module handles external service integration:
- `weather_service.py`: Service for interacting with weather API

### Utils Module

Located in `src/utils/`, this module provides SK-based utilities:
- `sk_agent_factory.py`: Creates standardized SK agents
- `sk_deployment_manager.py`: Manages deployment of SK agents to Azure

### API Module

Located in `src/api/`, this module implements HTTP interface:
- `server.py`: FastAPI server for remote interaction

### Config Module

Located in `src/config/`, this module handles configuration:
- `settings.py`: Environment variables and configuration helpers
- `agent_configs.py`: Centralized agent configuration for SK-based agents

## Architecture Pattern

The application follows a modular agent architecture pattern:
1. Individual specialist agents with defined roles
2. Orchestrator agent for routing requests
3. Abstractions for both local operation and cloud deployment
4. HTTP API for remote interaction

## Integration Points

Key integration points to be aware of:
1. Weather API integration via `WeatherService` and `WeatherPlugin`
2. Calculator functionality via `CalculatorPlugin`
3. Azure AI Service integration via `SkDeploymentManager`
4. Semantic Kernel integration via all agent classes and plugins

## Agent Orchestration

The project includes a multi-agent orchestration system built with Semantic Kernel 1.30.0:

1. The orchestrator agent routes requests to appropriate specialized agents
2. Weather queries are routed to the weather agent
3. Mathematical calculations are routed to the calculator agent
4. General queries are routed to the chat agent
5. All implementation uses function calling via the Semantic Kernel plugin system
6. The system is designed to be extensible with additional specialized agents

The SK orchestration files are:
- `src/scripts/orchestrate_with_sk.py`: SK-based orchestration implementation
- `src/scripts/test_sk_orchestration.py`: Testing orchestration functionality
- `SK_IMPLEMENTATION_README.md`: Detailed implementation documentation

## IMPORTANT NOTE

**All future development must focus exclusively on the Semantic Kernel (SK) based implementation.** 

Files with the following patterns are part of the SK-based implementation:
- `*_sk_*.py` - SK-specific scripts and tests
- `sk_*.py` - SK utility files
- `*_sk.py` - SK-based agent implementations
- `orchestrator_agent_updated.py` - Updated orchestrator using SK

Do not modify or use any non-SK implementations (such as direct Azure OpenAI API calls) as they are being phased out in favor of the standardized SK approach. This ensures all agents are consistently defined using the Semantic Kernel SDK and properly deploy to Azure AI Service.