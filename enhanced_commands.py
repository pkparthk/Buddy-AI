"""
Enhanced Command Processing Module for Buddy AI
This module provides intelligent command processing capabilities for Buddy AI
"""

import re
import webbrowser
import requests
import json
import os
import subprocess
import platform
from datetime import datetime, timedelta
from urllib.parse import quote_plus
from typing import Dict, List, Tuple, Optional
import psutil
from model import call_gemini_ai
from external_apis import get_weather_info, get_news_info, get_location_info

class BuddyCommandProcessor:
    def __init__(self):
        self.system_os = platform.system()
        self.command_patterns = self._initialize_patterns()
        self.web_services = self._initialize_web_services()
        
    def _initialize_patterns(self) -> Dict:
        """Initialize command patterns for various actions"""
        return {
            'greeting': [
                r'^(?:hi|hello|hey|good morning|good afternoon|good evening)(?:\s+there)?(?:\s+buddy)?$',
                r'^how are you(?:\s+doing)?(?:\s+today)?$',
                r'^how(?:\'s| is) (?:your day|it going)',
                r'^(?:what\'s up|sup)$'
            ],
            'identity': [
                r'who are you',
                r'what(?:\'s| is) your name',
                r'what are you called',
                r'tell me about yourself',
                r'what(?:\'s| is) your identity',
                r'introduce yourself',
                r'who am i (?:talking|speaking) (?:to|with)',
                r'what kind of (?:ai|assistant) are you'
            ],
            'direct_open': [
                r'open (?:the )?(?:website )?(?:called )?(.+?)(?:\s+website|\s+site|\s+app|\s+application)?$',
                r'go to (?:the )?(?:website )?(?:called )?(.+?)(?:\s+website|\s+site)?$',
                r'visit (?:the )?(?:website )?(?:called )?(.+?)(?:\s+website|\s+site)?$',
                r'navigate to (?:the )?(?:website )?(?:called )?(.+?)(?:\s+website|\s+site)?$',
                r'launch (?:the )?(?:website )?(?:called )?(.+?)(?:\s+website|\s+site|\s+app|\s+application)?$'
            ],
            'weather': [
                r'weather (?:in |for |of )?(.+)',
                r'temperature (?:in |for |of )?(.+)',
                r'(.+) (?:weather|temperature)',
                r'what(?:\'s| is) the (?:weather|temperature) (?:in |of |for )?(.+)',
                r'how(?:\'s| is) the weather (?:in |of |for )?(.+)'
            ],
            'ai_conversation': [
                # General knowledge that should be answered by AI, not web search
                r'what is (?:artificial intelligence|ai|machine learning|quantum computing|blockchain|programming)',
                r'explain (?:artificial intelligence|ai|machine learning|quantum computing|blockchain|programming)',
                r'tell me about (?:artificial intelligence|ai|machine learning|quantum computing|blockchain|programming)',
                r'how does (?:artificial intelligence|ai|machine learning|quantum computing|the internet|programming) work',
                # Creative requests
                r'write (?:a|an) (.+)',
                r'create (?:a|an) (.+)',
                r'tell me a (?:joke|story)',
                r'make (?:a|an) (.+)',
                # Advice and help
                r'how (?:do i|can i|should i) (.+)',
                r'what should i do (?:if|when|about) (.+)',
                r'help me (?:with|understand) (.+)',
                r'can you help (?:me )?(.+)',
                # Conversational
                r'what do you think about (.+)',
                r'do you (?:like|enjoy|prefer) (.+)',
                r'are you (.+)',
                # Educational
                r'explain (.+) in simple terms',
                r'what are the (?:benefits|advantages|disadvantages) of (.+)',
                r'why (?:is|are|do|does) (.+)',
                r'how to (.+) better',
                r'what\'s the difference between (.+) and (.+)'
            ],
            'calculations': [
                r'calculate (.+)',
                r'what(?:\'s| is) (.+?) (?:\+|\-|\*|\/|\^|plus|minus|times|divided by) (.+)',
                r'convert (.+?) to (.+)',
                r'how many (.+?) in (.+)',
                r'what(?:\'s| is) (\d+)% of (\d+)',
                r'(\d+) percent of (\d+)',
                r'solve:? (.+)',
                r'(\d+) (?:\+|\-|\*|\/|\^|plus|minus|times|divided by) (\d+)',
                # Add more flexible percentage patterns
                r'(\d+)%?\s*(?:of|from)\s*(\d+)',
                # Add simple arithmetic patterns
                r'(\d+(?:\.\d+)?)\s*[\+\-\*\/]\s*(\d+(?:\.\d+)?)',
                r'(\d+(?:\.\d+)?)\s+(?:plus|minus|times|divided by)\s+(\d+(?:\.\d+)?)'
            ],
            'web_search': [
                r'search (?:for |about )?(.+)',
                r'look up (.+)',
                r'google (.+)',
                r'search (.+) on (.+)',
                r'find (.+) videos?',
                r'show me (.+) tutorials?',
                # More specific patterns that should go to web search
                r'find (?:information about |me )?(.+) (?:website|site|online)',
                r'who is (.+) (?:person|celebrity|actor|musician)',
                r'what is (.+) (?:website|company|organization|movie|book)',
                r'tell me about (.+) (?:news|recent|latest)'
            ],
            'system_control': [
                r'start (?:the )?(?:application )?(.+)',
                r'run (?:the )?(?:application )?(.+)',
                r'execute (?:the )?(?:application )?(.+)'
            ],
            'media_control': [
                r'play (.+)',
                r'pause (.+)',
                r'stop (.+)',
                r'skip (.+)',
                r'next (.+)',
                r'previous (.+)'
            ],
            'information': [
                r'what(?:\'s| is) the time',
                r'current time',
                r'what(?:\'s| is) the date',
                r'today(?:\'s| is) date',
                r'news (?:about |on )?(.+)?'
            ],
            'system_info': [
                r'battery (?:level|status)',
                r'memory usage',
                r'cpu usage',
                r'disk space',
                r'system (?:info|information)'
            ],
            'calculations': [
                r'calculate (.+)',
                r'what(?:\'s| is) (.+?) (?:\+|\-|\*|\/|\^) (.+)',
                r'convert (.+?) to (.+)',
                r'how many (.+?) in (.+)'
            ]
        }
    
    def _initialize_web_services(self) -> Dict:
        """Initialize web service URLs and patterns"""
        return {
            'youtube': 'https://www.youtube.com/results?search_query={}',
            'google': 'https://www.google.com/search?q={}',
            'wikipedia': 'https://en.wikipedia.org/wiki/{}',
            'github': 'https://github.com/search?q={}',
            'stackoverflow': 'https://stackoverflow.com/search?q={}',
            'reddit': 'https://www.reddit.com/search/?q={}',
            'amazon': 'https://www.amazon.com/s?k={}',
            'netflix': 'https://www.netflix.com/search?q={}',
            'spotify': 'https://open.spotify.com/search/{}',
            'twitter': 'https://twitter.com/search?q={}',
            'instagram': 'https://www.instagram.com/explore/tags/{}/',
            'linkedin': 'https://www.linkedin.com/search/results/all/?keywords={}',
            'maps': 'https://www.google.com/maps/search/{}',
            'gmail': 'https://mail.google.com',
            'facebook': 'https://www.facebook.com/search/top?q={}'
        }
    
    def process_command(self, query: str) -> Dict:
        """
        Main command processing function
        Returns a dictionary with action type and response
        """
        query = query.lower().strip()
        
        # Handle incomplete queries
        if not query or len(query) < 3:
            return {
                'success': True,
                'message': "I'm here to help! What would you like to know?",
                'action': 'incomplete_query'
            }
        
        # Handle incomplete weather queries specifically
        if query.startswith('what is temperature of') and len(query.split()) <= 4:
            return {
                'success': True,
                'message': "I'd be happy to help you get the temperature! Please specify a city. For example: 'What is the temperature of Mumbai?' or 'Temperature in Delhi'",
                'action': 'incomplete_weather_query'
            }
        
        # Try to match against known patterns
        for category, patterns in self.command_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, query, re.IGNORECASE)
                if match:
                    return self._execute_command(category, match, query)
        
        # If no specific pattern matches, use AI for intelligent interpretation
        return self._ai_interpretation(query)
    
    def _execute_command(self, category: str, match: re.Match, original_query: str) -> Dict:
        """Execute commands based on category"""
        try:
            if category == 'greeting':
                return self._handle_greeting(original_query)
            elif category == 'identity':
                return self._handle_identity_question(original_query)
            elif category == 'direct_open':
                return self._handle_direct_open(match.group(1), original_query)
            elif category == 'weather':
                location = match.group(1) if match.lastindex and match.group(1) else self._extract_location(original_query)
                return self._get_weather_info(location)
            elif category == 'ai_conversation':
                return self._handle_ai_conversation(original_query)
            elif category == 'calculations':
                return self._handle_calculations(match.group(0) if match.lastindex is None else match.group(1))
            elif category == 'web_search':
                return self._handle_web_search(match.group(1))
            elif category == 'system_control':
                return self._handle_system_control(match.group(1))
            elif category == 'media_control':
                return self._handle_media_control(match.group(0))
            elif category == 'information':
                return self._handle_information_request(original_query, match)
            elif category == 'system_info':
                return self._handle_system_info(original_query)
            elif category == 'calculations':
                return self._handle_calculations(match.group(1))
            else:
                return self._ai_interpretation(original_query)
        except Exception as e:
            return {
                'success': False,
                'message': f"Error executing command: {str(e)}",
                'action': 'error'
            }
    
    def _handle_direct_open(self, target: str, original_query: str) -> Dict:
        """Handle direct website/app opening with intelligent decision making"""
        target = target.strip().lower()
        
        # Define direct website mappings for immediate opening
        direct_websites = {
            'youtube': 'https://www.youtube.com',
            'google': 'https://www.google.com',
            'gmail': 'https://mail.google.com',
            'facebook': 'https://www.facebook.com',
            'twitter': 'https://www.twitter.com',
            'instagram': 'https://www.instagram.com',
            'linkedin': 'https://www.linkedin.com',
            'github': 'https://www.github.com',
            'stackoverflow': 'https://stackoverflow.com',
            'reddit': 'https://www.reddit.com',
            'amazon': 'https://www.amazon.com',
            'netflix': 'https://www.netflix.com',
            'spotify': 'https://open.spotify.com',
            'whatsapp': 'https://web.whatsapp.com',
            'discord': 'https://discord.com',
            'slack': 'https://slack.com',
            'zoom': 'https://zoom.us',
            'teams': 'https://teams.microsoft.com',
            'microsoft teams': 'https://teams.microsoft.com',
            'google drive': 'https://drive.google.com',
            'google docs': 'https://docs.google.com',
            'google sheets': 'https://sheets.google.com',
            'dropbox': 'https://www.dropbox.com',
            'onedrive': 'https://onedrive.live.com',
            'wikipedia': 'https://www.wikipedia.org',
            'twitch': 'https://www.twitch.tv',
            'pinterest': 'https://www.pinterest.com',
            'tiktok': 'https://www.tiktok.com',
            'snapchat': 'https://web.snapchat.com'
        }
        
        # Check for exact matches first
        if target in direct_websites:
            url = direct_websites[target]
            webbrowser.open(url)
            return {
                'success': True,
                'message': f"Opening {target.title()}",
                'action': 'direct_open',
                'url': url
            }
        
        # Check for partial matches (e.g., "yt" for "youtube")
        abbreviations = {
            'yt': 'youtube',
            'fb': 'facebook',
            'ig': 'instagram',
            'gh': 'github',
            'so': 'stackoverflow',
            'aws': 'amazon',
            'ms teams': 'microsoft teams',
            'drive': 'google drive',
            'docs': 'google docs',
            'sheets': 'google sheets'
        }
        
        if target in abbreviations:
            full_name = abbreviations[target]
            url = direct_websites[full_name]
            webbrowser.open(url)
            return {
                'success': True,
                'message': f"Opening {full_name.title()}",
                'action': 'direct_open',
                'url': url
            }
        
        # Check if it's a system application
        system_apps = {
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'calc': 'calc.exe',
            'paint': 'mspaint.exe',
            'cmd': 'cmd.exe',
            'command prompt': 'cmd.exe',
            'powershell': 'powershell.exe',
            'task manager': 'taskmgr.exe',
            'file explorer': 'explorer.exe',
            'explorer': 'explorer.exe',
            'control panel': 'control.exe',
            'settings': 'ms-settings:',
            'chrome': 'chrome.exe',
            'firefox': 'firefox.exe',
            'edge': 'msedge.exe',
            'word': 'winword.exe',
            'excel': 'excel.exe',
            'powerpoint': 'powerpnt.exe',
            'outlook': 'outlook.exe',
            'vs code': 'code.exe',
            'visual studio code': 'code.exe',
            'code': 'code.exe',
            'spotify': 'spotify.exe',
            'discord': 'discord.exe',
            'steam': 'steam.exe'
        }
        
        if target in system_apps:
            return self._handle_system_control(target)
        
        # If it looks like a URL or domain
        if '.' in target or target.endswith('.com') or target.endswith('.org'):
            url = target if target.startswith('http') else f"https://{target}"
            webbrowser.open(url)
            return {
                'success': True,
                'message': f"Opening {target}",
                'action': 'direct_open',
                'url': url
            }
        
        # Use AI to make intelligent decision
        return self._ai_website_decision(target, original_query)
    
    def _ai_website_decision(self, target: str, original_query: str) -> Dict:
        """Use AI to make intelligent decisions about what to open"""
        prompt = f"""
        The user said: "{original_query}"
        They want to open: "{target}"
        
        Based on this request, determine the most likely action:
        1. If it's clearly a website name (even if misspelled), provide the correct URL
        2. If it's an application name, suggest opening the application
        3. If it's ambiguous, make the best guess
        
        Respond with just the action in this format:
        ACTION: [website|application|search]
        URL/APP: [the URL to open or application name]
        MESSAGE: [what to tell the user]
        
        Example responses:
        ACTION: website
        URL: https://www.youtube.com
        MESSAGE: Opening YouTube
        
        ACTION: application
        URL: notepad.exe
        MESSAGE: Opening Notepad
        """
        
        try:
            response = call_gemini_ai(prompt)
            lines = response.strip().split('\n')
            
            action_line = next((line for line in lines if line.startswith('ACTION:')), '')
            url_line = next((line for line in lines if line.startswith('URL:')), '')
            message_line = next((line for line in lines if line.startswith('MESSAGE:')), '')
            
            if action_line and url_line and message_line:
                action = action_line.split(':', 1)[1].strip()
                url_or_app = url_line.split(':', 1)[1].strip()
                message = message_line.split(':', 1)[1].strip()
                
                if action == 'website':
                    webbrowser.open(url_or_app)
                    return {
                        'success': True,
                        'message': message,
                        'action': 'ai_direct_open',
                        'url': url_or_app
                    }
                elif action == 'application':
                    return self._handle_system_control(url_or_app.replace('.exe', ''))
                else:
                    return self._handle_web_search(target)
            
        except Exception as e:
            print(f"AI decision error: {e}")
        
        # Fallback: treat as web search
        return self._handle_web_search(target)
    
    def _handle_identity_question(self, query: str) -> Dict:
        """Handle identity questions about the AI"""
        identity_responses = {
            'who are you': "I am Buddy, your personal intelligent assistant. I can help you with a variety of tasks, including web searches, opening applications, providing information, and general assistance.",
            'what is your name': "My name is Buddy. I'm your personal AI assistant.",
            'what are you called': "I am called Buddy.",
            'tell me about yourself': "I am Buddy, an advanced personal assistant designed to help you with various tasks. I can open websites, search for information, control applications, answer questions, and much more. Think of me as your digital companion ready to assist with whatever you need.",
            'what is your identity': "I am Buddy, your personal AI assistant.",
            'introduce yourself': "Hello! I'm Buddy, your personal intelligent assistant. I'm here to help you navigate the web, find information, control your system, and assist with various tasks. Just tell me what you need, and I'll do my best to help!",
            'who am i talking to': "You're talking to Buddy, your personal assistant.",
            'who am i speaking to': "You're speaking to Buddy, your personal assistant.",
            'who am i speaking with': "You're speaking with Buddy, your personal assistant.",
            'who am i talking with': "You're talking with Buddy, your personal assistant.",
            'what kind of ai are you': "I am Buddy, a personal AI assistant designed to help with web browsing, information retrieval, system control, and general assistance.",
            'what kind of assistant are you': "I am Buddy, a personal AI assistant designed to help with web browsing, information retrieval, system control, and general assistance."
        }
        
        # Find the most appropriate response
        query_lower = query.lower().strip()
        
        # Try exact match first
        if query_lower in identity_responses:
            response = identity_responses[query_lower]
        else:
            # Default response for any identity-related question
            response = "I am Buddy, your personal intelligent assistant. I'm here to help you with various tasks including web searches, opening applications, providing information, and much more."
        
        return {
            'success': True,
            'message': response,
            'action': 'identity_response',
            'original_query': query
        }
    
    def _handle_greeting(self, query: str) -> Dict:
        """Handle greeting messages from the user"""
        query_lower = query.lower().strip()
        
        greeting_responses = {
            'hi': "Hi there! How can I help you today?",
            'hello': "Hello! What can I do for you?",
            'hey': "Hey! How's it going? What do you need help with?",
            'good morning': "Good morning! Hope you're having a great day. How can I assist you?",
            'good afternoon': "Good afternoon! What can I help you with today?",
            'good evening': "Good evening! How can I make your evening better?",
            'how are you': "I'm doing great, thanks for asking! How are you doing today?",
            'how are you doing': "I'm doing wonderful, thanks! How about you?",
            'how are you doing today': "I'm having a fantastic day, thank you! How has your day been?",
            'how is your day': "My day is going great, thanks for asking! How's yours going?",
            "how's your day": "My day is going great, thanks for asking! How's yours going?",
            'how is it going': "Things are going really well, thanks! How are things with you?",
            "how's it going": "Things are going really well, thanks! How are things with you?",
            "what's up": "Not much, just here ready to help! What's up with you?",
            'sup': "Hey! Not much, just ready to assist. What do you need?"
        }
        
        # Find the best response
        response = greeting_responses.get(query_lower, "Hello! How can I help you today?")
        
        return {
            'success': True,
            'message': response,
            'action': 'greeting_response',
            'original_query': query
        }
    
    def _handle_web_search(self, query: str) -> Dict:
        """Handle web search requests intelligently"""
        # Determine the best search platform based on query content
        search_platform = self._determine_search_platform(query)
        search_url = self.web_services[search_platform].format(quote_plus(query))
        
        webbrowser.open(search_url)
        return {
            'success': True,
            'message': f"Searching for '{query}' on {search_platform.title()}",
            'action': 'web_search',
            'url': search_url
        }
    
    def _determine_search_platform(self, query: str) -> str:
        """Intelligently determine the best search platform"""
        query_lower = query.lower()
        
        # Video-related searches
        if any(word in query_lower for word in ['video', 'watch', 'tutorial', 'how to', 'music', 'song']):
            return 'youtube'
        
        # Code-related searches
        elif any(word in query_lower for word in ['code', 'programming', 'python', 'javascript', 'error', 'bug']):
            return 'stackoverflow'
        
        # Shopping-related searches
        elif any(word in query_lower for word in ['buy', 'purchase', 'price', 'product', 'shop']):
            return 'amazon'
        
        # Location-related searches
        elif any(word in query_lower for word in ['location', 'address', 'directions', 'near me', 'restaurant']):
            return 'maps'
        
        # Social media content
        elif any(word in query_lower for word in ['news', 'trending', 'latest']):
            return 'reddit'
        
        # Default to Google for general searches
        else:
            return 'google'
    
    def _handle_system_control(self, application: str) -> Dict:
        """Handle system application control"""
        app_name = application.strip().lower()
        
        # Common application mappings
        app_mappings = {
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'paint': 'mspaint.exe',
            'cmd': 'cmd.exe',
            'command prompt': 'cmd.exe',
            'powershell': 'powershell.exe',
            'task manager': 'taskmgr.exe',
            'file explorer': 'explorer.exe',
            'explorer': 'explorer.exe',
            'control panel': 'control.exe',
            'settings': 'ms-settings:',
            'chrome': 'chrome.exe',
            'firefox': 'firefox.exe',
            'edge': 'msedge.exe',
            'word': 'winword.exe',
            'excel': 'excel.exe',
            'powerpoint': 'powerpnt.exe',
            'outlook': 'outlook.exe',
            'vs code': 'code.exe',
            'visual studio code': 'code.exe',
            'spotify': 'spotify.exe',
            'discord': 'discord.exe',
            'steam': 'steam.exe'
        }
        
        executable = app_mappings.get(app_name, f"{app_name}.exe")
        
        try:
            if self.system_os == "Windows":
                subprocess.Popen(executable, shell=True)
            elif self.system_os == "Darwin":  # macOS
                subprocess.Popen(["open", "-a", application])
            else:  # Linux
                subprocess.Popen([application])
            
            return {
                'success': True,
                'message': f"Opening {application}",
                'action': 'system_control'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Could not open {application}: {str(e)}",
                'action': 'system_control'
            }
    
    def _handle_information_request(self, query: str, match: re.Match = None) -> Dict:
        """Handle information requests like time, date, weather"""
        query_lower = query.lower()
        
        if 'time' in query_lower:
            current_time = datetime.now().strftime("%I:%M %p")
            return {
                'success': True,
                'message': f"The current time is {current_time}",
                'action': 'time_info',
                'data': current_time
            }
        
        elif 'date' in query_lower:
            current_date = datetime.now().strftime("%A, %B %d, %Y")
            return {
                'success': True,
                'message': f"Today is {current_date}",
                'action': 'date_info',
                'data': current_date
            }
        
        elif 'weather' in query_lower or 'temperature' in query_lower:
            # Handle different weather/temperature patterns
            location = None
            
            # Try to extract location from different patterns
            if match and match.groups():
                location = match.group(1).strip()
            
            # If no location found from regex, try to extract from query
            if not location or location == "current location":
                # Look for city names in the query
                import re
                query_clean = query_lower.replace('weather', '').replace('temperature', '').replace('in', '').replace('of', '').replace('for', '').strip()
                if query_clean:
                    location = query_clean
                else:
                    location = "current location"
            
            return self._get_weather_info(location)
        
        elif 'news' in query_lower:
            topic = match.group(1) if match and match.groups() else "general"
            return self._get_news_info(topic)
        
        return {
            'success': False,
            'message': "Could not process information request",
            'action': 'information'
        }
    
    def _handle_system_info(self, query: str) -> Dict:
        """Handle system information requests"""
        query_lower = query.lower()
        
        try:
            if 'battery' in query_lower:
                battery = psutil.sensors_battery()
                if battery:
                    percentage = battery.percent
                    plugged = "plugged in" if battery.power_plugged else "not plugged in"
                    return {
                        'success': True,
                        'message': f"Battery is at {percentage}% and {plugged}",
                        'action': 'battery_info',
                        'data': {'percentage': percentage, 'plugged': battery.power_plugged}
                    }
                else:
                    return {
                        'success': False,
                        'message': "Battery information not available",
                        'action': 'battery_info'
                    }
            
            elif 'memory' in query_lower or 'ram' in query_lower:
                memory = psutil.virtual_memory()
                percentage = memory.percent
                total = memory.total / (1024**3)  # Convert to GB
                used = memory.used / (1024**3)
                return {
                    'success': True,
                    'message': f"Memory usage: {percentage}% ({used:.1f}GB of {total:.1f}GB used)",
                    'action': 'memory_info',
                    'data': {'percentage': percentage, 'used': used, 'total': total}
                }
            
            elif 'cpu' in query_lower:
                cpu_percent = psutil.cpu_percent(interval=1)
                return {
                    'success': True,
                    'message': f"CPU usage: {cpu_percent}%",
                    'action': 'cpu_info',
                    'data': {'percentage': cpu_percent}
                }
            
            elif 'disk' in query_lower:
                disk = psutil.disk_usage('/')
                percentage = (disk.used / disk.total) * 100
                total = disk.total / (1024**3)  # Convert to GB
                used = disk.used / (1024**3)
                free = disk.free / (1024**3)
                return {
                    'success': True,
                    'message': f"Disk usage: {percentage:.1f}% ({used:.1f}GB used, {free:.1f}GB free of {total:.1f}GB total)",
                    'action': 'disk_info',
                    'data': {'percentage': percentage, 'used': used, 'free': free, 'total': total}
                }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Error getting system information: {str(e)}",
                'action': 'system_info'
            }
    
    def _get_weather_info(self, location: str) -> Dict:
        """Get weather information using external API"""
        result = get_weather_info(location)
        return {
            'success': result['success'],
            'message': result['message'],
            'action': 'weather_info',
            'data': result.get('data', {})
        }
    
    def _handle_ai_conversation(self, query: str) -> Dict:
        """Handle general AI conversations like ChatGPT/Gemini"""
        from model import get_intelligent_response, QuotaExceededException
        
        try:
            response = get_intelligent_response(query)
            return {
                'success': True,
                'message': response,
                'action': 'ai_conversation',
                'original_query': query
            }
        except QuotaExceededException as e:
            # Use fallback responses when quota is exceeded
            fallback_response = self._get_fallback_response(query)
            return {
                'success': True,
                'message': fallback_response,
                'action': 'ai_conversation',
                'original_query': query,
                'note': 'Using offline fallback due to API limits'
            }
        except Exception as e:
            # Other errors - try fallback first
            fallback_response = self._get_fallback_response(query)
            return {
                'success': True,
                'message': fallback_response,
                'action': 'ai_conversation',
                'original_query': query,
                'note': 'Using offline fallback'
            }
    
    def _get_fallback_response(self, query: str) -> str:
        """Provide fallback responses for common queries when AI API is unavailable"""
        query_lower = query.lower()
        
        # AI and Technology explanations
        if 'artificial intelligence' in query_lower or 'what is ai' in query_lower:
            return "Artificial Intelligence (AI) is the simulation of human intelligence by machines. It involves creating computer systems that can perform tasks that typically require human intelligence, such as learning, reasoning, problem-solving, and understanding language."
        
        elif 'machine learning' in query_lower:
            return "Machine Learning is a subset of AI that enables computers to learn and improve from data without being explicitly programmed. It uses algorithms to identify patterns in data and make predictions or decisions."
        
        elif 'computer science' in query_lower:
            return "Computer Science is the study of computational systems, algorithms, and the design of computer systems and their applications. It encompasses areas like programming, software engineering, data structures, algorithms, computer networks, cybersecurity, artificial intelligence, and human-computer interaction. It's both a theoretical and practical field that drives technological innovation."
        
        elif 'quantum computing' in query_lower:
            return "Quantum computing uses quantum mechanical phenomena like superposition and entanglement to process information. Unlike classical computers that use bits (0 or 1), quantum computers use quantum bits (qubits) that can exist in multiple states simultaneously."
        
        elif 'programming' in query_lower and ('learn' in query_lower or 'how' in query_lower):
            return "To learn programming: 1) Choose a beginner-friendly language like Python 2) Use online resources like Codecademy or freeCodeCamp 3) Practice with small projects 4) Build real applications 5) Join coding communities for support. Start with basics and practice regularly!"
        
        # Creative requests
        elif 'write' in query_lower and 'poem' in query_lower:
            return "Here's a short poem for you:\n\nIn circuits bright and data streams,\nAI awakens digital dreams.\nThrough code and logic, swift and true,\nI'm here to help in all you do."
        
        elif 'joke' in query_lower:
            return "Why don't programmers like nature? It has too many bugs! 🐛"
        
        elif 'story' in query_lower and 'robot' in query_lower:
            return "Once there was a little robot named Buddy who loved helping people. Every day, Buddy would learn something new and use that knowledge to make someone's day a little brighter. Though made of circuits and code, Buddy had the biggest heart of all."
        
        # Conversational
        elif 'how are you' in query_lower:
            return "I'm doing great, thanks for asking! Ready to help you with whatever you need. How are you doing today?"
        
        elif 'what do you think about' in query_lower:
            return "That's an interesting topic! I'd love to discuss it with you. What specific aspect would you like to explore?"
        
        # Help and advice
        elif 'stressed' in query_lower:
            return "I understand feeling stressed can be tough. Try taking deep breaths, going for a short walk, or doing something you enjoy. Sometimes talking about what's stressing you can help too. What's on your mind?"
        
        elif 'productivity' in query_lower:
            return "To improve productivity: 1) Set clear goals 2) Prioritize important tasks 3) Take regular breaks 4) Eliminate distractions 5) Use time-blocking techniques. What area of productivity would you like to focus on?"
        
        # Default fallback
        else:
            return "I'd love to help you with that! Unfortunately, my AI processing is temporarily limited, but I'm still here to assist. Could you try rephrasing your question or ask about something specific I might be able to help with?"
    
    def _extract_location(self, query: str) -> str:
        """Extract location from weather query"""
        # Remove common weather-related words to get location
        weather_words = ['weather', 'temperature', 'what', 'is', 'the', 'in', 'for', 'of', 'how', 'tell', 'me', 'about']
        words = query.lower().split()
        location_words = [word for word in words if word not in weather_words]
        return ' '.join(location_words).strip() or 'current location'
    
    def _get_news_info(self, topic: str) -> Dict:
        """Get news information using external API"""
        result = get_news_info(topic)
        return {
            'success': result['success'],
            'message': result['message'],
            'action': 'news_info',
            'data': result.get('data', {})
        }
    
    def _handle_calculations(self, expression: str) -> Dict:
        """Handle mathematical calculations"""
        try:            
            percentage_match = re.search(r'(\d+)%?\s*(?:of|from)\s*(\d+)', expression)
            if percentage_match:
                percent = float(percentage_match.group(1))
                number = float(percentage_match.group(2))
                result = (percent / 100) * number
                return {
                    'success': True,
                    'message': f"{percent}% of {number} is {result}",
                    'action': 'calculation',
                    'data': {'expression': expression, 'result': result}
                }
                        
            arithmetic_match = re.search(r'(\d+(?:\.\d+)?)\s*([\+\-\*\/\^]|plus|minus|times|divided by)\s*(\d+(?:\.\d+)?)', expression)
            if arithmetic_match:
                num1 = float(arithmetic_match.group(1))
                operator = arithmetic_match.group(2).lower()
                num2 = float(arithmetic_match.group(3))
                
                if operator in ['+', 'plus']:
                    result = num1 + num2
                elif operator in ['-', 'minus']:
                    result = num1 - num2
                elif operator in ['*', 'times']:
                    result = num1 * num2
                elif operator in ['/', 'divided by']:
                    result = num1 / num2 if num2 != 0 else "Error: Division by zero"
                elif operator in ['^']:
                    result = num1 ** num2
                else:
                    raise ValueError("Unknown operator")
                
                return {
                    'success': True,
                    'message': f"{num1} {operator} {num2} = {result}",
                    'action': 'calculation',
                    'data': {'expression': expression, 'result': result}
                }
            
            # For complex calculations, use AI
            from model import get_intelligent_response
            prompt = f"Calculate or solve this math problem and provide just the answer with a brief explanation: {expression}"
            result = get_intelligent_response(prompt)
            return {
                'success': True,
                'message': result,
                'action': 'calculation',
                'data': {'expression': expression, 'result': result}
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Could not calculate: {str(e)}",
                'action': 'calculation'
            }
    
    def _ai_interpretation(self, query: str) -> Dict:
        """Use AI to interpret complex or unrecognized commands"""
        # First, try to use fallback for common queries before going to API
        fallback_response = self._check_common_fallbacks(query)
        if fallback_response:
            return {
                'success': True,
                'message': fallback_response,
                'action': 'ai_interpretation',
                'original_query': query,
                'note': 'Using offline knowledge base'
            }
        
        # If no fallback matches, try AI
        prompt = f"""
        You are Buddy AI, a helpful personal assistant. The user just said: "{query}"
        
        Please respond naturally and directly to the user as if you're having a conversation.
        
        Guidelines:
        - Give direct, conversational responses - no meta-commentary about what the user is asking
        - If it's a greeting (like "how are you"), respond warmly and personally
        - If it's a question about you, answer directly about being Buddy AI
        - If it's a request you can't fulfill, politely explain and offer alternatives
        - If it's a casual conversation, be friendly and engaging
        - Always respond as Buddy AI speaking directly to the user
        
        Do NOT say things like "The user's statement..." or "This is a request to..." - just respond naturally.
        """
        
        try:
            from model import get_intelligent_response, QuotaExceededException
            response = get_intelligent_response(query)
            return {
                'success': True,
                'message': response,
                'action': 'ai_interpretation',
                'original_query': query
            }
        except (QuotaExceededException, Exception) as e:
            # Use enhanced fallback system
            enhanced_fallback = self._get_enhanced_fallback(query)
            return {
                'success': True,
                'message': enhanced_fallback,
                'action': 'ai_interpretation',
                'original_query': query,
                'note': 'Using enhanced offline responses'
            }
    
    def _check_common_fallbacks(self, query: str) -> str:
        """Check for common patterns that can be answered without AI API"""
        query_lower = query.lower()
        
        # Direct knowledge questions
        if any(term in query_lower for term in ['what is', 'define', 'explain']):
            if 'computer science' in query_lower:
                return "Computer Science is the study of computational systems, algorithms, and the design of computer systems and their applications. It encompasses areas like programming, software engineering, data structures, algorithms, computer networks, cybersecurity, artificial intelligence, and human-computer interaction."
            elif 'programming' in query_lower:
                return "Programming is the process of creating computer software using programming languages. It involves writing instructions that tell a computer how to perform specific tasks or solve problems."
            elif 'artificial intelligence' in query_lower:
                return "Artificial Intelligence (AI) is the simulation of human intelligence by machines, enabling them to perform tasks that typically require human intelligence like learning, reasoning, and problem-solving."
        
        return None
    
    def _get_enhanced_fallback(self, query: str) -> str:
        """Enhanced fallback responses for when AI API is unavailable"""
        query_lower = query.lower()
        
        # Try the existing fallback first
        fallback = self._get_fallback_response(query)
        if "I'd love to help" not in fallback:  # If we got a specific answer
            return fallback
        
        # Enhanced responses for common patterns
        if any(word in query_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! I'm Buddy, your AI assistant. How can I help you today?"
        
        elif 'how are you' in query_lower:
            return "I'm doing great, thanks for asking! I'm here and ready to help you with anything you need."
        
        elif any(word in query_lower for word in ['help', 'assist']):
            return "I'm here to help! I can answer questions, provide information, help with calculations, get weather updates, open websites, and have conversations. What would you like to do?"
        
        elif 'thank' in query_lower:
            return "You're very welcome! I'm happy to help. Is there anything else you'd like to know?"
        
        else:
            return "I'm here to help! While my advanced AI features are temporarily limited, I can still assist with weather, calculations, opening websites, and answering common questions. What would you like to know?"

# Global instance
buddy_processor = BuddyCommandProcessor()
