#!/usr/bin/env python3
"""
Test the weather service directly without using agents.
"""
import os
import sys

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from src.services.weather_service import WeatherService

def main():
    """Main entry point"""
    print("Testing Weather Service...")
    weather_service = WeatherService()
    
    # List of cities with hardcoded coordinates to test
    test_locations = [
        {"name": "Seattle, WA", "lat": 47.6062, "lon": -122.3321},
        {"name": "New York, NY", "lat": 40.7128, "lon": -74.0060},
        {"name": "Miami, FL", "lat": 25.7617, "lon": -80.1918},
        {"name": "San Francisco, CA", "lat": 37.7749, "lon": -122.4194},
        {"name": "Chicago, IL", "lat": 41.8781, "lon": -87.6298}
    ]
    
    for location in test_locations:
        name = location["name"]
        lat = location["lat"]
        lon = location["lon"]
        
        print(f"\nGetting weather for {name} (lat: {lat}, lon: {lon})...")
        
        # Get current weather using coordinates
        try:
            current = weather_service.get_current_weather(lat=lat, lon=lon)
            print(f"Current Weather: {current}")
        except Exception as e:
            print(f"Error getting current weather: {str(e)}")
        
        # Get forecast using coordinates
        try:
            forecast = weather_service.get_forecast(lat=lat, lon=lon, days=3)
            print(f"Weather Forecast: {forecast}")
        except Exception as e:
            print(f"Error getting forecast: {str(e)}")
    
    # Test invalid coordinates (out of US range)
    print("\nTesting non-US location with coordinates...")
    try:
        # Coordinates for London, UK
        non_us = weather_service.get_current_weather(lat=51.5074, lon=-0.1278)
        print(f"Result: {non_us}")
    except Exception as e:
        print(f"Error (expected): {str(e)}")

if __name__ == "__main__":
    main()