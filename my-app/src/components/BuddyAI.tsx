import React, { useState, useEffect, useRef } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { ScrollArea } from "./ui/scroll-area";
import WelcomeMessage from "./WelcomeMessage";

declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

const API_URL =
  import.meta.env.VITE_BACKEND_URL || "http://localhost:5000/api/chat";

const BuddyAI: React.FC = () => {
  const [isListening, setIsListening] = useState(false);
  const [conversation, setConversation] = useState<
    { role: "user" | "ai"; content: string; timestamp: Date }[]
  >([]);
  const [currentInput, setCurrentInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [isConnected, setIsConnected] = useState(true);
  const [showQuickCommands, setShowQuickCommands] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [showWelcome, setShowWelcome] = useState(true);
  const [sidebarWidth, setSidebarWidth] = useState(280);
  const [isResizing, setIsResizing] = useState(false);

  const quickCommands = [
    {
      text: "Open YouTube",
      icon: "🎥",
      category: "Web",
      color: "from-red-500 to-red-600",
    },
    {
      text: "Open Gmail",
      icon: "📧",
      category: "Web",
      color: "from-blue-500 to-blue-600",
    },
    {
      text: "Open Google",
      icon: "🔍",
      category: "Web",
      color: "from-green-500 to-green-600",
    },
    {
      text: "Open GitHub",
      icon: "💻",
      category: "Web",
      color: "from-gray-700 to-gray-800",
    },
    {
      text: "Open Netflix",
      icon: "🎬",
      category: "Web",
      color: "from-red-600 to-red-700",
    },
    {
      text: "What time is it?",
      icon: "⏰",
      category: "Info",
      color: "from-yellow-500 to-yellow-600",
    },
    {
      text: "Show system information",
      icon: "💾",
      category: "System",
      color: "from-purple-500 to-purple-600",
    },
    {
      text: "Check battery level",
      icon: "🔋",
      category: "System",
      color: "from-green-500 to-green-600",
    },
    {
      text: "Open calculator",
      icon: "🧮",
      category: "Apps",
      color: "from-blue-500 to-blue-600",
    },
    {
      text: "Open VS Code",
      icon: "⚡",
      category: "Apps",
      color: "from-blue-600 to-blue-700",
    },
    {
      text: "Get weather for London",
      icon: "🌤️",
      category: "Info",
      color: "from-cyan-500 to-cyan-600",
    },
    {
      text: "Search for Python tutorials",
      icon: "🐍",
      category: "Search",
      color: "from-yellow-600 to-yellow-700",
    },
  ];

  const scrollAreaRef = useRef<HTMLDivElement>(null);

  // Speech recognition setup
  const recognition = useRef<null | (typeof window)["SpeechRecognition"]>(null);

  useEffect(() => {
    if ("SpeechRecognition" in window || "webkitSpeechRecognition" in window) {
      const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;
      recognition.current = new SpeechRecognition();
      recognition.current.continuous = false;
      recognition.current.interimResults = false;
      recognition.current.lang = "en-US";

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
        handleSubmit(transcript);
      };

      recognition.current.onerror = (event: any) => {
        console.error("Speech recognition error:", event.error);
        setIsListening(false);
      };

      recognition.current.onend = () => {
        setIsListening(false);
      };
    } else {
      console.log("Speech recognition not supported");
    }
  }, []);

  // Enhanced text-to-speech with better voice selection
  const speak = (text: string) => {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();

      const utterance = new SpeechSynthesisUtterance(text);

      const voices = window.speechSynthesis.getVoices();
      const preferredVoice = voices.find(
        (voice) =>
          voice.name.includes("Microsoft") ||
          voice.name.includes("Google") ||
          voice.lang.startsWith("en")
      );

      if (preferredVoice) {
        utterance.voice = preferredVoice;
      }

      utterance.rate = 0.9;
      utterance.pitch = 1;
      utterance.volume = 0.8;

      window.speechSynthesis.speak(utterance);
    }
  };

  const toggleListening = () => {
    if (isListening) {
      recognition.current?.stop();
    } else {
      setCurrentInput("");
      recognition.current?.start();
    }
    setIsListening(!isListening);
  };

  const handleSubmit = async (input?: string) => {
    const messageToSend = input || currentInput;
    if (messageToSend.trim() === "") return;

    // Hide welcome message when user sends first message
    if (showWelcome) {
      setShowWelcome(false);
    }

    const userMessage = {
      role: "user" as const,
      content: messageToSend,
      timestamp: new Date(),
    };

    setConversation((prev) => [...prev, userMessage]);
    setCurrentInput("");
    setIsTyping(true);
    setIsConnected(true);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: messageToSend }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const aiResponse = data.response;

      const aiMessage = {
        role: "ai" as const,
        content: aiResponse,
        timestamp: new Date(),
      };

      setConversation((prev) => [...prev, aiMessage]);
      speak(aiResponse);
    } catch (error) {
      console.error("Error:", error);
      setIsConnected(false);
      const errorMessage = {
        role: "ai" as const,
        content:
          "I'm having trouble connecting to my services right now. Please check if the backend server is running and try again.",
        timestamp: new Date(),
      };
      setConversation((prev) => [...prev, errorMessage]);
      speak("Sorry, I'm having connection issues. Please try again.");
    } finally {
      setIsTyping(false);
    }
  };

  const clearConversation = () => {
    setConversation([]);
    setShowWelcome(true);
  };

  const handleQuickCommand = (command: string) => {
    setCurrentInput(command);
    handleSubmit(command);
    setShowQuickCommands(false);
  };

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [conversation]);

  // Mobile detection and responsive handling
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
      // Close sidebar on desktop
      if (window.innerWidth >= 768) {
        setSidebarOpen(false);
      }
    };

    checkMobile();
    window.addEventListener("resize", checkMobile);

    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  // Resize handler for desktop sidebar
  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizing(true);

    const handleMouseMove = (e: MouseEvent) => {
      const newWidth = Math.max(240, Math.min(500, e.clientX));
      setSidebarWidth(newWidth);
    };

    const handleMouseUp = () => {
      setIsResizing(false);
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
    };

    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseup", handleMouseUp);
  };

  // Prevent body scrolling when mobile sidebar is open to avoid background gaps
  useEffect(() => {
    if (isMobile && sidebarOpen) {
      // Prevent background scrolling and add a class to mask the body background
      document.body.style.overflow = "hidden";
      document.body.classList.add("mobile-sidebar-open");
    } else {
      document.body.style.overflow = "";
      document.body.classList.remove("mobile-sidebar-open");
    }

    return () => {
      document.body.style.overflow = "";
      document.body.classList.remove("mobile-sidebar-open");
    };
  }, [isMobile, sidebarOpen]);

  // Welcome message on first load
  useEffect(() => {
    if (conversation.length === 0) {
      const welcomeMessage = {
        role: "ai" as const,
        content:
          "Hi! I’m Buddy, your smart assistant.\nI can open sites, control your system, and answer questions.",
        timestamp: new Date(),
      };
      setConversation([welcomeMessage]);
    }
  }, []);

  return (
    <div
      className={`flex h-screen theme-background overflow-hidden relative ${
        isResizing ? "cursor-col-resize" : ""
      }`}
    >
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -inset-10 opacity-20">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyan-400/30 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute top-3/4 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
          <div className="absolute bottom-1/4 left-1/2 w-96 h-96 bg-cyan-500/20 rounded-full blur-3xl animate-pulse delay-2000"></div>
          <div className="absolute top-1/2 right-1/3 w-64 h-64 bg-pink-500/10 rounded-full blur-2xl animate-bounce duration-3000"></div>
        </div>

        <div className="absolute inset-0">
          {[...Array(20)].map((_, i) => (
            <div
              key={i}
              className="absolute w-1 h-1 bg-white/20 rounded-full animate-float"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 3}s`,
                animationDuration: `${3 + Math.random() * 4}s`,
              }}
            />
          ))}
        </div>
      </div>

      {/* Mobile sidebar overlay (single overlay) */}
      {isMobile && sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/80 backdrop-blur-md z-[900]"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Enhanced Sidebar with mobile support */}
      <div
        className={`relative ${
          isMobile
            ? "fixed inset-0 left-0 right-0 transform transition-transform duration-300 ease-in-out z-[1000] safe-area-full"
            : "z-10"
        } ${isMobile && !sidebarOpen ? "-translate-x-full" : "translate-x-0"} ${
          isMobile ? "w-full" : ""
        } theme-sidebar text-white p-3 md:p-4 ${
          isMobile ? "" : "border-r theme-border"
        } shadow-2xl transition-all duration-300`}
        style={
          !isMobile
            ? { width: `${sidebarWidth}px` }
            : { width: "100vw", height: "100vh" }
        }
      >
        {/* Mobile header */}
        {isMobile && (
          <div className="flex justify-between items-center mb-4 pb-3 border-b border-white/20">
            <h3 className="text-lg font-bold text-white">Menu</h3>
            <button
              onClick={() => setSidebarOpen(false)}
              className="text-gray-300 hover:text-white p-2 hover:bg-white/10 rounded-lg transition-colors"
            >
              ✕
            </button>
          </div>
        )}
        <div className="flex items-center space-x-3 mb-4 group">
          <div className="relative">
            <div
              className={`${
                isMobile ? "w-10 h-10" : "w-14 h-14"
              } bg-gradient-to-r from-blue-500 via-purple-500 to-cyan-500 rounded-full flex items-center justify-center shadow-lg group-hover:shadow-xl transition-all duration-300 animate-pulse`}
            >
              <span
                className={`${isMobile ? "text-lg" : "text-2xl"} font-bold`}
              >
                🤖
              </span>
            </div>
            <div
              className={`absolute -bottom-1 -right-1 ${
                isMobile ? "w-3 h-3" : "w-5 h-5"
              } rounded-full ${
                isConnected ? "bg-green-500" : "bg-red-500"
              } border-2 border-black/50 animate-pulse`}
            ></div>
          </div>
          <div>
            <h2
              className={`${
                isMobile ? "text-lg" : "text-2xl"
              } font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent`}
            >
              Buddy AI
            </h2>
            <p
              className={`${
                isMobile ? "text-xs" : "text-sm"
              } text-gray-300 font-medium`}
            >
              Intelligent Assistant
            </p>
          </div>
        </div>

        <nav className="space-y-2 mb-3">
          <button
            onClick={clearConversation}
            className={`w-full flex items-center space-x-3 ${
              isMobile ? "p-2" : "p-4"
            } rounded-xl hover:bg-white/10 transition-all duration-300 group hover:shadow-lg transform hover:-translate-y-1`}
          >
            <span className="group-hover:scale-125 transition-transform text-lg">
              🗨️
            </span>
            <span
              className={`${isMobile ? "text-sm" : "text-base"} font-medium`}
            >
              New Conversation
            </span>
          </button>

          <button
            onClick={() => setShowQuickCommands(!showQuickCommands)}
            className={`w-full flex items-center space-x-3 ${
              isMobile ? "p-2" : "p-4"
            } rounded-xl hover:bg-white/10 transition-all duration-300 group hover:shadow-lg transform hover:-translate-y-1`}
          >
            <span className="group-hover:scale-125 transition-transform text-lg">
              ⚡
            </span>
            <span
              className={`${isMobile ? "text-sm" : "text-base"} font-medium`}
            >
              Quick Commands
            </span>
            <span
              className={`ml-auto transition-transform duration-300 ${
                showQuickCommands ? "rotate-180" : ""
              }`}
            >
              ▼
            </span>
          </button>

          <div
            className={`${
              isMobile ? "p-3" : "p-4"
            } rounded-xl theme-surface border theme-border`}
          >
            <div className="flex items-center justify-between">
              <span
                className={`${
                  isMobile ? "text-xs" : "text-sm"
                } theme-text-muted font-medium`}
              >
                Connection Status
              </span>
              <div className="flex items-center space-x-2">
                <div
                  className={`w-2 h-2 rounded-full ${
                    isConnected ? "bg-green-500" : "bg-red-500"
                  } animate-pulse shadow-lg`}
                ></div>
                <span
                  className={`${
                    isMobile ? "text-xs" : "text-sm"
                  } font-semibold ${
                    isConnected ? "text-green-400" : "text-red-400"
                  }`}
                >
                  {isConnected ? "Online" : "Offline"}
                </span>
              </div>
            </div>
          </div>
        </nav>

        {/* Quick Commands Panel */}
        {showQuickCommands && (
          <div className="space-y-2 max-h-72 overflow-y-auto">
            <h3
              className={`${
                isMobile ? "text-sm" : "text-lg"
              } font-semibold text-gray-300 border-b border-white/10 pb-2`}
            >
              Quick Commands
            </h3>
            <div className="grid grid-cols-1 gap-1">
              {quickCommands.map((command, index) => (
                <button
                  key={index}
                  onClick={() => handleQuickCommand(command.text)}
                  className={`flex items-center space-x-2 ${
                    isMobile ? "p-1.5" : "p-2"
                  } text-sm rounded-lg hover:bg-white/10 transition-all duration-200 group text-left`}
                >
                  <span
                    className={`${
                      isMobile ? "text-sm" : "text-lg"
                    } group-hover:scale-110 transition-transform`}
                  >
                    {command.icon}
                  </span>
                  <div>
                    <div
                      className={`${
                        isMobile ? "text-xs" : "text-sm"
                      } text-gray-200`}
                    >
                      {command.text}
                    </div>
                    <div className="text-xs text-gray-500">
                      {command.category}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Desktop Resize Handle */}
        {!isMobile && (
          <div
            className="absolute top-0 right-0 w-1 h-full bg-white/20 hover:bg-white/40 cursor-col-resize transition-colors group"
            onMouseDown={handleMouseDown}
          >
            <div className="absolute right-0 top-1/2 transform -translate-y-1/2 w-1 h-12 bg-white/30 group-hover:bg-white/50 rounded-l transition-colors"></div>
          </div>
        )}
      </div>

      {/* Main Chat Area */}
      <div
        className={`relative z-10 flex-1 flex flex-col transition-all duration-300 ${
          isMobile && sidebarOpen ? "opacity-30 pointer-events-none" : ""
        }`}
        style={{
          willChange: isMobile && sidebarOpen ? "opacity" : undefined,
        }}
      >
        {/* Enhanced Chat Header with mobile menu button */}
        <div
          className={`theme-surface border-b theme-border ${
            isMobile ? "p-4" : "p-5"
          } shadow-xl`}
        >
          <div className="flex items-center justify-between max-w-6xl mx-auto">
            <div className="flex items-center space-x-3">
              {isMobile && (
                <button
                  onClick={() => setSidebarOpen(true)}
                  className="text-white p-2 hover:bg-white/10 rounded-lg transition-colors"
                >
                  ☰
                </button>
              )}
              <div className="relative">
                <div
                  className={`${
                    isMobile ? "w-10 h-10" : "w-12 h-12"
                  } bg-gradient-to-r from-green-400 via-blue-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg animate-pulse`}
                >
                  {isTyping ? (
                    <div className="flex space-x-1">
                      <div
                        className={`${
                          isMobile ? "w-0.5 h-0.5" : "w-1 h-1"
                        } bg-white rounded-full animate-bounce`}
                      ></div>
                      <div
                        className={`${
                          isMobile ? "w-0.5 h-0.5" : "w-1 h-1"
                        } bg-white rounded-full animate-bounce delay-100`}
                      ></div>
                      <div
                        className={`${
                          isMobile ? "w-0.5 h-0.5" : "w-1 h-1"
                        } bg-white rounded-full animate-bounce delay-200`}
                      ></div>
                    </div>
                  ) : (
                    <span className={`${isMobile ? "text-base" : "text-lg"}`}>
                      🧠
                    </span>
                  )}
                </div>
                {isListening && (
                  <div className="absolute inset-0 bg-red-500/50 rounded-full animate-ping"></div>
                )}
              </div>
              <div>
                <h1
                  className={`text-white font-bold ${
                    isMobile ? "text-lg" : "text-xl"
                  } bg-gradient-to-r from-white to-gray-200 bg-clip-text text-transparent`}
                >
                  {isTyping
                    ? "Thinking..."
                    : isListening
                    ? "Listening..."
                    : "Ready to help"}
                </h1>
                <p
                  className={`text-gray-300 ${
                    isMobile ? "text-xs" : "text-sm"
                  } font-medium`}
                >
                  {isListening ? "Speak now..." : "Your intelligent assistant"}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2 md:space-x-4">
              {/* {!isMobile && (
                <div className="text-gray-300 text-sm bg-white/10 px-4 py-2 rounded-lg backdrop-blur-sm border border-white/10 font-mono">
                  {new Date().toLocaleTimeString()}
                </div>
              )} */}
              <div className="flex items-center space-x-2 bg-white/10 px-3 py-2 rounded-lg backdrop-blur-sm border border-white/10">
                <div
                  className={`w-2 h-2 rounded-full ${
                    isConnected ? "bg-green-500" : "bg-red-500"
                  } animate-pulse`}
                ></div>
                <span
                  className={`${
                    isMobile ? "text-xs" : "text-sm"
                  } text-gray-300 font-medium`}
                >
                  {conversation.length} {isMobile ? "" : "messages"}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Enhanced Chat Messages */}
        <ScrollArea
          className={`flex-1 ${isMobile ? "p-3" : "p-6"}`}
          ref={scrollAreaRef}
        >
          <div className="max-w-6xl mx-auto space-y-4">
            {conversation.length === 0 && showWelcome ? (
              <WelcomeMessage onGetStarted={() => setShowWelcome(false)} />
            ) : (
              conversation.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${
                    message.role === "user" ? "justify-end" : "justify-start"
                  } animate-in slide-in-from-bottom-5 duration-500`}
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <div
                    className={`${
                      isMobile
                        ? "max-w-[85%] px-4 py-3 text-sm"
                        : "max-w-xs lg:max-w-2xl px-6 py-4"
                    } chat-bubble shadow-xl transition-all duration-300 hover:shadow-2xl hover:-translate-y-1 ${
                      message.role === "user"
                        ? "chat-bubble-user theme-text-primary ml-auto border theme-border"
                        : "chat-bubble-ai theme-text-primary mr-auto border theme-border"
                    }`}
                  >
                    <div
                      className={`whitespace-pre-wrap leading-relaxed font-medium ${
                        isMobile ? "text-sm" : ""
                      }`}
                    >
                      {message.content}
                    </div>
                    <div
                      className={`text-xs mt-2 flex items-center space-x-2 ${
                        message.role === "user"
                          ? "text-blue-100"
                          : "text-gray-300"
                      }`}
                    >
                      <span className="font-mono">
                        {message.timestamp.toLocaleTimeString()}
                      </span>
                      {message.role === "ai" && (
                        <div className="flex items-center space-x-1">
                          <span className="w-1 h-1 bg-green-500 rounded-full animate-pulse"></span>
                          <span className="text-green-400 text-xs">AI</span>
                        </div>
                      )}
                      {message.role === "user" && (
                        <div className="flex items-center space-x-1">
                          <span className="w-1 h-1 bg-blue-300 rounded-full"></span>
                          <span className="text-blue-200 text-xs">You</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}

            {isTyping && (
              <div className="flex justify-start animate-in slide-in-from-bottom-5 duration-300">
                <div
                  className={`chat-bubble-ai theme-text-primary ${
                    isMobile ? "px-4 py-3" : "px-6 py-4"
                  } mr-auto border theme-border shadow-xl`}
                >
                  <div className="flex items-center space-x-3">
                    <div className="flex space-x-1">
                      <div
                        className={`${
                          isMobile ? "w-1.5 h-1.5" : "w-2 h-2"
                        } bg-blue-400 rounded-full animate-bounce`}
                      ></div>
                      <div
                        className={`${
                          isMobile ? "w-1.5 h-1.5" : "w-2 h-2"
                        } bg-purple-400 rounded-full animate-bounce`}
                        style={{ animationDelay: "0.1s" }}
                      ></div>
                      <div
                        className={`${
                          isMobile ? "w-1.5 h-1.5" : "w-2 h-2"
                        } bg-cyan-400 rounded-full animate-bounce`}
                        style={{ animationDelay: "0.2s" }}
                      ></div>
                    </div>
                    <span
                      className={`${
                        isMobile ? "text-xs" : "text-sm"
                      } text-gray-300 font-medium`}
                    >
                      AI is thinking...
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>

        {/* Enhanced Input Area with mobile optimization */}
        <div
          className={`theme-surface border-t theme-border p-4 md:p-5 shadow-xl transition-all duration-300 ${
            isMobile && sidebarOpen
              ? "translate-y-24 opacity-0 pointer-events-none"
              : ""
          }`}
        >
          <div className="max-w-5xl mx-auto">
            <div
              className={`flex items-center space-x-2 md:space-x-4 ${
                isMobile ? "flex-col space-y-3 space-x-0" : ""
              }`}
            >
              <div className={`${isMobile ? "w-full" : "flex-1"} relative`}>
                <Input
                  type="text"
                  value={currentInput}
                  onChange={(e) => setCurrentInput(e.target.value)}
                  placeholder={
                    isMobile
                      ? "Ask me anything..."
                      : "Ask me anything... Try 'Open YouTube' or 'What time is it?'"
                  }
                  className="theme-input pr-12 py-3 md:py-4 text-base md:text-sm transition-all duration-300 shadow-lg hover:shadow-xl font-medium"
                  onKeyPress={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      handleSubmit();
                    }
                  }}
                  disabled={isTyping}
                />
                {currentInput && (
                  <button
                    onClick={() => setCurrentInput("")}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 theme-text-muted hover:theme-text-primary transition-colors hover:scale-110 transition-transform"
                  >
                    ✕
                  </button>
                )}
              </div>

              <div
                className={`flex ${
                  isMobile ? "w-full justify-center" : ""
                } space-x-2 md:space-x-4`}
              >
                <Button
                  onClick={() => handleSubmit()}
                  disabled={isTyping || !currentInput.trim()}
                  className={`theme-btn-primary ${
                    isMobile ? "flex-1 px-6" : "px-8"
                  } py-3 md:py-4 shadow-lg transition-all duration-300 transform hover:scale-105 hover:shadow-xl disabled:opacity-50 disabled:transform-none`}
                >
                  {isTyping ? (
                    <div className="w-4 md:w-5 h-4 md:h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  ) : (
                    <span className="flex items-center space-x-2">
                      <span>{isMobile ? "Send" : "Send"}</span>
                      <span>🚀</span>
                    </span>
                  )}
                </Button>

                <Button
                  onClick={toggleListening}
                  variant="outline"
                  className={`${
                    isMobile ? "flex-1 px-6" : "px-6"
                  } py-3 md:py-4 transition-all duration-300 transform hover:scale-105 ${
                    isListening
                      ? "bg-red-500 hover:bg-red-600 text-white border-red-500 shadow-lg shadow-red-500/25 animate-pulse"
                      : "theme-btn-secondary"
                  }`}
                >
                  {isListening ? (
                    <span className="flex items-center space-x-2">
                      <span>🔴</span>
                      <span>Stop</span>
                    </span>
                  ) : (
                    <span className="flex items-center space-x-2">
                      <span>🎤</span>
                      <span>{isMobile ? "Voice" : "Voice"}</span>
                    </span>
                  )}
                </Button>
              </div>
            </div>

            {/* {!isMobile && (
              <div className="mt-6 text-center">
                <p className="text-gray-300 text-sm font-medium bg-white/5 px-4 py-2 rounded-lg border border-white/10 backdrop-blur-sm">
                  💡 <strong>Try:</strong> "Open YouTube", "Search for Python tutorials", "What time is it?", "Show system info"
                </p>
              </div>
            )} */}
          </div>
        </div>
      </div>
    </div>
  );
};

export default BuddyAI;
