import os
import unittest
from unittest.mock import patch, MagicMock
import json

from src.services.weather_service import WeatherService

class WeatherServiceTest(unittest.TestCase):
    """Test cases for the WeatherService"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock API key
        self.api_key = "test_api_key"
        self.service = WeatherService(api_key=self.api_key)
    
    @patch('src.services.weather_service.requests.get')
    def test_get_current_weather_by_city(self, mock_get):
        """Test getting current weather by city"""
        # Mock response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        
        # Sample weather data
        weather_data = {
            "name": "Seattle",
            "sys": {"country": "US"},
            "main": {"temp": 15.5, "feels_like": 14.8, "humidity": 75},
            "wind": {"speed": 3.5},
            "weather": [{"description": "light rain", "main": "Rain"}]
        }
        
        mock_response.json.return_value = weather_data
        mock_get.return_value = mock_response
        
        # Call the method
        result = self.service.get_current_weather(city="Seattle")
        
        # Verify the correct URL and parameters
        mock_get.assert_called_once_with(
            f"{self.service.base_url}/weather",
            params={"q": "Seattle", "appid": self.api_key, "units": "metric"}
        )
        
        # Verify the result
        self.assertEqual(result, weather_data)
    
    @patch('src.services.weather_service.requests.get')
    def test_get_current_weather_by_coordinates(self, mock_get):
        """Test getting current weather by coordinates"""
        # Mock response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        
        # Sample weather data
        weather_data = {
            "name": "Seattle",
            "sys": {"country": "US"},
            "main": {"temp": 15.5, "feels_like": 14.8, "humidity": 75},
            "wind": {"speed": 3.5},
            "weather": [{"description": "light rain", "main": "Rain"}]
        }
        
        mock_response.json.return_value = weather_data
        mock_get.return_value = mock_response
        
        # Call the method
        result = self.service.get_current_weather(lat=47.6062, lon=-122.3321)
        
        # Verify the correct URL and parameters
        mock_get.assert_called_once_with(
            f"{self.service.base_url}/weather",
            params={"lat": 47.6062, "lon": -122.3321, "appid": self.api_key, "units": "metric"}
        )
        
        # Verify the result
        self.assertEqual(result, weather_data)
    
    def test_missing_location(self):
        """Test error case when location is missing"""
        with self.assertRaises(ValueError):
            self.service.get_current_weather()
    
    def test_missing_api_key(self):
        """Test error case when API key is missing"""
        with self.assertRaises(ValueError):
            WeatherService(api_key=None)

if __name__ == '__main__':
    unittest.main()