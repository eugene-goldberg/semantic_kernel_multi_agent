from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

from src.agents.chat_agent import ChatAgent
from src.agents.weather_agent import WeatherAgent

class OrchestratorAgent:
    """
    Orchestrator agent that routes requests to appropriate specialist agents.
    """
    
    def __init__(self, service=None):
        """
        Initialize orchestrator with specialist agents
        
        Args:
            service: An optional pre-configured service
        """
        if service is None:
            # Create a new service if none is provided
            service = AzureChatCompletion()
        
        # Create a kernel with filters for debugging
        kernel = Kernel()
        
        # Create specialist agents
        chat_agent = ChatAgent(service).get_agent()
        weather_agent = WeatherAgent(service).get_agent()
        
        # Create the orchestrator agent
        self.agent = ChatCompletionAgent(
            service=service,
            kernel=kernel,
            name="OrchestratorAgent",
            instructions=(
                "You are a triage agent that routes user requests to the appropriate specialist agent. "
                "If the request is about weather or forecast information for US locations, direct it to the WeatherAgent. "
                "Note that the WeatherAgent can only provide weather data for locations within the United States "
                "as it uses the National Weather Service API. "
                "For all other general questions or conversations, direct it to the ChatAgent. "
                "Your job is to determine which specialist can best answer the query and route "
                "accordingly. Do not try to answer questions yourself - your role is purely to route "
                "requests to the appropriate specialist."
            ),
            plugins=[chat_agent, weather_agent],
        )
    
    def get_agent(self):
        """Get the underlying ChatCompletionAgent"""
        return self.agent