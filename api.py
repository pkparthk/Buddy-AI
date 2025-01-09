from flask import Flask, request, jsonify
from flask_cors import CORS
from main import process_query  # Import the process_query function from main.py

app = Flask(__name__)
CORS(app)  # Enable CORS if you're calling the API from a different domain

@app.route('/api/chat', methods=['POST'])
def handle_chat():
    """
    Handle chat requests, process the query, and return a response.
    """
    data = request.json
    query = data.get('query')
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    response = process_query(query)  # Calls the process_query function from main.py
    
    return jsonify({'response': response})  # Return the response in JSON format

if __name__ == '__main__':
    app.run(debug=True, port=5000)
