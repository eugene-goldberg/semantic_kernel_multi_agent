# Semantic Kernel Multi-Agent Application

This project demonstrates building a multi-agent application using Microsoft Semantic Kernel SDK and Azure AI Foundry SDK, with deployment to Azure AI Agent Service and agent orchestration capabilities.

## Features

- Chat completion agent for general conversation
- Weather agent for providing weather information
- Calculator agent for mathematical operations
- **Agent Orchestration**: Capability for chat agent to delegate tasks to specialized agents
- Deployment to Azure AI Agent Service and Azure OpenAI
- Local testing with a CLI client
- Remote testing with API client
- HTTP API server for integrating with other applications

## Project Structure

```
.
├── src/
│   ├── agents/            # Agent definitions
│   │   ├── plugins/       # Semantic Kernel plugins
│   ├── api/               # HTTP API server
│   ├── config/            # Configuration settings
│   ├── scripts/           # CLI and utility scripts
│   │   └── orchestrate_with_kernel.py  # Orchestration implementation
│   ├── services/          # External services like weather API
│   └── utils/             # Utility classes and factories
├── docs/                  # Detailed documentation
├── .env.example           # Example environment variables
├── requirements.txt       # Python dependencies
├── ORCHESTRATION_GUIDE.md # Guide for using orchestration
├── ORCHESTRATION_IMPLEMENTATION.md # Technical details of orchestration
├── deployment.md          # Deployment documentation
└── README.md              # Project documentation
```

## Prerequisites

- Python 3.8+
- Azure subscription
- Azure OpenAI service
- Azure AI Foundry Hub and Project created
- Weather API key (e.g., OpenWeatherMap)

## Setup

1. Clone the repository
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your API keys and configuration:
   ```
   cp .env.example .env
   ```
5. Set up your Azure AI Foundry Hub and Project using one of these approaches:
   - [Azure AI Foundry Portal Setup Guide](docs/azure_ai_foundry_setup.md) for UI-based setup
   - [Azure CLI Setup Guide](docs/azure_cli_setup_guide.md) for command-line based setup
   - Automated setup script (requires Azure CLI):
     ```bash
     ./src/scripts/setup_azure_infrastructure.sh
     ```

## Usage

### Local Development

To run the application locally:

```
python src/scripts/local_chat.py
```

### Deploying to Azure AI Agent Service

There are multiple ways to deploy agents to Azure AI Agent Service:

#### Using Azure CLI (Recommended)

The most reliable way to deploy agents is using the Azure CLI directly:

```bash
# Deploy agents with Azure CLI commands
bash src/scripts/deploy_agents_az_cli.sh
```

This script will:
1. Verify your Azure CLI login status
2. Set the correct subscription
3. Create agent definitions in JSON format
4. Deploy agents using Azure REST API calls through Azure CLI
5. Save deployment information
6. List all deployed agents

#### Using Agent Deployment SDK

For programmatic deployment through the SDK (may require additional setup):

```bash
# Deploy agents with SDK
bash src/scripts/deploy_agents_cli.sh

# If you want to use a service principal, add the --create-sp flag
bash src/scripts/deploy_agents_cli.sh --create-sp
```

This approach uses the Azure AI Projects SDK to deploy agents.

#### Alternative Deployment Methods

We also provide several alternative deployment methods for specific scenarios:

```bash
# Using Service Principal authentication with REST API
python src/scripts/deploy_with_service_principal.py

# All-in-one script to deploy and start chatting
bash src/scripts/deploy_and_chat.sh

# Using DefaultAzureCredential with Semantic Kernel SDK
python src/scripts/deploy_agents.py

# Direct REST API approach
python src/scripts/deploy_rest.py
```

All deployment methods will create agents in your Azure AI Agent Service project and save their IDs to `deployment_info.json`.

See the [Azure Agent Deployment Guide](docs/azure_agent_deployment.md) for detailed instructions.

### Interacting with Deployed Agents

#### Interactive Chat Session

Use the interactive chat client for a continuous conversation with deployed agents:

```bash
python src/scripts/interact_deployed_agents.py
```

In the chat interface:
- Type `exit` to quit
- Type `switch` to change between Chat and Weather agents
- Type `clear` to start a new conversation thread

#### Using Orchestration (NEW)

The orchestration system allows the chat agent to delegate tasks to specialized agents (like the weather agent) using Semantic Kernel:

```bash
python src/scripts/orchestrate_with_kernel.py
```

This provides a more integrated experience where:
- The chat agent automatically detects weather-related queries
- Weather tasks are delegated to the specialized weather agent
- Responses are seamlessly integrated

See [ORCHESTRATION_GUIDE.md](ORCHESTRATION_GUIDE.md) for more details about using the orchestration capability.

#### Using API Client

You can also use the API client for programmatic access:

```bash
# Get information about deployed agents
python src/scripts/api_client.py info

# Send a message to an agent
python src/scripts/api_client.py message --agent chat --message "Hello, how are you?"
python src/scripts/api_client.py message --agent weather --message "What's the weather in Seattle?"
```

Or use the remote chat client:

```bash
python src/scripts/remote_chat.py
```

### HTTP API Server

Start the HTTP API server:

```
cd src/api
uvicorn server:app --reload
```

The API server will be available at http://localhost:8000 with Swagger documentation at http://localhost:8000/docs.

## API Endpoints

- `GET /agents` - Get information about deployed agents
- `POST /message` - Send a message to an agent

## Development Workflow

1. Create a new feature or capability
2. Test locally using `local_chat.py`
3. Deploy to Azure AI Agent Service using `deploy_agents.py`
4. Test the deployed feature using `remote_chat.py` or `api_client.py`
5. Repeat for the next feature

## Agent Orchestration

This project now includes a complete agent orchestration system built with Semantic Kernel. The orchestration allows the main chat agent to delegate specialized tasks to other agents, such as weather information requests.

### Documentation

- [ORCHESTRATION_GUIDE.md](ORCHESTRATION_GUIDE.md): User guide for the orchestration capability
- [ORCHESTRATION_IMPLEMENTATION.md](ORCHESTRATION_IMPLEMENTATION.md): Technical implementation details

### Key Features

- **Function Delegation**: Chat agent detects specialized requests and delegates to appropriate agents
- **Seamless Integration**: Responses are integrated into the conversation flow
- **Extensible Architecture**: New specialized agents can be added to the system
- **Semantic Kernel Integration**: Uses SK 1.30.0's plugin system and function calling

### Example Usage

```bash
python src/scripts/orchestrate_with_kernel.py
```

You can then ask questions like:
- "What's the weather like in Seattle?" (routes to Weather Agent)
- "Will it rain tomorrow in New York?" (routes to Weather Agent)
- "Calculate the square root of 64" (routes to Calculator Agent)
- "What is 15% of 230?" (routes to Calculator Agent)

The chat agent will automatically detect the query type and delegate to the appropriate specialized agent.

## License

This project is licensed under the MIT License.# semantic_kernel_multi_agent
# semantic_kernel_multi_agent
