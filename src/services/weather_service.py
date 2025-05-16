import requests
import json
from datetime import datetime, timedelta
import pytz

class WeatherService:
    """Service to interact with the National Weather Service API."""
    
    def __init__(self):
        self.base_url = "https://api.weather.gov"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Semantic Kernel Multi Agent App)",
            "Accept": "application/geo+json"
        }
        self.geocoding_url = "https://nominatim.openstreetmap.org/search"
    
    def _get_coordinates(self, city):
        """
        Convert city name to coordinates using OpenStreetMap Nominatim API.
        
        Args:
            city (str): City name with optional state like "Seattle, WA"
            
        Returns:
            tuple: (latitude, longitude)
        """
        # Append ", USA" to ensure we get US locations
        if not city.lower().endswith(", usa") and not "usa" in city.lower():
            search_city = f"{city}, USA"
        else:
            search_city = city
            
        params = {
            "q": search_city,
            "format": "json",
            "limit": 1
        }
        
        response = requests.get(self.geocoding_url, params=params)
        response.raise_for_status()
        
        results = response.json()
        if not results:
            raise ValueError(f"Could not find coordinates for city: {city}. Note: NWS API only works for US locations.")
        
        return float(results[0]["lat"]), float(results[0]["lon"])
    
    def _get_forecast_url(self, lat, lon):
        """
        Get the specific forecast URL for the given coordinates.
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            
        Returns:
            str: URL for the forecast
        """
        points_url = f"{self.base_url}/points/{lat},{lon}"
        
        try:
            response = requests.get(points_url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            return data["properties"]["forecast"]
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error getting forecast URL: {str(e)}. Note: NWS API only works for US locations.")
    
    def _process_current_weather(self, forecast_data):
        """Process NWS forecast data to extract current weather."""
        current_period = forecast_data["properties"]["periods"][0]
        
        # Parse the NWS data into a similar format as the original service
        result = {
            "location": forecast_data.get("properties", {}).get("relativeLocation", {}).get("properties", {}).get("city", "Unknown"),
            "country": "USA",
            "temperature": current_period.get("temperature"),
            "feels_like": current_period.get("temperature"),  # NWS doesn't provide feels_like
            "humidity": None,  # NWS doesn't provide humidity in the basic forecast
            "wind_speed": current_period.get("windSpeed", "").split()[0] if isinstance(current_period.get("windSpeed"), str) else current_period.get("windSpeed"),  # Extract numeric part
            "description": current_period.get("shortForecast"),
            "condition": current_period.get("shortForecast"),
            "forecast_time": current_period.get("startTime"),
            "wind_direction": current_period.get("windDirection")
        }
        
        return result
    
    def get_current_weather(self, city=None, lat=None, lon=None):
        """
        Get current weather for a location by city name or coordinates.
        
        Args:
            city (str, optional): City name. Defaults to None.
            lat (float, optional): Latitude. Defaults to None.
            lon (float, optional): Longitude. Defaults to None.
            
        Returns:
            dict: Weather data
        """
        # Get coordinates if city is provided
        if city and not (lat and lon):
            lat, lon = self._get_coordinates(city)
        
        if not (lat and lon):
            raise ValueError("Either city or lat/lon coordinates are required")
        
        # Get forecast URL for the coordinates
        forecast_url = self._get_forecast_url(lat, lon)
        
        # Get forecast data
        response = requests.get(forecast_url, headers=self.headers)
        response.raise_for_status()
        forecast_data = response.json()
        
        # Process the data
        return self._process_current_weather(forecast_data)
    
    def get_forecast(self, city=None, lat=None, lon=None, days=5):
        """
        Get weather forecast for a location.
        
        Args:
            city (str, optional): City name. Defaults to None.
            lat (float, optional): Latitude. Defaults to None.
            lon (float, optional): Longitude. Defaults to None.
            days (int, optional): Number of days. Defaults to 5.
            
        Returns:
            dict: Forecast data
        """
        # Get coordinates if city is provided
        if city and not (lat and lon):
            lat, lon = self._get_coordinates(city)
        
        if not (lat and lon):
            raise ValueError("Either city or lat/lon coordinates are required")
        
        # Get forecast URL for the coordinates
        forecast_url = self._get_forecast_url(lat, lon)
        
        # Get forecast data
        response = requests.get(forecast_url, headers=self.headers)
        response.raise_for_status()
        forecast_data = response.json()
        
        # Process the forecast data
        periods = forecast_data["properties"]["periods"]
        location = forecast_data.get("properties", {}).get("relativeLocation", {}).get("properties", {})
        
        processed_forecast = {
            "location": location.get("city", "Unknown"),
            "country": "USA",
            "forecast": []
        }
        
        # NWS normally provides about 14 periods (7 days, day and night)
        # Limit to the requested number of days (2 periods per day)
        max_periods = min(len(periods), days * 2)
        
        for i in range(max_periods):
            period = periods[i]
            processed_forecast["forecast"].append({
                "time": period.get("startTime"),
                "temperature": period.get("temperature"),
                "feels_like": period.get("temperature"),  # NWS doesn't provide feels_like
                "humidity": None,  # NWS doesn't provide humidity in the basic forecast
                "wind_speed": period.get("windSpeed", "").split()[0] if isinstance(period.get("windSpeed"), str) else period.get("windSpeed"),  # Extract numeric part
                "description": period.get("shortForecast"),
                "condition": period.get("shortForecast"),
                "name": period.get("name"),  # This will be "Monday", "Monday Night", etc.
                "wind_direction": period.get("windDirection"),
                "detailed_forecast": period.get("detailedForecast")
            })
        
        return processed_forecast