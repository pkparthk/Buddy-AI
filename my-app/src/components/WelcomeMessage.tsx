import React from "react";

interface WelcomeMessageProps {
  onGetStarted: () => void;
}

const WelcomeMessage: React.FC<WelcomeMessageProps> = ({ onGetStarted }) => {
  const features = [
    {
      icon: "🌐",
      title: "Web Navigation",
      description: "Open your favorite websites instantly",
    },
    {
      icon: "🔍",
      title: "Smart Search",
      description: "Search the web with intelligent queries",
    },
    {
      icon: "💻",
      title: "System Control",
      description: "Check system info and control your PC",
    },
    {
      icon: "🎤",
      title: "Voice Commands",
      description: "Talk to me naturally with voice recognition",
    },
    {
      icon: "⚡",
      title: "Quick Actions",
      description: "Access frequently used commands quickly",
    },
    {
      icon: "🧠",
      title: "AI Intelligence",
      description: "Get smart responses and helpful assistance",
    },
  ];

  return (
    <div className="max-w-4xl mx-auto p-3 md:p-6 text-center">
      <div className="mb-6 md:mb-8">
        <div className="w-16 h-16 md:w-24 md:h-24 bg-gradient-to-r from-blue-500 via-purple-500 to-cyan-500 rounded-full flex items-center justify-center shadow-2xl mx-auto mb-4 md:mb-6 animate-pulse">
          <span className="text-2xl md:text-4xl">🤖</span>
        </div>

        <h1 className="text-2xl md:text-4xl lg:text-5xl font-bold text-white mb-3 md:mb-4 bg-gradient-to-r from-blue-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
          Welcome to Buddy AI
        </h1>

        <p className="text-sm md:text-xl text-gray-300 mb-6 md:mb-8 max-w-2xl mx-auto px-4 md:px-0">
          Your intelligent assistant ready to help with web navigation, system
          control, smart searches, and much more. Let's get started!
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6 mb-6 md:mb-8">
        {features.map((feature, index) => (
          <div
            key={index}
            className="bg-black/30 backdrop-blur-sm border border-white/10 rounded-xl p-4 md:p-6 hover:bg-black/40 transition-all duration-300 transform hover:-translate-y-2 hover:shadow-xl"
          >
            <div className="text-2xl md:text-4xl mb-3 md:mb-4">
              {feature.icon}
            </div>
            <h3 className="text-white font-semibold text-base md:text-lg mb-2">
              {feature.title}
            </h3>
            <p className="text-gray-400 text-xs md:text-sm">
              {feature.description}
            </p>
          </div>
        ))}
      </div>

      <div className="space-y-3 md:space-y-4">
        <button
          onClick={onGetStarted}
          className="bg-gradient-to-r from-blue-600 via-purple-600 to-blue-700 hover:from-blue-700 hover:via-purple-700 hover:to-blue-800 text-white font-semibold px-6 md:px-8 py-3 md:py-4 rounded-xl shadow-lg transition-all duration-300 transform hover:scale-105 hover:shadow-xl w-full md:w-auto"
        >
          <span className="flex items-center justify-center space-x-2">
            <span>Get Started</span>
            <span>🚀</span>
          </span>
        </button>

        <p className="text-gray-400 text-xs md:text-sm px-4 md:px-0">
          💡 <strong>Quick tip:</strong> Try saying "Open YouTube" or "What time
          is it?" to see me in action!
        </p>
      </div>
    </div>
  );
};

export default WelcomeMessage;
