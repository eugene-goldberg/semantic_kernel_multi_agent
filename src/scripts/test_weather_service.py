#!/usr/bin/env python3
import asyncio
import os
import sys
import json

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from src.services.weather_service import WeatherService

def test_weather_service():
    """Test the weather service directly"""
    print("Testing Weather Service...")
    weather_service = WeatherService()
    
    # Test US cities with hardcoded coordinates to avoid geocoding API limitations
    test_locations = [
        {"city": "Seattle", "lat": 47.6062, "lon": -122.3321},
        {"city": "New York", "lat": 40.7128, "lon": -74.0060},
        {"city": "Los Angeles", "lat": 34.0522, "lon": -118.2437},
        {"city": "Miami", "lat": 25.7617, "lon": -80.1918},
        {"city": "Chicago", "lat": 41.8781, "lon": -87.6298}
    ]
    
    for location in test_locations:
        city = location["city"]
        lat = location["lat"]
        lon = location["lon"]
        
        print(f"\nGetting weather for {city} using coordinates ({lat}, {lon})...")
        try:
            # Get current weather
            current_weather = weather_service.get_current_weather(lat=lat, lon=lon)
            print(f"Current Weather near {city}:")
            print(json.dumps(current_weather, indent=2))
            
            # Get forecast
            forecast = weather_service.get_forecast(lat=lat, lon=lon, days=2)
            print(f"Forecast near {city} (2 days):")
            print(f"  Total periods: {len(forecast['forecast'])}")
            if forecast['forecast']:
                print(f"  First period: {forecast['forecast'][0]['name']} - {forecast['forecast'][0]['description']}")
            
        except Exception as e:
            print(f"Error for {city}: {str(e)}")
    
    # Test coordinates outside the US (non-US)
    print("\nTesting coordinates outside US (should fail with a clear error message)...")
    try:
        # London coordinates
        current_weather = weather_service.get_current_weather(lat=51.5074, lon=-0.1278)
        print("Result (should have failed):", current_weather)
    except Exception as e:
        print(f"Expected error: {str(e)}")

if __name__ == "__main__":
    test_weather_service()