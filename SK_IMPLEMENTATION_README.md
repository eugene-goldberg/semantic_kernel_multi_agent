# Semantic Kernel Multi-Agent Implementation

This document provides guidance on implementing and using the Semantic Kernel-based multi-agent system.

## Overview

This implementation standardizes all agents using the Microsoft Semantic Kernel SDK, providing a consistent approach for local development, testing, and deployment to Azure AI Service.

## Key Components

### Agent Classes

1. **Chat Agent**
   - Location: `src/agents/chat_agent.py`
   - Purpose: General-purpose conversational agent
   - Dependencies: Semantic Kernel SDK

2. **Weather Agent**
   - Location: `src/agents/weather_agent.py`
   - Purpose: Weather information specialist
   - Dependencies: Weather Plugin, Semantic Kernel SDK

3. **Calculator Agent**
   - Location: `src/agents/calculator_agent_sk.py`
   - Purpose: Mathematical operations specialist
   - Dependencies: Calculator Plugin, Semantic Kernel SDK, NumPy, SciPy, SymPy

4. **Orchestrator Agent**
   - Location: `src/agents/orchestrator_agent_updated.py`
   - Purpose: Routes requests to appropriate specialized agents
   - Dependencies: All specialized agents, Semantic Kernel SDK

### Plugins

1. **Weather Plugin**
   - Location: `src/agents/plugins/weather_plugin.py`
   - Purpose: Provides weather information capabilities
   - Functions: GetCurrentWeather, GetWeatherForecast, GetWeather

2. **Calculator Plugin**
   - Location: `src/agents/plugins/calculator_plugin.py`
   - Purpose: Provides mathematical calculation capabilities
   - Functions: Calculate, MatrixOperation, Statistics, SolveEquation, Calculus, Algebra

### Utilities & Configuration

1. **Agent Factory**
   - Location: `src/utils/sk_agent_factory.py`
   - Purpose: Factory for creating and configuring agents consistently

2. **Deployment Manager**
   - Location: `src/utils/sk_deployment_manager.py`
   - Purpose: Handles deployment of agents to Azure AI Service

3. **Agent Configuration**
   - Location: `src/config/agent_configs.py`
   - Purpose: Centralizes agent configuration for consistent deployment

### Scripts

1. **Deploy SK Agents**
   - Location: `src/scripts/deploy_sk_agents.py`
   - Purpose: Deploys agents to Azure AI Service
   - Usage: `python src/scripts/deploy_sk_agents.py [all|chat|weather|calculator|orchestrator|info|help]`

2. **Interact with SK Agents**
   - Location: `src/scripts/interact_sk_agents.py`
   - Purpose: Interactive chat with deployed agents
   - Usage: `python src/scripts/interact_sk_agents.py`

3. **Test SK Orchestration**
   - Location: `src/scripts/test_sk_orchestration.py`
   - Purpose: Tests local orchestration of agents
   - Usage: `python src/scripts/test_sk_orchestration.py`

## Implementation Details

### Semantic Kernel Setup

```python
# Create kernel with Azure OpenAI service
kernel = sk.Kernel()
service = AzureChatCompletion(
    deployment_name=deployment,
    endpoint=endpoint,
    api_key=api_key,
    api_version="2024-02-15-preview"
)
kernel.add_service(service, service_id="chat")
```

### Plugin Registration

```python
# Example plugin registration
plugin_object = WeatherPlugin()
plugin = KernelPlugin.from_object(
    "WeatherPlugin",
    plugin_object,
    description="Provides weather information"
)
kernel.plugins["WeatherPlugin"] = plugin
```

### Agent Creation

```python
# Example agent creation
agent = ChatCompletionAgent(
    service=service,
    kernel=kernel,
    name="AgentName",
    instructions="Detailed instructions for the agent..."
)
```

## Setup Instructions

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment variables:
   - Copy `.env.sample` to `.env`
   - Add your Azure OpenAI credentials

3. Test local orchestration:
   ```bash
   python src/scripts/test_sk_orchestration.py
   ```

4. Deploy to Azure AI Service:
   ```bash
   python src/scripts/deploy_sk_agents.py
   ```

5. Interact with deployed agents:
   ```bash
   python src/scripts/interact_sk_agents.py
   ```

## Agent Configuration

Agent configuration is centralized in `src/config/agent_configs.py`, making it easy to update agent behavior, instructions, and plugin dependencies in one place.

## Deployment Process

The deployment process follows these steps:
1. Create service and kernel using Azure credentials
2. Configure plugins and specialized capabilities
3. Create agents with appropriate instructions
4. Deploy agents to Azure AI Service
5. Save deployment information for future use

## Orchestration Flow

The orchestration flow works as follows:
1. User sends query to the orchestrator
2. Orchestrator analyzes query content
3. Orchestrator delegates to the appropriate specialized agent:
   - Weather Agent for weather-related queries
   - Calculator Agent for mathematical operations
   - Chat Agent for general conversation
4. Specialized agent processes the query
5. Response is returned to the user

## Customization

To add a new specialized agent:
1. Create a new agent class in `src/agents/`
2. Create a new plugin in `src/agents/plugins/`
3. Update `src/config/agent_configs.py` with the new agent configuration
4. Update `src/agents/orchestrator_agent_updated.py` with routing logic
5. Update `src/utils/sk_agent_factory.py` to include the new agent

## Troubleshooting

Common issues and solutions:
- **Authentication Errors**: Verify Azure OpenAI credentials in `.env`
- **Plugin Loading Errors**: Ensure proper plugin registration in the kernel
- **Deployment Failures**: Check Azure resource permissions and quota
- **Orchestration Issues**: Verify routing logic in the orchestrator agent