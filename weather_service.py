import os
import requests
import logging

def get_weather_condition():
    """
    Get current weather condition using OpenWeatherMap API
    Returns: 'clear', 'partly_cloudy', 'cloudy', 'rain', 'snow', or 'unknown'
    """
    try:
        api_key = os.getenv("OPENWEATHER_API_KEY", "demo_key")
        city = "Union City,PA"  # Tyler's location in Pennsylvania
        
        if api_key == "demo_key":
            logging.warning("Using demo weather data - no API key provided")
            # Return a default condition for demo purposes
            return "clear"
        
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        weather_main = data['weather'][0]['main'].lower()
        
        # Map OpenWeather conditions to our simplified conditions
        condition_map = {
            'clear': 'clear',
            'clouds': 'partly_cloudy',
            'rain': 'rain',
            'drizzle': 'rain',
            'thunderstorm': 'rain',
            'snow': 'snow',
            'mist': 'cloudy',
            'fog': 'cloudy',
            'haze': 'cloudy'
        }
        
        return condition_map.get(weather_main, 'cloudy')
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Weather API request failed: {e}")
        return "unknown"
    except KeyError as e:
        logging.error(f"Weather API response parsing failed: {e}")
        return "unknown"
    except Exception as e:
        logging.error(f"Unexpected error in weather service: {e}")
        return "unknown"
