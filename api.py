from flask import Flask, request, jsonify
from flask_cors import CORS
from main import process_query, set_speech_enabled  # Import the process_query function and speech control from main.py
import os  # Import os to handle environment variables
import logging  # For logging

# Initialize the Flask application
app = Flask(__name__)

# Disable speech in production environment (audio doesn't work well in serverless)
if os.environ.get('FLASK_ENV') == 'production':
    set_speech_enabled(False)
    print("Speech disabled for production environment")
else:
    set_speech_enabled(True)
    print("Speech enabled for development environment")

# Configure CORS for production and development
if os.environ.get('FLASK_ENV') == 'production':
    # Production CORS - Render + Vercel specific
    allowed_origins = [
        "https://buddy-ai-frontend.vercel.app",  # Update with your Vercel URL
        "https://your-buddy-ai.vercel.app",      # Alternative Vercel URL
        "http://localhost:5173",                 # Local development
        "http://localhost:3000"                  # Alternative local
    ]
else:
    # Development CORS
    allowed_origins = ["http://localhost:5173", "http://localhost:3000"]

CORS(app, resources={r"/*": {"origins": allowed_origins}})

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint for deployment platforms"""
    return jsonify({
        'status': 'healthy',
        'message': 'Buddy AI Backend is running!',
        'version': '1.0.0'
    }), 200

@app.route('/api/health', methods=['GET'])
def api_health():
    """API health check"""
    return jsonify({
        'api': 'healthy',
        'gemini_configured': bool(os.environ.get('GEMINI_API_KEY')),
        'features': ['chat', 'enhanced_commands', 'external_apis']
    }), 200

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def handle_chat():
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'Preflight check successful'})
        response.headers.add("Access-Control-Allow-Origin", request.headers.get('Origin', '*'))
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        return response, 200
    
    try:
        data = request.json  # Parse incoming JSON data
        query = data.get('query')  # Get the "query" field

        # Validate the query
        if not query:
            return jsonify({'error': 'No query provided'}), 400

        # Process the query
        response = process_query(query)

        # Return the AI-generated response
        return jsonify({'response': response})
    
    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return jsonify({'error': 'An error occurred', 'details': str(e)}), 500

if __name__ == '__main__':
    # Use environment variables for host and port, with defaults for local testing
    host = os.environ.get('HOST', '0.0.0.0')  # Bind to all network interfaces
    port = int(os.environ.get('PORT', 5000))  # Use Render's provided port or default to 5000
    
    # Run the Flask app
    app.run(host=host, port=port, debug=False)  # Set debug=False for production
