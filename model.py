import os
from dotenv import load_dotenv
import google.generativeai as genai

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

def call_gemini_ai(prompt):
    """
    Makes a call to Google Gemini AI with the provided prompt.
    The API key is passed for authentication.
    """
    api_key = get_api_key()  # Retrieve the API key securely
    
    # Configure the API client with the API key
    genai.configure(api_key=api_key)
    
    try:
        # Use the correct model for your requirement
        model = genai.GenerativeModel("gemini-1.5-flash")  # Update to the correct model name
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    prompt = "Tell me about Artificial Intelligence."
    result = call_gemini_ai(prompt)
    print(f"Gemini AI response: {result}")
