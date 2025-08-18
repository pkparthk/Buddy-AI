"""
External API Integration Module for Buddy AI
Handles weather, news, and other external service integrations
"""

import requests
import os
from typing import Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ExternalAPIManager:
    def __init__(self):
        self.weather_api_key = os.getenv('OPENWEATHER_API_KEY')
        self.news_api_key = os.getenv('NEWS_API_KEY')
        
    def get_weather(self, location: str = "auto") -> Dict:
        """
        Get weather information for a location
        """
        if not self.weather_api_key:
            return {
                'success': False,
                'message': "Weather API key not configured. Please set OPENWEATHER_API_KEY environment variable.",
                'data': None
            }
        
        try:
            # If location is auto, try to get user's location (simplified)
            if location.lower() in ['auto', 'current location', 'here']:
                location = "London"  # Default fallback
            
            # Handle common city name variations
            city_mapping = {
                'bangalore': 'Bengaluru,IN',
                'bengaluru': 'Bengaluru,IN',
                'mumbai': 'Mumbai,IN',
                'bombay': 'Mumbai,IN',
                'delhi': 'New Delhi,IN',
                'new delhi': 'New Delhi,IN',
                'calcutta': 'Kolkata,IN',
                'kolkata': 'Kolkata,IN',
                'chennai': 'Chennai,IN',
                'madras': 'Chennai,IN',
                'hyderabad': 'Hyderabad,IN',
                'pune': 'Pune,IN',
                'ahmedabad': 'Ahmedabad,IN'
            }
            
            # Check if we have a mapping for this city
            location_query = city_mapping.get(location.lower(), location)
            
            # OpenWeatherMap API call
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': location_query,
                'appid': self.weather_api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                weather_info = {
                    'location': data['name'],
                    'temperature': data['main']['temp'],
                    'description': data['weather'][0]['description'],
                    'humidity': data['main']['humidity'],
                    'wind_speed': data['wind']['speed']
                }
                
                message = f"The temperature in {weather_info['location']} is {weather_info['temperature']}°C with {weather_info['description']}. Humidity is at {weather_info['humidity']}% and wind speed is {weather_info['wind_speed']} m/s."
                
                return {
                    'success': True,
                    'message': message,
                    'data': weather_info
                }
            elif response.status_code == 401:
                return {
                    'success': False,
                    'message': "Weather API key is invalid or not activated yet. Please check your OpenWeatherMap API key or wait for activation (can take up to 2 hours).",
                    'data': None
                }
            elif response.status_code == 404:
                return {
                    'success': False,
                    'message': f"Location '{location}' not found. Please try a different city name or include country code (e.g., 'London,UK').",
                    'data': None
                }
            else:
                return {
                    'success': False,
                    'message': f"Could not get weather for {location}. API returned status {response.status_code}.",
                    'data': None
                }
                
        except requests.RequestException as e:
            return {
                'success': False,
                'message': f"Network error getting weather: {str(e)}",
                'data': None
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Error getting weather: {str(e)}",
                'data': None
            }
    
    def get_news(self, topic: str = "general", count: int = 5) -> Dict:
        """
        Get news articles about a specific topic
        """
        if not self.news_api_key:
            return {
                'success': False,
                'message': "News API key not configured. Please set NEWS_API_KEY environment variable.",
                'data': None
            }
        
        try:
            # NewsAPI call
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': topic,
                'apiKey': self.news_api_key,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': count
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                if articles:
                    news_summary = f"Here are the latest {len(articles)} news articles about {topic}:\n\n"
                    for i, article in enumerate(articles[:count], 1):
                        title = article.get('title', 'No title')
                        source = article.get('source', {}).get('name', 'Unknown source')
                        news_summary += f"{i}. {title} - {source}\n"
                    
                    return {
                        'success': True,
                        'message': news_summary.strip(),
                        'data': articles
                    }
                else:
                    return {
                        'success': False,
                        'message': f"No news articles found for {topic}",
                        'data': None
                    }
            else:
                return {
                    'success': False,
                    'message': f"Could not get news for {topic}",
                    'data': None
                }
                
        except requests.RequestException as e:
            return {
                'success': False,
                'message': f"Network error getting news: {str(e)}",
                'data': None
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Error getting news: {str(e)}",
                'data': None
            }
    
    def get_ip_location(self) -> Dict:
        """
        Get user's approximate location based on IP
        """
        try:
            response = requests.get('http://ipapi.co/json/', timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'city': data.get('city', 'Unknown'),
                    'country': data.get('country_name', 'Unknown'),
                    'timezone': data.get('timezone', 'Unknown')
                }
        except:
            pass
        
        return {
            'success': False,
            'city': 'Unknown',
            'country': 'Unknown',
            'timezone': 'Unknown'
        }

# Global instance
api_manager = ExternalAPIManager()

# Convenience functions
def get_weather_info(location: str = "auto") -> Dict:
    """Convenience function to get weather"""
    return api_manager.get_weather(location)

def get_news_info(topic: str = "general") -> Dict:
    """Convenience function to get news"""
    return api_manager.get_news(topic)

def get_location_info() -> Dict:
    """Convenience function to get location"""
    return api_manager.get_ip_location()
