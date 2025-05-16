#!/usr/bin/env python3
"""
Minimal test script for Semantic Kernel weather plugin.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv
import semantic_kernel as sk
from semantic_kernel.functions.kernel_arguments import KernelArguments

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from src.agents.plugins.weather_plugin import WeatherPlugin
from src.services.weather_service import WeatherService

def configure_kernel():
    """Set up the Semantic Kernel with basic configuration"""
    # Set environment variables
    os.environ["AZURE_OPENAI_ENDPOINT"] = "https://sk-multi-agent-openai.openai.azure.com/"
    os.environ["AZURE_OPENAI_API_KEY"] = "48d4df6c7b5a49f38d7675620f8e3aa0"
    os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"] = "gpt-35-turbo"
    
    # Create kernel
    kernel = sk.Kernel()
    return kernel

async def test_weather_plugin():
    """Test the weather plugin directly without chat completion"""
    print("Initializing kernel...")
    kernel = configure_kernel()
    
    print("Creating weather plugin...")
    # Create the weather service
    weather_service = WeatherService()
    
    # Create the weather plugin
    weather_plugin_obj = WeatherPlugin(weather_service)
    
    # Register the plugin with the kernel
    from semantic_kernel.functions import KernelPlugin
    
    weather_plugin = KernelPlugin.from_object(
        "WeatherPlugin",  # Plugin name
        weather_plugin_obj,  # Plugin instance
        description="Provides weather information for US cities"
    )
    
    # Add the plugin to the kernel
    kernel.plugins["WeatherPlugin"] = weather_plugin
    
    # Test each function in the weather plugin
    try:
        print("\nTesting GetCurrentWeather...")
        current_weather_function = weather_plugin["GetCurrentWeather"]
        current_weather_args = KernelArguments(city="Seattle, WA")
        current_weather_result = await kernel.invoke(current_weather_function, arguments=current_weather_args)
        print(f"Result: {current_weather_result}")
    except Exception as e:
        print(f"Error in GetCurrentWeather: {str(e)}")
    
    try:
        print("\nTesting GetWeatherForecast...")
        forecast_function = weather_plugin["GetWeatherForecast"]
        forecast_args = KernelArguments(city="New York, NY", days=2)
        forecast_result = await kernel.invoke(forecast_function, arguments=forecast_args)
        print(f"Result: {forecast_result}")
    except Exception as e:
        print(f"Error in GetWeatherForecast: {str(e)}")
    
    try:
        print("\nTesting GetWeather...")
        weather_function = weather_plugin["GetWeather"]
        
        # Test current weather
        current_args = KernelArguments(location="Chicago, IL", type="current")
        current_result = await kernel.invoke(weather_function, arguments=current_args)
        print(f"Current Weather: {current_result}")
        
        # Test forecast
        forecast_args = KernelArguments(location="Miami, FL", type="forecast")
        forecast_result = await kernel.invoke(weather_function, arguments=forecast_args)
        print(f"Forecast: {forecast_result}")
    except Exception as e:
        print(f"Error in GetWeather: {str(e)}")
    
    print("\nWeather plugin test complete!")

async def main():
    """Main entry point"""
    try:
        await test_weather_plugin()
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())