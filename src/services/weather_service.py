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
        Convert city name to coordinates using a combination of hardcoded data and API.
        
        Args:
            city (str): City name with optional state like "Seattle, WA"
            
        Returns:
            tuple: (latitude, longitude)
        """
        # Common US cities with hardcoded coordinates to avoid API calls
        common_cities = {
            "seattle": (47.6062, -122.3321),
            "seattle, wa": (47.6062, -122.3321),
            "new york": (40.7128, -74.0060),
            "new york, ny": (40.7128, -74.0060),
            "chicago": (41.8781, -87.6298),
            "chicago, il": (41.8781, -87.6298),
            "los angeles": (34.0522, -118.2437),
            "los angeles, ca": (34.0522, -118.2437),
            "san francisco": (37.7749, -122.4194),
            "san francisco, ca": (37.7749, -122.4194),
            "miami": (25.7617, -80.1918),
            "miami, fl": (25.7617, -80.1918),
            "dallas": (32.7767, -96.7970),
            "dallas, tx": (32.7767, -96.7970),
            "denver": (39.7392, -104.9903),
            "denver, co": (39.7392, -104.9903),
            "boston": (42.3601, -71.0589),
            "boston, ma": (42.3601, -71.0589),
            "austin": (30.2672, -97.7431),
            "austin, tx": (30.2672, -97.7431),
            "washington": (38.9072, -77.0369),
            "washington, dc": (38.9072, -77.0369),
            "houston": (29.7604, -95.3698),
            "houston, tx": (29.7604, -95.3698),
            "philadelphia": (39.9526, -75.1652),
            "philadelphia, pa": (39.9526, -75.1652),
            "phoenix": (33.4484, -112.0740),
            "phoenix, az": (33.4484, -112.0740),
            "atlanta": (33.7490, -84.3880),
            "atlanta, ga": (33.7490, -84.3880),
            "portland": (45.5051, -122.6750),
            "portland, or": (45.5051, -122.6750),
            "las vegas": (36.1699, -115.1398),
            "las vegas, nv": (36.1699, -115.1398),
            "san diego": (32.7157, -117.1611),
            "san diego, ca": (32.7157, -117.1611),
            "minneapolis": (44.9778, -93.2650),
            "minneapolis, mn": (44.9778, -93.2650),
            "detroit": (42.3314, -83.0458),
            "detroit, mi": (42.3314, -83.0458),
            "nashville": (36.1627, -86.7816),
            "nashville, tn": (36.1627, -86.7816),
            "baltimore": (39.2904, -76.6122),
            "baltimore, md": (39.2904, -76.6122),
            "charlotte": (35.2271, -80.8431),
            "charlotte, nc": (35.2271, -80.8431),
            "raleigh": (35.7796, -78.6382),
            "raleigh, nc": (35.7796, -78.6382),
            "cleveland": (41.4993, -81.6944),
            "cleveland, oh": (41.4993, -81.6944),
            "pittsburgh": (40.4406, -79.9959),
            "pittsburgh, pa": (40.4406, -79.9959)
        }
        
        # Check if the city is in our hardcoded list (case insensitive)
        city_key = city.lower()
        if city_key in common_cities:
            print(f"Using hardcoded coordinates for {city}")
            return common_cities[city_key]
        
        # For less common cities, try the OpenStreetMap API with rate limiting safeguards
        try:
            print(f"City not found in hardcoded list, trying API for {city}")
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
            
            # Add a User-Agent header to be more polite to the API
            headers = {
                "User-Agent": "Semantic Kernel Weather Service/1.0 (eugene.goldberg117@gmail.com)"
            }
            
            response = requests.get(self.geocoding_url, params=params, headers=headers)
            response.raise_for_status()
            
            results = response.json()
            if not results:
                raise ValueError(f"Could not find coordinates for city: {city}. Note: NWS API only works for US locations.")
            
            return float(results[0]["lat"]), float(results[0]["lon"])
        except requests.exceptions.RequestException as e:
            # If API fails, try to approximate based on known cities
            print(f"API request failed, trying approximate match: {str(e)}")
            
            # Remove state code if present to try a more general match
            if "," in city_key:
                base_city = city_key.split(",")[0].strip()
                if base_city in common_cities:
                    print(f"Found approximate match: {base_city}")
                    return common_cities[base_city]
            
            # If we truly can't find it, raise error
            raise ValueError(f"Could not find coordinates for city: {city}. Note: NWS API only works for US locations.")
    
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