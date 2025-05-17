# Architectural Diagram Prompt: Semantic Kernel Multi-Agent System on Azure

## Overview

Create a detailed architectural diagram of our Semantic Kernel multi-agent system deployed on Azure OpenAI. The diagram should illustrate the complete system architecture, including all components, communication flows, and integration points.

## System Components

### 1. Client Applications
- **Interactive CLI Client**: Python-based command-line interface for interacting with deployed agents
- **HTTP API Server**: FastAPI server providing RESTful endpoints for agent interaction
- **Orchestration Client**: Client interface for the multi-agent orchestration system

### 2. Agent Components
- **Chat Agent (asst_Psx1vZD4DDuuuuI2Dwk4OkOL)**: General-purpose conversational agent
- **Weather Agent (asst_qzuXJV5Y3y61iUVpAJn2LU54)**: Specialized agent for weather information
- **Calculator Agent (asst_wfHsDnDao5nEtcq5OFqMdWcT)**: Specialized agent for mathematical operations
- **Orchestrator Agent (asst_UveL0nlfSE4CqHODnKIPqf59)**: Meta-agent that analyzes queries and routes them to specialized agents

### 3. Azure Services
- **Azure OpenAI**: Hosts the deployed assistant agents
  - Model: GPT-4 or GPT-3.5 Turbo
  - API Version: 2024-02-15-preview
- **Azure Key Vault** (optional): For securely storing API keys and credentials
- **Azure App Service** (optional): For hosting the HTTP API server

### 4. External Services
- **National Weather Service API**: Provides weather data for the Weather Agent

### 5. Local Development Components
- **Semantic Kernel SDK**: Provides orchestration capabilities
- **Weather Plugin**: SK plugin integrating with weather service
- **Calculator Plugin**: SK plugin for mathematical operations

## Communication Flows

1. **User Query Flow**:
   - User submits query to Orchestration Client
   - Orchestration Client creates a thread in Azure OpenAI
   - Query is sent to the Orchestrator Agent
   - Orchestrator analyzes the query and determines the appropriate agent
   - Query is routed to the specialized agent (Chat, Weather, or Calculator)
   - Response is returned to the user

2. **Weather Information Flow**:
   - Weather Agent receives weather-related query
   - Weather Plugin makes API call to National Weather Service
   - Weather data is processed and formatted
   - Response is returned to the Orchestrator
   - Orchestrator presents response to the user

3. **Calculator Processing Flow**:
   - Calculator Agent receives mathematical query
   - Mathematical operation is identified and processed
   - Step-by-step calculation is performed
   - Result is formatted with explanation
   - Response is returned to the Orchestrator
   - Orchestrator presents response to the user

4. **Deployment Flow**:
   - Deployment scripts communicate with Azure OpenAI
   - Agents are created with specific instructions and capabilities
   - Deployment information is stored in configuration files
   - Client applications connect to deployed agents using stored IDs

## Key Integration Points

1. **Azure OpenAI Integration**:
   - Authentication via API Keys
   - Thread-based conversation management
   - Assistant API for agent deployment and management

2. **Semantic Kernel Integration**:
   - Plugin registration for specialized capabilities
   - Function calling for delegation between agents
   - Prompt templates for consistent agent responses

3. **External API Integration**:
   - RESTful API calls to National Weather Service
   - JSON response parsing and formatting

## Technical Specifications

- **Architecture Pattern**: Microservices-based with specialized agents
- **Deployment Model**: Cloud-based deployment on Azure
- **Authentication**: API Key authentication for Azure OpenAI
- **Programming Language**: Python 3.8+
- **Key Libraries**:
  - Semantic Kernel 1.30.0
  - Azure OpenAI SDK
  - FastAPI for HTTP server
  - NumPy, SciPy, SymPy for Calculator functionality

## Agent Orchestration Details

The diagram should emphasize the Orchestrator's central role:

1. **Query Analysis**:
   - Natural language understanding to identify query intent
   - Pattern matching for specialized queries (weather, calculations)
   - Decision logic for routing to appropriate agent

2. **Agent Selection Logic**:
   - Weather-related terms route to Weather Agent
   - Mathematical expressions route to Calculator Agent
   - General knowledge queries route to Chat Agent

3. **Response Integration**:
   - Specialized agent responses are captured by the Orchestrator
   - Responses are formatted consistently
   - Presented to the user through the client interface

## Deployment Configuration

- **Region**: Azure OpenAI deployment region
- **Model Deployment**: GPT-4 or GPT-3.5 Turbo
- **API Version**: 2024-02-15-preview
- **Endpoint**: sk-multi-agent-openai.openai.azure.com

## Design Considerations

- Use distinct colors for different agent types
- Show clear data flow directions with arrows
- Include deployment details where relevant
- Highlight integration points between components
- Show thread-based conversation management
- Include cloud boundaries to indicate Azure services

## Diagram Style Guide

- **Component Types**:
  - Users/Clients: Stick figures or computer icons
  - Agents: AI or robot icons with distinctive colors
  - Azure Services: Azure service icons
  - External APIs: API or cloud icons
  - SDK Components: Library or code icons

- **Connection Types**:
  - API Calls: Solid lines with arrows
  - Data Flow: Dashed lines with arrows
  - Deployment Actions: Dotted lines with arrows

- **Labels**:
  - Include agent IDs where relevant
  - Show API versions for Azure services
  - Label key communication protocols (REST, JSON)
  - Include brief function descriptions

## Sample Interaction Flow to Illustrate

To help visualize the system in action, please include a representation of this sample interaction:

1. User asks: "What's the square root of 64?"
2. Orchestrator Agent analyzes the query and identifies it as a mathematical question
3. Orchestrator routes the query to the Calculator Agent
4. Calculator Agent processes the query and computes the square root
5. Calculator Agent returns "8" with explanation
6. Response is presented to the user

Include another example for weather:

1. User asks: "What's the weather in Seattle?"
2. Orchestrator Agent analyzes the query and identifies it as a weather question
3. Orchestrator routes the query to the Weather Agent
4. Weather Agent contacts the National Weather Service API
5. Weather data is processed and formatted
6. Response is presented to the user

This comprehensive architectural diagram will provide a clear visualization of our multi-agent system's structure, behavior, and integration points in the Azure environment.