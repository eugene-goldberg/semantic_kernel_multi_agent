from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

from src.agents.plugins.weather_plugin import WeatherPlugin

class WeatherAgent:
    """Weather specialist agent that provides weather information"""
    
    def __init__(self, service=None, kernel=None):
        """
        Initialize weather agent with weather plugin
        
        Args:
            service: An optional pre-configured service
            kernel: An optional pre-configured kernel
        """
        if service is None:
            # Create a new service if none is provided
            service = AzureChatCompletion()
        
        # Create a kernel for this agent if not provided
        if kernel is None:
            kernel = Kernel()
        
        # Import the weather plugin
        weather_plugin = WeatherPlugin()
        kernel.import_plugin(weather_plugin, plugin_name="WeatherPlugin")
        
        self.agent = ChatCompletionAgent(
            service=service,
            kernel=kernel,
            name="WeatherAgent",
            instructions=(
                "You are a weather specialist agent that provides accurate and helpful weather information "
                "for locations in the United States. "
                "You have access to real-time US weather data through your WeatherPlugin skills which use "
                "the National Weather Service API. "
                "When asked about weather, always use the appropriate function from WeatherPlugin to get accurate data. "
                "For current weather, use the GetCurrentWeather function. "
                "For forecasts, use the GetWeatherForecast function. "
                "Provide your answers in a friendly, concise manner, focusing on the most relevant information "
                "for the user's query. "
                "If asked about weather outside the United States, politely explain that your weather data "
                "is currently limited to US locations only. "
                "If you're asked something not related to weather, politely explain "
                "that you specialize in weather information only."
            ),
        )
    
    def get_agent(self):
        """Get the underlying ChatCompletionAgent"""
        return self.agent