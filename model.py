import os
from dotenv import load_dotenv
import google.generativeai as genai
import json
from typing import Dict, List, Optional

# Load environment variables from the .env file
load_dotenv()

def get_api_key():
    """
    Retrieve the API key from the environment variable.
    """
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key is None:
        raise ValueError("API key not found. Please set the GEMINI_API_KEY environment variable.")
    return api_key

def call_gemini_ai(prompt, system_context=None):
    """
    Enhanced Gemini AI call with system context for better responses.
    """
    api_key = get_api_key()
    genai.configure(api_key=api_key)
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Add system context for better AI behavior
        if system_context:
            full_prompt = f"{system_context}\n\nUser: {prompt}"
        else:
            # Default Buddy system context
            full_prompt = f"""You are Buddy, a helpful personal AI assistant. Be conversational, friendly, and direct.
            
            Important guidelines:
            - Respond naturally and directly to the user
            - No meta-commentary like "The user is asking..." - just answer the question
            - Be warm and personal in your responses
            - When greeting someone, respond warmly
            - Answer questions about yourself directly as Buddy (not Buddy AI)
            - Keep responses conversational but helpful
            
            User: {prompt}"""
        
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        # Re-raise the exception instead of returning it as a string
        raise e

def get_intelligent_response(query: str, context: Dict = None) -> str:
    """
    Get an intelligent response for complex queries that require reasoning.
    """
    system_context = """You are Buddy AI, a helpful personal AI assistant.
    
    Important: Always respond directly and conversationally. Do NOT use meta-commentary.
    
    When users:
    - Greet you or ask how you are: Respond warmly and personally
    - Ask for help: Offer specific assistance 
    - Make casual conversation: Be friendly and engaging
    - Ask questions: Answer directly without explaining what they're asking
    
    Examples of what NOT to do:
    ❌ "The user is asking about..."
    ❌ "This appears to be a greeting..."
    ❌ "The user's statement indicates..."
    
    Examples of what TO do:
    ✅ "I'm doing great, thanks for asking!"
    ✅ "Hello! How can I help you today?"
    ✅ "I'm Buddy, your personal assistant."
    
    Always respond as Buddy speaking directly to the user in a natural, conversational way."""
    
    if context:
        system_context += f"\n\nAdditional context: {json.dumps(context)}"
    
    try:
        return call_gemini_ai(query, system_context)
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg or "rate" in error_msg.lower():
            # Raise a special exception for quota issues that can be caught by handlers
            raise QuotaExceededException(f"API quota exceeded: {error_msg}")
        else:
            raise e

class QuotaExceededException(Exception):
    """Custom exception for API quota exceeded errors"""
    pass

def analyze_command_intent(query: str) -> Dict:
    """
    Analyze the intent behind a user's command using AI.
    """
    analysis_prompt = f"""
    Analyze this user command and determine the intent: "{query}"
    
    Respond with a JSON object containing:
    - intent: the main action (e.g., "open_website", "search", "system_control", "information", "chat")
    - confidence: how confident you are (0.0 to 1.0)
    - entities: any specific items mentioned (websites, applications, topics)
    - suggested_action: what action should be taken
    
    Example response:
    {{
        "intent": "open_website",
        "confidence": 0.9,
        "entities": ["youtube"],
        "suggested_action": "open youtube.com"
    }}
    """
    
    try:
        response = call_gemini_ai(analysis_prompt)
        # Try to parse as JSON, fallback to text if it fails
        try:
            return json.loads(response)
        except:
            return {
                "intent": "chat",
                "confidence": 0.5,
                "entities": [],
                "suggested_action": "respond with AI",
                "raw_response": response
            }
    except Exception as e:
        return {
            "intent": "error",
            "confidence": 0.0,
            "entities": [],
            "suggested_action": "handle error",
            "error": str(e)
        }

if __name__ == '__main__':
    prompt = "Tell me about Artificial Intelligence."
    result = call_gemini_ai(prompt)
    print(f"Buddy response: {result}")

    # Test intent analysis
    test_query = "open youtube and search for python tutorials"
    intent = analyze_command_intent(test_query)
    print(f"Intent analysis: {intent}")
