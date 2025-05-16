from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from src.config.settings import AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT_NAME
from src.agents.chat_agent import ChatAgent
from src.agents.weather_agent import WeatherAgent
from src.agents.orchestrator_agent import OrchestratorAgent

class LocalAgentFactory:
    """Factory class for creating local agents using Semantic Kernel"""
    
    @staticmethod
    def create_chat_service():
        """Create and configure an Azure OpenAI chat service"""
        if not all([AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT_NAME]):
            raise ValueError("Azure OpenAI configuration is incomplete.")
        
        return AzureChatCompletion(
            deployment_name=AZURE_OPENAI_DEPLOYMENT_NAME,
            endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY
        )
    
    @staticmethod
    def create_chat_agent():
        """Create a chat agent"""
        service = LocalAgentFactory.create_chat_service()
        return ChatAgent(service)
    
    @staticmethod
    def create_weather_agent():
        """Create a weather agent"""
        service = LocalAgentFactory.create_chat_service()
        return WeatherAgent(service)
    
    @staticmethod
    def create_orchestrator_agent():
        """Create an orchestrator agent with all specialist agents"""
        service = LocalAgentFactory.create_chat_service()
        return OrchestratorAgent(service)