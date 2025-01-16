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

chatStr = ""  # Initialize the global chat string

# Initialize the pyttsx3 engine globally
# engine = pyttsx3.init()

# Define a lock to prevent multiple threads from executing runAndWait at the same time
speech_lock = threading.Lock()

def speak(text):
    """
    Uses gTTS (Google Text-to-Speech) for text-to-speech functionality.
    This method speaks the entire response asynchronously.
    """
    def _speak():
        try:
            # Generate speech using gTTS
            tts = gTTS(text=text, lang='en')

            # Use a temporary file for storing the speech audio
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                temp_file_path = temp_file.name
                tts.save(temp_file_path)  # Save the speech to a temporary file

            # Initialize pygame mixer
            pygame.mixer.init()

            # Load and play the audio file
            pygame.mixer.music.load(temp_file_path)
            pygame.mixer.music.play()

            # Wait until the music finishes playing
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            # Explicitly stop the music to release the file handle
            pygame.mixer.music.stop()

            # Add a small delay to ensure the file is fully released
            time.sleep(0.5)

        finally:
            # Clean up the temporary audio file after playback
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except PermissionError:
                    print(f"Could not delete the file {temp_file_path} due to permission error.")
                    # If the file is still in use, try again after a small delay
                    time.sleep(1)
                    try:
                        os.remove(temp_file_path)
                    except Exception as e:
                        print(f"Error deleting file: {e}")

    # Run the speak function in a separate thread to avoid blocking the main thread
    threading.Thread(target=_speak).start()

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
    Processes each query and executes the corresponding task.
    """
    if 'open' in query:
        # Check if the query is a command to open a website
        sites = [["youtube", "https://www.youtube.com"], ["wikipedia", "https://www.wikipedia.com"], ["google", "https://www.google.com"]]
        for site in sites:
            if f"open {site[0]}" in query.lower():  # Case-insensitive matching
                speak(f"Opening {site[0]} sir...")
                webbrowser.open(site[1])
                return "Opening website..."  # Return a response here
    
    elif "the time" in query:
        # Check for time query
        hour = datetime.datetime.now().strftime("%H")
        minute = datetime.datetime.now().strftime("%M")
        speak(f"Sir, the time is {hour} hours and {minute} minutes.")
        return f"The time is {hour}:{minute}"  # Return the time as a string
    
    elif "buddy quit" in query:
        speak("Goodbye!")
        exit()
    
    elif "reset chat" in query:
        global chatStr
        chatStr = ""
        speak("Chat has been reset.")
        return "Chat has been reset."
    
    elif "shutdown" in query or "exit" in query:
        speak("Shutting down now. Goodbye!")
        print("Shutting down...")
        exit()
    
    else:
        # For other queries, chat with Gemini AI
        print("Chatting with Buddy AI...")
        return chat(query)  # Make sure chat returns a response

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
