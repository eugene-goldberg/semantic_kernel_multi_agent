#!/usr/bin/env python3
"""
A mock demonstration of the orchestration capability without requiring actual API access.
This script simulates how the chat agent would delegate to the weather agent.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from src.services.weather_service import WeatherService

async def simulate_chat_agent(user_input, weather_service):
    """Simulate chat agent behavior with weather delegation"""
    print(f"\nUser: {user_input}")
    
    # Check if this is a weather-related query
    weather_keywords = ["weather", "temperature", "forecast", "rain", "snow", "sunny", "cloudy"]
    is_weather_query = any(keyword in user_input.lower() for keyword in weather_keywords)
    
    if is_weather_query:
        # Extract location from query (simplified)
        location = None
        if "in " in user_input:
            location = user_input.split("in ")[1].strip().rstrip('?.,!')
        
        if location:
            print(f"\n[Chat Agent]: Detected weather query about location: {location}")
            print("[Chat Agent]: Delegating to Weather Agent...")
            
            # Call the weather service directly to get the data
            weather_type = "forecast" if "tomorrow" in user_input.lower() else "current"
            weather_data = await simulate_weather_agent(location, weather_type, weather_service)
            
            # Simulate chat agent incorporating the weather data into its response
            if weather_type == "current":
                response = f"Based on information from the Weather Agent, the current weather in {location} is {weather_data['description']} with a temperature of {weather_data['temperature']}°F."
            else:
                response = f"According to the Weather Agent's forecast for {location}, you can expect {weather_data['description']} with temperatures around {weather_data['temperature']}°F."
        else:
            response = "I'd be happy to tell you about the weather, but I need to know which location you're asking about."
    else:
        # Simulate responding to a general query
        if "capital of france" in user_input.lower():
            response = "The capital of France is Paris."
        elif "pasta" in user_input.lower():
            response = "To make pasta, boil water, add salt, cook the pasta until al dente, and drain. You can then add your favorite sauce!"
        else:
            response = "I can answer general questions or get weather information for you. For weather queries, just mention a location."
    
    print(f"Agent: {response}")
    return response

async def simulate_weather_agent(location, weather_type, weather_service):
    """Simulate the weather agent getting data from the weather service"""
    print(f"[Weather Agent]: Getting {weather_type} weather for {location}")
    
    try:
        if weather_type == "current":
            weather_data = await weather_service.get_current_weather(location)
            print(f"[Weather Agent]: Retrieved current weather data for {location}")
        else:
            weather_data = await weather_service.get_weather_forecast(location)
            print(f"[Weather Agent]: Retrieved forecast weather data for {location}")
        
        return {
            "location": location,
            "temperature": weather_data.get("temperature", "unknown"),
            "description": weather_data.get("description", "unknown conditions"),
            "type": weather_type
        }
    except Exception as e:
        print(f"[Weather Agent]: Error getting weather data: {str(e)}")
        return {
            "location": location,
            "temperature": "N/A",
            "description": "unavailable at the moment",
            "type": weather_type
        }

async def run_orchestration_demo():
    """Run the orchestration demo with predefined inputs"""
    # Load environment variables (for weather service)
    load_dotenv()
    
    # Create the weather service
    weather_service = WeatherService()
    
    # Test cases
    test_inputs = [
        "What's the capital of France?",
        "What's the weather like in Seattle?",
        "Will it rain tomorrow in Chicago?",
        "Tell me about the weather in New York",
        "How do I make pasta?"
    ]
    
    print("Starting Multi-Agent Orchestration Demo")
    print("This demonstrates how the chat agent delegates weather queries to the weather agent")
    print("-" * 70)
    
    for user_input in test_inputs:
        print("\n" + "-" * 70)
        await simulate_chat_agent(user_input, weather_service)

async def main():
    """Main entry point"""
    try:
        await run_orchestration_demo()
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())