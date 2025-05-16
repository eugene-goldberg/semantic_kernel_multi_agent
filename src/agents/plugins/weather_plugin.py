import json
from typing import Optional
from semantic_kernel.functions import kernel_function
from src.services.weather_service import WeatherService

class WeatherPlugin:
    """Plugin that provides weather information using the National Weather Service API."""
    
    def __init__(self, weather_service=None):
        # Use provided weather service or create a new instance
        self.weather_service = weather_service if weather_service else WeatherService()
    
    @kernel_function(
        description="Get the current weather for a US city",
        name="GetCurrentWeather"
    )
    def get_current_weather(self, city: str) -> str:
        """
        Get the current weather for a specific city in the US.
        
        Args:
            city (str): The name of the city to get weather for (must be in the USA)
            
        Returns:
            str: JSON string with weather information
        """
        try:
            weather_data = self.weather_service.get_current_weather(city=city)
            
            # The weather_data is already processed in the service
            return json.dumps(weather_data, indent=2)
        except Exception as e:
            return (f"Error retrieving weather information: {str(e)}\n"
                   f"Note: This weather service only works for US locations.")
    
    @kernel_function(
        description="Get the weather forecast for a US city",
        name="GetWeatherForecast"
    )
    def get_weather_forecast(self, city: str, days: Optional[int] = 3) -> str:
        """
        Get the weather forecast for a specific city in the US.
        
        Args:
            city (str): The name of the city to get weather forecast for (must be in the USA)
            days (int, optional): Number of days for forecast. Defaults to 3.
            
        Returns:
            str: JSON string with forecast information
        """
        try:
            # Ensure days is an integer
            days = int(days)
            
            forecast_data = self.weather_service.get_forecast(city=city, days=days)
            
            # The forecast_data is already processed in the service
            return json.dumps(forecast_data, indent=2)
        except Exception as e:
            return (f"Error retrieving forecast information: {str(e)}\n"
                   f"Note: This weather service only works for US locations.")
    
    @kernel_function(
        description="Get weather information for a location (current or forecast)",
        name="GetWeather"
    )
    def get_weather(self, location: str, type: Optional[str] = "current") -> str:
        """
        General function to get weather information, either current or forecast.
        This is the main function that will be called by the chat agent.
        
        Args:
            location (str): The city and state, e.g. Seattle, WA
            type (str): Either "current" or "forecast"
            
        Returns:
            str: Weather information as a formatted string
        """
        try:
            # Clean up the location
            location = location.strip()
            
            # Determine which type of weather information to get
            if type.lower() == "forecast":
                result = self.weather_service.get_forecast(city=location, days=3)
                
                # Format the forecast data into a readable string
                forecast_str = f"Weather forecast for {location}:\n"
                
                for day in result.get("forecast", [])[:3]:  # First 3 days
                    name = day.get("name", "Unknown")
                    temp = day.get("temperature", "N/A")
                    condition = day.get("description", "Unknown")
                    forecast_str += f"- {name}: {temp}°F, {condition}\n"
                
                return forecast_str
            else:
                # Default to current weather
                result = self.weather_service.get_current_weather(city=location)
                
                # Format the current weather data into a readable string
                temp = result.get("temperature", "N/A")
                condition = result.get("description", "Unknown")
                wind = result.get("wind_speed", "N/A")
                wind_dir = result.get("wind_direction", "")
                
                return (f"Current weather in {location}: {temp}°F, {condition}, "
                        f"Wind: {wind} mph {wind_dir}")
                
        except Exception as e:
            return (f"Error retrieving weather information: {str(e)}\n"
                   f"Note: This weather service only works for US locations.")