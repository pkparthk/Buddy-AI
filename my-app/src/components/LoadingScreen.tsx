import React from "react";

const LoadingScreen: React.FC = () => {
  return (
    <div className="fixed inset-0 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center z-50">
      <div className="text-center">
        <div className="relative mb-8">
          <div className="w-24 h-24 bg-gradient-to-r from-blue-500 via-purple-500 to-cyan-500 rounded-full flex items-center justify-center shadow-2xl animate-pulse">
            <span className="text-4xl">🤖</span>
          </div>
          <div className="absolute inset-0 bg-gradient-to-r from-blue-500 via-purple-500 to-cyan-500 rounded-full opacity-20 animate-ping"></div>
        </div>

        <h2 className="text-3xl font-bold text-white mb-4 bg-gradient-to-r from-blue-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
          Buddy AI
        </h2>

        <div className="flex items-center justify-center space-x-2 mb-4">
          <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
          <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce delay-100"></div>
          <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce delay-200"></div>
        </div>

        <p className="text-gray-300 text-lg">
          Initializing your intelligent assistant...
        </p>
      </div>
    </div>
  );
};

export default LoadingScreen;
