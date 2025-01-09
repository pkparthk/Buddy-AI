import React, { useState, useEffect, useRef } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { ScrollArea } from "./ui/scroll-area";

declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}
// Define the API_URL for backend communication (you can modify this for production)
const API_URL =
  import.meta.env.VITE_BACKEND_URL || "http://localhost:5000/api/chat";

  // const API_URL = "http://localhost:5000/api/chat";
    
const BuddyAI: React.FC = () => {
  const [isListening, setIsListening] = useState(false);
  const [conversation, setConversation] = useState<
    { role: "user" | "ai"; content: string }[]
  >([]);
  const [currentInput, setCurrentInput] = useState("");
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  // Speech recognition setup
  const recognition = useRef<null | (typeof window)["SpeechRecognition"]>(null);
  useEffect(() => {
    if ("SpeechRecognition" in window || "webkitSpeechRecognition" in window) {
      const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;
      recognition.current = new SpeechRecognition();
      recognition.current.continuous = false; // Stop after recognizing one input
      recognition.current.interimResults = false; // No interim results

      recognition.current.onresult = (event: {
        results: Iterable<unknown> | ArrayLike<unknown>;
      }) => {
        const transcript = Array.from(event.results)
          .map(
            (result: any) =>
              (result[0] as SpeechRecognitionAlternative).transcript
          )
          .join("");
        setCurrentInput(transcript);
        handleSubmit(transcript); // Automatically submit when speech recognition ends
      };
    } else {
      console.log("Speech recognition not supported");
    }
  }, []);

  // Text-to-speech setup
  const speak = (text: string) => {
    const utterance = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(utterance);
  };

  const toggleListening = () => {
    if (isListening) {
      recognition.current?.stop();
    } else {
      setCurrentInput(""); // Clear the input when starting to listen
      recognition.current?.start();
    }
    setIsListening(!isListening);
  };

  const handleSubmit = async (input?: string) => {
    const messageToSend = input || currentInput;
    if (messageToSend.trim() === "") return;

    setConversation((prev) => [
      ...prev,
      { role: "user", content: messageToSend },
    ]);

    try {
      // Ensure the backend URL is correctly configured
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: messageToSend }),
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await response.json();
      const aiResponse = data.response;

      setConversation((prev) => [...prev, { role: "ai", content: aiResponse }]);
      speak(aiResponse);
    } catch (error) {
      console.error("Error:", error);
      setConversation((prev) => [
        ...prev,
        { role: "ai", content: "Sorry, an error occurred." },
      ]);
      speak("Sorry, an error occurred.");
    }

    setCurrentInput("");
  };

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [conversation]);

  return (
    <div className="flex h-screen bg-gray-100 dark:bg-gray-900">
      {/* Sidebar */}
      <div className="w-64 bg-gray-800 text-white p-4 hidden md:block">
        <h2 className="text-2xl font-bold mb-4">Buddy AI</h2>
        <nav>
          <ul>
            <li className="mb-2">
              <a href="#" className="block p-2 rounded hover:bg-gray-700">
                New Chat
              </a>
            </li>
            {/* Add more sidebar items as needed */}
          </ul>
        </nav>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Chat Messages */}
        <ScrollArea className="flex-1 p-4" ref={scrollAreaRef}>
          {conversation.map((message, index) => (
            <div
              key={index}
              className={`mb-4 ${
                message.role === "user" ? "text-right" : "text-left"
              }`}
            >
              <div
                className={`inline-block p-2 rounded-lg ${
                  message.role === "user"
                    ? "bg-blue-500 text-white"
                    : "bg-gray-200 dark:bg-gray-700 text-black dark:text-white"
                }`}
              >
                {message.content}
              </div>
            </div>
          ))}
        </ScrollArea>

        {/* Input Area */}
        <div className="border-t border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center space-x-2">
            <Input
              type="text"
              value={currentInput}
              onChange={(e) => setCurrentInput(e.target.value)}
              placeholder="Type your message..."
              className="flex-1"
              onKeyPress={(e) => {
                if (e.key === "Enter") {
                  handleSubmit();
                }
              }}
            />
            <Button onClick={() => handleSubmit()}>Send</Button>
            <Button onClick={toggleListening} variant="outline">
              {isListening ? "Stop Listening" : "Start Listening"}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BuddyAI;
