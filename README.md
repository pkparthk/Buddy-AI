# Buddy AI

**Buddy AI** is a voice assistant powered by **Gemini AI**. It allows users to interact with an AI for various tasks such as chatting, answering questions, browsing the web, and performing system commands through voice commands.

## Watch Demo Video
   🎥 [https://vimeo.com/1078472414?share=copy](#)  
   Click the link above to see Buddy AI in action!

## Table of Contents
1. [Installation](#installation)
2. [Usage](#usage)
3. [Features](#features)
4. [Configuration](#configuration)
5. [Contributing](#contributing)
6. [License](#license)
7. [Contact](#contact)

## Installation

### Prerequisites
- Python 3.x
- Google API key for Gemini AI (you will need to set up your API access).
- Required Python libraries and dependencies.

### Steps to Install
1. Clone the repository:
   ```bash
   git clone https://github.com/pkparthk/buddy-ai.git
   ```

2. Navigate to the project folder:
   ```bash
   cd buddy-ai
   ```

3. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # On Linux/MacOS
   source venv/bin/activate
   # On Windows
   venv\Scripts\activate
   ```

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Create a `.env` file in the root directory and add your Google API key:
   ```
   API_KEY=your_google_api_key_here
   ```

6. Run the application:
   ```bash
   python main.py
   ```

## Usage

### Voice Commands
Buddy AI supports a variety of voice commands, including:
- **Chatting**: "Tell me about Artificial Intelligence."
- **Opening Websites**: "Open YouTube," "Open Google."
- **System Information**: "What time is it?"
- **Application Management**: "Open FaceTime," "Buddy quit."
- **Resetting Chat**: "Reset chat."

### Keyboard Interaction
In case voice commands are not feasible, users can interact via text input.

## Features
- Voice interaction using **SpeechRecognition** and **Pyttsx3**.
- Integration with Google **Gemini AI** for advanced conversational capabilities.
- Customizable commands for opening applications and performing tasks.
- Real-time API responses using a secure `.env` file for configuration.

## Configuration

### Setting Up Google Gemini AI
1. Obtain an API key from the [Google Cloud Console](https://console.cloud.google.com/).
2. Add the key to your `.env` file as `API_KEY`.

### Adding New Features
1. Update the `main.py` file to define new commands.
2. Add any necessary dependencies to `requirements.txt` and install them.

## Contributing

1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add your message here"
   ```
4. Push the branch:
   ```bash
   git push origin feature/your-feature-name
   ```
5. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions, feedback, or contributions, reach out at:
- **Email**: [0xparthk@gmail.com](mailto:0xparthk.com)
- **GitHub**: [pkparthk](https://github.com/pkparthk)

