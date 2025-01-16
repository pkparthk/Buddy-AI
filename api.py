from flask import Flask, request, jsonify
from flask_cors import CORS
from main import process_query  # Import the process_query function from main.py
import os  # Import os to handle environment variables
import logging  # For logging

# Initialize the Flask application
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "https://buddy-ai-tfha.onrender.com"]}})

# CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def handle_chat():
    if request.method == 'OPTIONS':
        # Preflight request
        return '', 200  # Respond with HTTP 200 OK for OPTIONS requests
    
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
        return jsonify({'error': 'An error occurred', 'details': str(e)}), 500

if __name__ == '__main__':
    # Use environment variables for host and port, with defaults for local testing
    host = os.environ.get('HOST', '0.0.0.0')  # Bind to all network interfaces
    port = int(os.environ.get('PORT', 5000))  # Use Render's provided port or default to 5000
    
    # Run the Flask app
    app.run(host=host, port=port, debug=False)  # Set debug=False for production
