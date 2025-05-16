#!/usr/bin/env python3
"""
Simple local chat implementation that connects directly to Azure OpenAI
without using the agent deployment. This demonstrates the core functionality
even if the agent deployment is not working.
"""

import os
import sys
import argparse
from dotenv import load_dotenv
import openai
from openai import AzureOpenAI

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from src.services.weather_service import WeatherService

def get_client():
    """Get Azure OpenAI client"""
    # Load environment variables
    load_dotenv()
    
    # Get Azure OpenAI configuration
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    if not all([endpoint, api_key, deployment]):
        raise ValueError("Azure OpenAI configuration not found in .env file")
    
    # Create client
    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version="2023-07-01-preview"
    )
    
    return client, deployment

def handle_weather_query(query):
    """Handle a weather-related query using the weather service"""
    # Extract location from query (simple approach)
    query = query.lower()
    
    # US cities with their coordinates
    cities = {
        "seattle": (47.6062, -122.3321),
        "new york": (40.7128, -74.0060),
        "los angeles": (34.0522, -118.2437),
        "chicago": (41.8781, -87.6298),
        "houston": (29.7604, -95.3698),
        "miami": (25.7617, -80.1918),
        "san francisco": (37.7749, -122.4194),
        "boston": (42.3601, -71.0589),
        "denver": (39.7392, -104.9903),
        "austin": (30.2672, -97.7431)
    }
    
    # Find the first city mentioned in the query
    found_city = None
    found_coords = None
    
    for city, coords in cities.items():
        if city in query:
            found_city = city
            found_coords = coords
            break
    
    if not found_city:
        return "I couldn't identify a US city in your query. Please specify a US city like Seattle, New York, or Chicago."
    
    try:
        # Initialize weather service
        weather_service = WeatherService()
        
        # Get weather data
        if "forecast" in query:
            # Get forecast
            forecast_data = weather_service.get_forecast(lat=found_coords[0], lon=found_coords[1])
            
            # Format the response
            result = f"Weather forecast for {found_city.title()}:\n"
            for day in forecast_data["forecast"][:3]:  # First 3 days
                name = day.get("name", "Unknown")
                temp = day.get("temperature", "N/A")
                condition = day.get("description", "Unknown")
                result += f"- {name}: {temp}°F, {condition}\n"
            
            return result
        else:
            # Get current weather
            current_data = weather_service.get_current_weather(lat=found_coords[0], lon=found_coords[1])
            
            # Format the response
            temp = current_data.get("temperature", "N/A")
            condition = current_data.get("description", "Unknown")
            wind = current_data.get("wind_speed", "N/A")
            wind_dir = current_data.get("wind_direction", "")
            
            return f"Current weather in {found_city.title()}: {temp}°F, {condition}, Wind: {wind} mph {wind_dir}"
    
    except Exception as e:
        return f"Error getting weather information: {str(e)}"

def run_chat():
    """Run a simple chat interface"""
    print("=== Simple Local Chat ===")
    print("This chat connects directly to Azure OpenAI with weather capability.")
    print("Type 'exit' to quit.")
    print()
    
    try:
        # Initialize OpenAI client
        client, deployment = get_client()
        
        # Initialize chat history
        messages = [
            {"role": "system", "content": "You are a helpful assistant with access to weather information. If the user asks about weather, you'll respond with accurate weather data."}
        ]
        
        while True:
            # Get user input
            user_input = input("You: ")
            
            # Check for exit
            if user_input.lower() == "exit":
                print("Goodbye!")
                break
            
            # Add user message to history
            messages.append({"role": "user", "content": user_input})
            
            # Check if this is a weather query
            if "weather" in user_input.lower():
                weather_response = handle_weather_query(user_input)
                print(f"Weather Service: {weather_response}")
                messages.append({"role": "assistant", "content": weather_response})
                continue
            
            # Send to OpenAI
            response = client.chat.completions.create(
                model=deployment,
                messages=messages,
                temperature=0.7,
                max_tokens=800,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None
            )
            
            # Get and print response
            assistant_message = response.choices[0].message.content
            print(f"Assistant: {assistant_message}")
            
            # Add to history
            messages.append({"role": "assistant", "content": assistant_message})
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    run_chat()