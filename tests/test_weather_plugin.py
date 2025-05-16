import unittest
from unittest.mock import patch, MagicMock
import json

from src.agents.plugins.weather_plugin import WeatherPlugin

class WeatherPluginTest(unittest.TestCase):
    """Test cases for the WeatherPlugin"""
    
    def setUp(self):
        """Set up test environment"""
        self.plugin = WeatherPlugin()
    
    @patch('src.services.weather_service.WeatherService.get_current_weather')
    def test_get_current_weather(self, mock_get_current_weather):
        """Test the get_current_weather function"""
        # Mock weather service response
        mock_weather_data = {
            "name": "Seattle",
            "sys": {"country": "US"},
            "main": {"temp": 15.5, "feels_like": 14.8, "humidity": 75},
            "wind": {"speed": 3.5},
            "weather": [{"description": "light rain", "main": "Rain"}]
        }
        
        mock_get_current_weather.return_value = mock_weather_data
        
        # Call the function
        result = self.plugin.get_current_weather("Seattle")
        
        # Verify the function was called with the correct city
        mock_get_current_weather.assert_called_once_with(city="Seattle")
        
        # Parse the JSON result
        parsed_result = json.loads(result)
        
        # Verify the result contains the expected data
        self.assertEqual(parsed_result["location"], "Seattle")
        self.assertEqual(parsed_result["country"], "US")
        self.assertEqual(parsed_result["temperature"], 15.5)
        self.assertEqual(parsed_result["feels_like"], 14.8)
        self.assertEqual(parsed_result["humidity"], 75)
        self.assertEqual(parsed_result["wind_speed"], 3.5)
        self.assertEqual(parsed_result["description"], "light rain")
        self.assertEqual(parsed_result["condition"], "Rain")
    
    @patch('src.services.weather_service.WeatherService.get_current_weather')
    def test_get_current_weather_error(self, mock_get_current_weather):
        """Test error handling in get_current_weather"""
        # Mock an exception from the weather service
        mock_get_current_weather.side_effect = Exception("API error")
        
        # Call the function
        result = self.plugin.get_current_weather("Seattle")
        
        # Verify the result contains an error message
        self.assertTrue(result.startswith("Error retrieving weather information"))
    
    @patch('src.services.weather_service.WeatherService.get_forecast')
    def test_get_weather_forecast(self, mock_get_forecast):
        """Test the get_weather_forecast function"""
        # Mock forecast service response
        mock_forecast_data = {
            "city": {"name": "Seattle", "country": "US"},
            "list": [
                {
                    "dt_txt": "2023-01-01 12:00:00",
                    "main": {"temp": 15.5, "feels_like": 14.8, "humidity": 75},
                    "wind": {"speed": 3.5},
                    "weather": [{"description": "light rain", "main": "Rain"}]
                },
                {
                    "dt_txt": "2023-01-01 15:00:00",
                    "main": {"temp": 16.2, "feels_like": 15.5, "humidity": 70},
                    "wind": {"speed": 3.0},
                    "weather": [{"description": "overcast clouds", "main": "Clouds"}]
                }
            ]
        }
        
        mock_get_forecast.return_value = mock_forecast_data
        
        # Call the function
        result = self.plugin.get_weather_forecast("Seattle", 1)
        
        # Verify the function was called with the correct parameters
        mock_get_forecast.assert_called_once_with(city="Seattle", days=1)
        
        # Parse the JSON result
        parsed_result = json.loads(result)
        
        # Verify the result contains the expected data
        self.assertEqual(parsed_result["location"], "Seattle")
        self.assertEqual(parsed_result["country"], "US")
        self.assertEqual(len(parsed_result["forecast"]), 2)
        self.assertEqual(parsed_result["forecast"][0]["time"], "2023-01-01 12:00:00")
        self.assertEqual(parsed_result["forecast"][0]["temperature"], 15.5)
        self.assertEqual(parsed_result["forecast"][1]["description"], "overcast clouds")

if __name__ == '__main__':
    unittest.main()