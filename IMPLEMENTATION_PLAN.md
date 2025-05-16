# Semantic Kernel Agent Implementation Plan

## Current Status Assessment

### Agent Implementations

1. **SK-Based Implementations (Local)**
   - `src/agents/chat_agent.py` - Uses Semantic Kernel patterns
   - `src/agents/weather_agent.py` - Uses Semantic Kernel with weather plugin
   - `src/agents/orchestrator_agent.py` - Uses Semantic Kernel for orchestration
   - `src/agents/calculator_agent.py` - Partially implements SK patterns

2. **Direct OpenAI Implementations (Remote/Deployed)**
   - `src/scripts/deploy_openai_assistants.py` - Uses direct OpenAI API
   - `src/scripts/deploy_calculator_agent.py` - Uses direct OpenAI API
   - `src/scripts/deploy_orchestration_openai.py` - Uses direct OpenAI API

3. **Plugin Status**
   - `src/agents/plugins/weather_plugin.py` - Properly implemented as SK plugin
   - `src/agents/plugins/calculator_plugin.py` - Properly implemented as SK plugin

4. **Configuration & Environment**
   - Semantic Kernel version: 1.30.0
   - OpenAI API version: 2024-02-15-preview
   - Environment files require cleanup (see security recommendations)

## Implementation Plan

### Phase 1: Standardize Agent Implementations (3 days)

#### 1.1 Update Calculator Agent (Day 1)
- Complete the SK implementation of `calculator_agent.py` to match other agents
- Ensure proper integration with `calculator_plugin.py`
- Test calculator functions locally

#### 1.2 Refine Orchestrator Agent (Day 1)
- Update `orchestrator_agent.py` to include Calculator Agent
- Enhance plugin registration for all agents
- Implement consistent routing patterns

#### 1.3 Standardize Agent Initialization (Day 2)
- Create common initialization patterns across all agents
- Implement a factory class for agent creation
- Add documentation and typing for all classes

#### 1.4 Implement Unified Agent Interface (Day 2)
- Create a base agent class with common interfaces
- Ensure consistent method signatures across agents
- Add logging and error handling

### Phase 2: Create SK-Based Deployment System (3 days)

#### 2.1 Create Agent Configuration System (Day 3)
- Create `src/config/agent_configs.py` for centralized configuration
- Implement environment variable handling
- Create deployment settings JSON template

#### 2.2 Implement SK Deployment Manager (Day 3-4)
- Create `src/utils/sk_deployment_manager.py`
- Implement Azure AI Service deployment mechanisms
- Add proper error handling and validation

#### 2.3 Create Unified Deployment Script (Day 4)
- Create `src/scripts/deploy_sk_agents.py`
- Implement separate functions for each agent
- Add deployment verification

#### 2.4 Implement Connection Manager (Day 5)
- Create a connection manager for SK + Azure
- Implement proper authentication handling
- Add retry logic and error recovery

### Phase 3: Client & Interaction Updates (2 days)

#### 3.1 Update Client Scripts (Day 5)
- Create `src/scripts/interact_sk_agents.py`
- Implement SK-based interaction handlers
- Update testing and debugging scripts

#### 3.2 Create Orchestration Client (Day 6)
- Create `src/scripts/orchestrate_sk_agents.py`
- Implement proper threading and async patterns
- Add conversation history management

#### 3.3 Implement Testing Framework (Day 6)
- Create comprehensive test scripts
- Implement agent validation utilities
- Add performance monitoring

### Phase 4: Documentation & Cleanup (2 days)

#### 4.1 Update Documentation (Day 7)
- Update README.md with new SK architecture
- Create detailed deployment guide
- Document agent capabilities and integration points

#### 4.2 Cleanup Legacy Code (Day 7)
- Archive direct OpenAI implementation scripts
- Clean up unused configurations
- Ensure consistent naming conventions

#### 4.3 Final Testing & Validation (Day 8)
- Test end-to-end deployment and operation
- Verify all agent integrations
- Document any limitations or restrictions

## Technical Implementation Details

### 1. Semantic Kernel Configuration

```python
# Example configuration in src/config/agent_configs.py
AGENT_CONFIGS = {
    "chat": {
        "name": "ChatAgent",
        "instructions": "You are a helpful assistant...",
        "deployment_model": "gpt-35-turbo",
        "plugins": []
    },
    "weather": {
        "name": "WeatherAgent",
        "instructions": "You are a weather specialist...",
        "deployment_model": "gpt-35-turbo",
        "plugins": ["WeatherPlugin"]
    },
    "calculator": {
        "name": "CalculatorAgent",
        "instructions": "You are a specialized calculator...",
        "deployment_model": "gpt-35-turbo",
        "plugins": ["CalculatorPlugin"]
    },
    "orchestrator": {
        "name": "OrchestratorAgent",
        "instructions": "You are a triage agent...",
        "deployment_model": "gpt-35-turbo",
        "plugins": ["ChatPlugin", "WeatherPlugin", "CalculatorPlugin"]
    }
}
```

### 2. Agent Factory Pattern

```python
# Example factory in src/utils/agent_factory.py
class SkAgentFactory:
    """Factory class for creating SK-based agents."""
    
    @staticmethod
    def create_agent(agent_type, service=None, kernel=None):
        """Create an agent of the specified type."""
        if agent_type == "chat":
            return ChatAgent(service=service, kernel=kernel)
        elif agent_type == "weather":
            return WeatherAgent(service=service, kernel=kernel)
        elif agent_type == "calculator":
            return CalculatorAgent(service=service, kernel=kernel)
        elif agent_type == "orchestrator":
            return OrchestratorAgent(service=service, kernel=kernel)
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")
```

### 3. Deployment Architecture

```python
# Example deployment in src/scripts/deploy_sk_agents.py
async def deploy_agents():
    """Deploy all agents to Azure AI Service using SK."""
    # Set up Azure credentials
    deployment_settings = SkDeploymentSettings()
    
    # Create kernel with Azure service
    kernel = setup_azure_kernel(deployment_settings)
    
    # Deploy each agent
    deployed_agents = {}
    for agent_type, config in AGENT_CONFIGS.items():
        agent = SkAgentFactory.create_agent(agent_type, kernel=kernel)
        deployment = await SkDeploymentManager.deploy_agent(
            agent=agent,
            settings=deployment_settings,
            config=config
        )
        deployed_agents[agent_type] = deployment.id
    
    # Save deployment info
    save_deployment_info(deployed_agents)
```

## Deliverables

1. **Enhanced Agent Classes**
   - Updated SK-based implementations for all agents
   - Consistent interfaces and patterns
   - Proper plugin integration

2. **Deployment System**
   - SK-based deployment manager
   - Configuration system
   - Authentication handling

3. **Client Scripts**
   - SK-based interaction scripts
   - Orchestration client
   - Testing framework

4. **Documentation**
   - Updated README.md
   - Deployment guide
   - Code documentation

## Verification & Testing

Each phase will include verification steps:

1. **Local Testing**
   - Test each agent functionality locally
   - Verify plugin integrations
   - Test orchestration flows

2. **Deployment Testing**
   - Verify successful deployment to Azure
   - Test remote agent functionality
   - Validate credentials and authentication

3. **Integration Testing**
   - Test end-to-end orchestration
   - Verify client-agent communication
   - Test error handling and recovery

## Migration Strategy

A phased migration approach will be used:
1. Implement SK-based system in parallel
2. Test and validate the new implementation
3. Switch to the new system once fully tested
4. Archive the old implementation for reference