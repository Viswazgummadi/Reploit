// File: src/App.jsx
import { useState, useEffect, useRef } from "react";
import ChatWindow from "./components/ChatWindow";

// For development, we start directly in the chat state
const DEV_MODE_CHAT_READY = true;

function App() {
  const [appState, setAppState] = useState(
    DEV_MODE_CHAT_READY ? "chat_ready" : "awaiting_repo"
  );
  const [repoUrl, setRepoUrl] = useState(
    DEV_MODE_CHAT_READY
      ? "https://github.com/Viswazgummadi/p2p_lan_chat.git"
      : ""
  );
  const [error, setError] = useState("");

  const [messages, setMessages] = useState(
    DEV_MODE_CHAT_READY
      ? [{ role: "assistant", content: `Ready to chat about ${repoUrl}!` }]
      : []
  );
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentStatus, setCurrentStatus] = useState("");

  const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

  // --- NEW STREAMING API LOGIC WITH FETCH ---
  const handleSendMessage = async (userInput) => {
    // Add user message to state immediately
    const newMessages = [...messages, { role: "user", content: userInput }];
    setMessages(newMessages);
    setIsStreaming(true);
    setCurrentStatus("Connecting to agent...");

    try {
      const response = await fetch(`${API_URL}/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          // We could add a user's API key here if needed:
          // 'X-User-API-Key': 'USER_API_KEY_HERE',
        },
        body: JSON.stringify({
          question: userInput,
          // Send all previous messages EXCEPT the very first system message
          history: messages.slice(1),
        }),
      });

      if (!response.body) {
        throw new Error("Response body is null.");
      }

      // Manually read and decode the stream
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");

        // Process all complete event lines
        for (let i = 0; i < lines.length - 1; i++) {
          const line = lines[i];
          if (line.startsWith("data: ")) {
            const eventData = JSON.parse(line.substring(6));

            if (eventData.type === "status_update") {
              setCurrentStatus(`Agent is: ${eventData.data.node}`);
            } else if (eventData.type === "final_answer") {
              setMessages((prev) => [
                ...prev,
                { role: "assistant", content: eventData.data.answer },
              ]);
            } else if (eventData.type === "error") {
              setError(`An error occurred: ${eventData.data.message}`);
            }
          }
        }
        // Keep the last, potentially incomplete line in the buffer
        buffer = lines[lines.length - 1];
      }
    } catch (err) {
      console.error("Fetch stream failed:", err);
      setError("Failed to connect to the streaming service.");
    } finally {
      setIsStreaming(false);
      setCurrentStatus("");
    }
  };

  return (
    <div className="bg-gray-900 text-white min-h-screen">
      <div className="container mx-auto max-w-4xl pt-8 px-4">
        <h1 className="text-4xl font-bold text-teal-400 mb-2 text-center">
          AI Codebase Assistant
        </h1>
        {appState === "chat_ready" && (
          <p className="text-center text-gray-400 mb-6 text-sm truncate">
            Analyzing: {repoUrl}
          </p>
        )}

        {/* We are hardcoding the app to always show the chat window for dev */}
        <ChatWindow
          messages={messages}
          onSendMessage={handleSendMessage}
          isStreaming={isStreaming}
        />
        {isStreaming && (
          <p className="text-center text-teal-400 mt-2 text-sm animate-pulse">
            {currentStatus}
          </p>
        )}
        {error && (
          <div className="mt-4 p-4 bg-red-900/50 border border-red-500 text-red-300 rounded-lg text-center">
            <p>
              <strong>Error:</strong> {error}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
