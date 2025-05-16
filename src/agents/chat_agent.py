from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

class ChatAgent:
    """Chat agent that handles general conversation using SK"""
    
    def __init__(self, service=None):
        """
        Initialize chat agent with Azure OpenAI service
        
        Args:
            service: An optional pre-configured service
        """
        if service is None:
            # Create a new service if none is provided
            service = AzureChatCompletion()
            
        self.agent = ChatCompletionAgent(
            service=service,
            name="ChatAgent",
            instructions=(
                "You are a helpful assistant that provides friendly, concise, and accurate information. "
                "You should be conversational but prioritize accuracy and brevity over verbosity. "
                "If you don't know something, admit it clearly rather than making guesses. "
                "If the question is about weather information, inform the user that you'll need to "
                "ask a specialist weather agent to get accurate weather data."
            ),
        )
    
    def get_agent(self):
        """Get the underlying ChatCompletionAgent"""
        return self.agent