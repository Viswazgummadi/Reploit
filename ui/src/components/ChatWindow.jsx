import { useState } from "react";
import ChatMessage from "./ChatMessage";

// The loading spinner for the Send button
const Spinner = () => (
  <svg
    className="animate-spin h-5 w-5 text-white"
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    viewBox="0 0 24 24"
  >
    <circle
      className="opacity-25"
      cx="12"
      cy="12"
      r="10"
      stroke="currentColor"
      strokeWidth="4"
    ></circle>
    <path
      className="opacity-75"
      fill="currentColor"
      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
    ></path>
  </svg>
);

const ChatWindow = ({ messages, onSendMessage, isStreaming }) => {
  const [userInput, setUserInput] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (userInput.trim() && !isStreaming) {
      onSendMessage(userInput);
      setUserInput(""); // Clear input after sending
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-200px)] max-h-[700px] border border-gray-700 rounded-lg bg-gray-800/50 shadow-lg">
      {/* Message List */}
      <div className="flex-1 p-6 space-y-6 overflow-y-auto">
        {messages.map((msg, index) => (
          <ChatMessage key={index} message={msg} />
        ))}
      </div>

      {/* Message Input Form */}
      <div className="p-4 border-t border-gray-700">
        <form onSubmit={handleSubmit} className="flex items-center space-x-4">
          <input
            type="text"
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder={
              isStreaming
                ? "Wait for the AI to respond..."
                : "Ask a question about the codebase..."
            }
            disabled={isStreaming}
            className="flex-grow bg-gray-900 border border-gray-600 rounded-md px-4 py-2 text-white focus:ring-2 focus:ring-teal-400 focus:outline-none transition-colors disabled:cursor-not-allowed"
          />
          <button
            type="submit"
            disabled={isStreaming}
            className="flex items-center justify-center w-24 bg-teal-500 hover:bg-teal-600 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-bold py-2 px-4 rounded-md transition-colors"
          >
            {isStreaming ? <Spinner /> : "Send"}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatWindow;
