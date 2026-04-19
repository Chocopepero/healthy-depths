import { useEffect, useRef, useState } from "react";

function SonarLoader() {
  return (
    <div className="flex items-center gap-4 px-4 py-3">
      <div className="relative w-8 h-8 flex items-center justify-center shrink-0">
        <div className="sonar-ring w-4 h-4" />
        <div className="sonar-ring sonar-ring-2 w-4 h-4" />
        <div className="w-2 h-2 rounded-full bg-cyan-bio/80" />
      </div>
      <span className="text-cyan-bio/60 text-sm font-mono animate-pulse">
        Depth is surfacing...
      </span>
    </div>
  );
}

function ChatBubble({ message }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-3`}>
      {!isUser && (
        <div className="w-7 h-7 rounded-full bg-teal-ocean/30 border border-cyan-bio/20 flex items-center justify-center shrink-0 mr-2 mt-0.5">
          <span className="text-xs">⬡</span>
        </div>
      )}
      <div
        className={`max-w-[78%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
          isUser
            ? "bg-teal-ocean/30 border border-cyan-bio/15 text-slate-100 rounded-tr-sm"
            : "bg-navy-800 border border-slate-700/40 text-slate-200 rounded-tl-sm"
        }`}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>
      </div>
    </div>
  );
}

export default function ChatInterface({ history, isLoading, error, onSend }) {
  const [input, setInput] = useState("");
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history, isLoading]);

  useEffect(() => {
    if (!isLoading) inputRef.current?.focus();
  }, [isLoading]);

  function handleSubmit(e) {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;
    onSend(trimmed);
    setInput("");
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      handleSubmit(e);
    }
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto px-4 py-4">
        {history.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center py-12">
            <div className="relative mb-6">
              <div className="w-16 h-16 rounded-full bg-teal-ocean/20 border border-cyan-bio/20 flex items-center justify-center">
                <span className="text-2xl font-display text-cyan-bio">⬡</span>
              </div>
              <div className="absolute inset-0 rounded-full border border-cyan-bio/10 animate-ping" />
            </div>
            <h2 className="font-display text-xl text-slate-200 mb-2">
              Tell me what's going on.
            </h2>
            <p className="text-slate-400 text-sm max-w-xs leading-relaxed">
              Depth will help you understand your symptoms and prepare for care. Start by
              describing how you're feeling.
            </p>
          </div>
        )}

        {history.map((msg, i) => (
          <ChatBubble key={i} message={msg} />
        ))}

        {isLoading && <SonarLoader />}

        {error && (
          <div className="text-red-400/80 text-xs text-center py-2 font-mono">{error}</div>
        )}

        <div ref={bottomRef} />
      </div>

      <div className="border-t border-cyan-bio/10 p-4 bg-navy-950/60 backdrop-blur-sm">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Describe your symptoms..."
            disabled={isLoading}
            rows={1}
            className="depth-input resize-none flex-1"
            style={{ minHeight: "44px", maxHeight: "120px" }}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="depth-btn shrink-0 disabled:opacity-40 disabled:cursor-not-allowed px-5"
          >
            <svg
              className="w-4 h-4"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path d="M22 2L11 13" />
              <path d="M22 2L15 22 11 13 2 9l20-7z" />
            </svg>
          </button>
        </form>
        <p className="text-center text-slate-600 text-xs mt-3 font-mono">
          Not medical advice · Consult a licensed professional
        </p>
      </div>
    </div>
  );
}
