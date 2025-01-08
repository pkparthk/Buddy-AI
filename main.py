import speech_recognition as sr
import os
import webbrowser
import datetime
import pyttsx3
from model import call_gemini_ai  # Ensure the function call_gemini_ai is correctly defined in model.py

chatStr = ""  # Initialize the global chat string

# Initialize the pyttsx3 engine globally
engine = pyttsx3.init()

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
        
        # Print and speak the response
        print(f"Buddy AI: {reply}")  # Display the answer as text in the console
        speak(reply)
        
        return reply
    except Exception as e:
        print(f"Error: {e}")
        speak("Sorry, an error occurred.")
        return "Sorry, an error occurred."

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
            
            # Print and speak the response
            print(f"Buddy AI: {response}")  # Display the answer as text in the console
            speak(response)
        else:
            print("Failed to get a response from Gemini AI.")
            speak("Sorry, I couldn't generate a response.")
    except Exception as e:
        print(f"Error: {e}")
        speak("Sorry, an error occurred while generating the response.")

def speak(text):
    """
    Uses pyttsx3 for text-to-speech functionality.
    This method speaks the entire response synchronously.
    """
    engine.say(text)
    engine.runAndWait()  # Wait for the speech to complete before moving on

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
            if f"open {site[0]}" in query:
                speak(f"Opening {site[0]} sir...")
                webbrowser.open(site[1])
    
    elif "the time" in query:
        # Check for time query
        hour = datetime.datetime.now().strftime("%H")
        minute = datetime.datetime.now().strftime("%M")
        speak(f"Sir, the time is {hour} hours and {minute} minutes.")

    elif "open facetime" in query:
        os.system(f"open /System/Applications/FaceTime.app")

    # elif "open pass" in query:
    #     os.system(f"open /Applications/Passky.app")

    elif "buddy quit" in query:
        speak("Goodbye!")
        exit()

    elif "reset chat" in query:
        global chatStr
        chatStr = ""
        speak("Chat has been reset.")

    elif "using artificial intelligence" in query:
        ai(prompt=query)

    elif "shutdown" in query or "exit" in query:
        speak("Shutting down now. Goodbye!")
        print("Shutting down...")
        exit()

    else:
        # For other queries, chat with Gemini AI
        print("Chatting with Buddy AI...")
        chat(query)

if __name__ == '__main__':
    print("Welcome to Buddy A.I")
    speak("Buddy is now active.")
    
    while True:
        query = takeCommand().lower()
        process_query(query)
