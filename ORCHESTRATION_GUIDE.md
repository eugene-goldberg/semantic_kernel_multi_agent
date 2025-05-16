# Multi-Agent Orchestration with Semantic Kernel

This guide explains how to use the multi-agent orchestration capability built with Semantic Kernel to delegate tasks from a chat agent to specialized agents like the weather agent.

## Overview

The orchestration system allows the main chat agent to:
1. Process user inputs and determine if they need specialized information
2. For weather-related queries, delegate to the weather agent
3. Incorporate specialized information into its response

## Components

The system consists of these key components:

1. **Semantic Kernel**: Provides the orchestration framework and plugin architecture
2. **Chat Agent**: The primary AI assistant that can handle general queries
3. **Weather Plugin**: A specialized plugin that provides weather information 
4. **Function Calling**: The mechanism that enables delegation from chat agent to weather plugin

## Usage

### Running the Orchestration

You can run the orchestration system with the following command:

```bash
python src/scripts/orchestrate_with_kernel.py
```

This script:
- Sets up a kernel with Azure OpenAI
- Registers the weather plugin
- Provides a chat interface where you can interact with the system

### Example Interactions

The chat agent can handle both general questions and weather-related queries:

- **General Query**: "What is the capital of France?"
- **Weather Query**: "What's the weather like in Seattle?"
- **Weather Forecast**: "Will it rain tomorrow in New York?"

When you ask weather-related questions, the system will:
1. Recognize the need for weather information
2. Call the weather plugin's GetWeather function
3. Return the weather information in a conversational format

### Implementation Details

The orchestration system is built with Semantic Kernel 1.30.0 and uses function calling to delegate tasks. Key implementation features:

1. **KernelPlugin Registration**: Weather plugin is registered with the kernel
2. **Function Calling**: Enables the chat agent to call weather functions
3. **Tool Definition**: Weather functions are exposed as LLM tools

## Customization

You can customize this orchestration system by:

1. Adding new plugins for additional specialized capabilities
2. Modifying the system prompt to change how the chat agent delegates tasks
3. Extending the weather plugin to support more weather data

## Troubleshooting

If you encounter issues:

- Check that your Azure OpenAI API key and endpoints are correctly set in .env
- Ensure you're using a compatible Azure OpenAI deployment (API version 2024-05-01-preview or newer)
- Verify that your deployment supports function calling

## Next Steps

To extend this system:
1. Add more specialized plugins
2. Implement a more complex orchestration flow
3. Add memory capabilities to retain conversation context

For more details, see the code in `src/scripts/orchestrate_with_kernel.py`.