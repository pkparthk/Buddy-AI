import speech_recognition as sr
import os
import webbrowser
import datetime
# import pyttsx3
from gtts import gTTS
from model import call_gemini_ai  # Ensure the function call_gemini_ai is correctly defined in model.py
import threading  # Import the threading module
import pygame
import tempfile
import time
import platform
from enhanced_commands import buddy_processor 

chatStr = ""  # Initialize the global chat string

# Initialize the pyttsx3 engine globally
# engine = pyttsx3.init()

# Define a lock to prevent multiple threads from executing runAndWait at the same time
speech_lock = threading.Lock()

# Global flag to control speech functionality
ENABLE_SPEECH = True

def set_speech_enabled(enabled):
    """
    Enable or disable speech functionality (useful for deployment environments)
    """
    global ENABLE_SPEECH
    ENABLE_SPEECH = enabled

def speak(text):
    """
    Uses gTTS (Google Text-to-Speech) for text-to-speech functionality.
    This method speaks the entire response asynchronously with improved error handling.
    """
    # If speech is disabled (e.g., in deployment), just print the text
    if not ENABLE_SPEECH:
        print(f"Buddy AI: {text}")
        return
    
    def _speak():
        temp_file_path = None
        try:
            # Generate speech using gTTS
            tts = gTTS(text=text, lang='en')

            # Use a temporary file for storing the speech audio
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                temp_file_path = temp_file.name
                tts.save(temp_file_path)  # Save the speech to a temporary file

            # Initialize pygame mixer with better error handling
            try:
                # Quit any existing mixer instance first
                pygame.mixer.quit()
                time.sleep(0.1)  # Brief pause
                
                # Initialize with specific parameters for better compatibility
                pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
                pygame.mixer.init()
                
                # Load and play the audio file
                pygame.mixer.music.load(temp_file_path)
                pygame.mixer.music.play()

                # Wait until the music finishes playing
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                    
            except pygame.error as pe:
                print(f"Pygame error: {pe}")
                # Fallback: just print the text if audio fails
                print(f"Audio failed, text output: {text}")
                
        except Exception as e:
            print(f"Error in speech synthesis: {e}")
            # Fallback: just print the text
            print(f"Speech synthesis failed, text output: {text}")
        finally:
            # Clean up the temporary audio file after playback
            cleanup_temp_file(temp_file_path)

    # Run the speak function in a separate thread to avoid blocking the main thread
    threading.Thread(target=_speak, daemon=True).start()

def cleanup_temp_file(file_path):
    """
    Improved temporary file cleanup with multiple retry attempts and better error handling
    """
    if not file_path or not os.path.exists(file_path):
        return
    
    # Stop pygame mixer completely to release file handles
    try:
        if pygame.mixer.get_init():  # Check if mixer is initialized
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()  # Unload the music to release file handle
            pygame.mixer.quit()
        time.sleep(0.5)  # Give time for file handles to be released
    except Exception as cleanup_error:
        print(f"Error during pygame cleanup: {cleanup_error}")
    
    # Multiple attempts to delete the file
    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return  # Successfully deleted
        except PermissionError:
            if attempt < max_attempts - 1:
                time.sleep(0.5 * (attempt + 1))  # Increasing delay
            else:
                # As a last resort, try to schedule deletion on next reboot (Windows)
                try:
                    import platform
                    if platform.system() == "Windows":
                        os.system(f'echo del "{file_path}" >> %TEMP%\\cleanup_temp_files.bat')
                except:
                    pass
                print(f"Could not delete temp file {file_path} after {max_attempts} attempts")
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
            break

# def speak(text):
#     """
#     Uses pyttsx3 for text-to-speech functionality.
#     This method speaks the entire response asynchronously.
#     """
#     def _speak():
#         with speech_lock:  # Ensures only one thread runs the speech synthesis at a time
#             engine.say(text)
#             engine.runAndWait()  # Wait for the speech to complete before moving on

#     # Run the speak function in a separate thread to avoid blocking
#     threading.Thread(target=_speak).start()

def chat(query):
    """
    Handles chat interactions with Gemini AI.
    """
    global chatStr
    print(f"Chat History:\n{chatStr}")  # Debug: print the current conversation history
    
    # Update conversation with the user's query
    chatStr += f"User: {query}\nbuddy: "
    
    try:
        # Get the response from Gemini AI
        reply = call_gemini_ai(chatStr)
        
        # Update the conversation string with the reply after speaking
        chatStr += f"{reply}\n"
        
        # Print and speak the response only once
        print(f"Buddy AI: {reply}")  # Display the answer as text in the console
        speak(reply)  # Call speak here only once
        
        return reply  # Return the AI reply for use in Flask response
    except Exception as e:
        print(f"Error: {e}")
        speak("Sorry, an error occurred.")
        return "Sorry, an error occurred."  # Return error message to Flask

def ai(prompt):
    """
    Generates a response using Gemini AI for specific prompts.
    """
    try:
        response = call_gemini_ai(prompt)
        if response:
            filename = f"Gemini/{''.join(prompt.split('intelligence')[1:]).strip()}.txt"
            if not os.path.exists("Gemini"):
                os.mkdir("Gemini")
            with open(filename, "w") as f:
                f.write(f"Buddy response for Prompt: {prompt}\n*************************\n\n{response}")
            
            # Print and speak the response only once
            print(f"Buddy AI: {response}")  # Display the answer as text in the console
            speak(response)  # Call speak here only once
        else:
            print("Failed to get a response from Gemini AI.")
            speak("Sorry, I couldn't generate a response.")
    except Exception as e:
        print(f"Error: {e}")
        speak("Sorry, an error occurred while generating the response.")

def takeCommand():
    """
    Captures voice input and converts it into text.
    """
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
        try:
            print("Recognizing...")
            query = r.recognize_google(audio, language="en-in")
            print(f"User said: {query}")
            return query
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return "Sorry, I did not catch that."
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return "Sorry, I couldn't connect to the service."

def process_query(query):
    """
    Enhanced query processing using Buddy AI intelligence.
    """
    # Special commands that should be handled directly
    if "buddy quit" in query.lower():
        speak("Goodbye!")
        exit()
    
    elif "reset chat" in query.lower():
        global chatStr
        chatStr = ""
        speak("Chat has been reset.")
        return "Chat has been reset."
    
    elif any(word in query.lower() for word in ["shutdown", "exit"]):
        speak("Shutting down now. Goodbye!")
        print("Shutting down...")
        exit()
    
    # Use enhanced command processor for all other queries
    try:
        result = buddy_processor.process_command(query)
        
        if result['success']:
            speak(result['message'])
            return result['message']
        else:
            # If command processing fails, fall back to AI chat
            print("Falling back to AI chat...")
            return chat(query)
            
    except Exception as e:
        print(f"Error in command processing: {e}")
        # Fall back to AI chat if there's an error
        return chat(query)

def start_listening():
    """
    This function starts listening for voice input, sends the input to `process_query`, 
    and automatically stops the listening process after sending.
    """
    print("Started listening for voice input...")
    query = takeCommand()  # Get the user's voice input
    if query:
        print("Processing query...")
        response = process_query(query)  # Process the query (i.e., chat or other commands)
        print(f"Response from Buddy AI: {response}")
    else:
        print("No input received, stopping listening.")
