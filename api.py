from flask import Flask, request, jsonify
from flask_cors import CORS
from main import process_query  # Import the process_query function from main.py
import os  # Import os to handle environment variables

app = Flask(__name__)
CORS(app)  # Enable CORS to allow requests from different domains

@app.route('/api/chat', methods=['POST'])
def handle_chat():
    """
    Handle chat requests, process the query, and return a response.
    """
    data = request.json
    query = data.get('query')
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    try:
        response = process_query(query)  # Calls the process_query function from main.py
        return jsonify({'response': response})  # Return the response in JSON format
    except Exception as e:
        # Handle unexpected errors gracefully
        return jsonify({'error': 'An error occurred while processing the query', 'details': str(e)}), 500

if __name__ == '__main__':
    # Use environment variables for host and port, with sensible defaults for local testing
    host = os.environ.get('HOST', '0.0.0.0')  # Bind to all network interfaces
    port = int(os.environ.get('PORT', 5000))  # Use Render's provided port or default to 5000
    app.run(host=host, port=port, debug=False)  # Set debug=False for production
