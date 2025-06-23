// --- THIS IS THE CORRECTED VITE IMPORT SYNTAX ---
import UserIcon from "../assets/user-icon.svg";
import AssistantIcon from "../assets/assistant-icon.svg";

const ChatMessage = ({ message }) => {
  const { role, content } = message;
  const isUser = role === "user";

  return (
    <div className={`flex items-start gap-4 ${isUser ? "justify-end" : ""}`}>
      {/* Conditionally render the assistant icon on the left */}
      {!isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-teal-500 flex items-center justify-center">
          {/* --- RENDER AS AN IMG TAG --- */}
          <img src={AssistantIcon} alt="Assistant Icon" className="w-5 h-5" />
        </div>
      )}

      {/* Main message bubble */}
      <div
        className={`max-w-xl p-4 rounded-lg shadow-md ${
          isUser
            ? "bg-teal-600 text-white rounded-br-none"
            : "bg-gray-700 text-gray-200 rounded-bl-none"
        }`}
      >
        <p className="whitespace-pre-wrap">{content}</p>
      </div>

      {/* Conditionally render the user icon on the right */}
      {isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center">
          {/* --- RENDER AS AN IMG TAG --- */}
          <img src={UserIcon} alt="User Icon" className="w-5 h-5" />
        </div>
      )}
    </div>
  );
};

export default ChatMessage;
