/*import React, { useState, useEffect, useRef } from "react";
function ChatUI() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const chatBodyRef = useRef(null);

  // Auto‑scroll to bottom when messages change
  useEffect(() => {
    if (chatBodyRef.current) {
      chatBodyRef.current.scrollTop = chatBodyRef.current.scrollHeight;
    }
  }, [messages, loading]);

  const handleSend = async () => {
    if (!input && !file) return;

    const userMessage = {
      id: Date.now(),
      text: input || (file ? `Sent a file: ${file.name}` : ""),
      fileName: file ? file.name : null,
      sender: "user",
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    const formData = new FormData();
    if (input) formData.append("message", input);
    if (file) formData.append("file", file);

    setLoading(true);

    try {
      const res = await fetch("http://localhost:5000/api/chat", {
        method: "POST",
        body: formData,
      });

      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        throw new Error(data.reply || `HTTP error! status: ${res.status}`);
      }

      const botMessage = {
        id: Date.now() + 1,
        text: data.reply || "No reply received from server.",
        sender: "bot",
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Error calling API:", error);
      const errorMessage = {
        id: Date.now() + 2,
        text: `⚠️ ${error.message}`,
        sender: "bot",
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
      setFile(null);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (!selected) return;
    setFile(selected);
  };

  return (
    <div className="app-shell">
      <div className="chat-panel">
        <header className="chat-header">
          <div className="chat-avatar">
            <span>AI</span>
          </div>
          <div>
            <div className="chat-title">RAG Chatbot</div>
            <div className="chat-subtitle">
              Connected • Ask anything, upload PDFs or images
            </div>
          </div>
        </header>

        <div className="chat-body" ref={chatBodyRef}>
          {messages.length === 0 && !loading && (
            <div className="chat-empty">
              <h3>Welcome 👋</h3>
              <p>
                Start by asking a question or upload a PDF / image for the
                assistant to analyze.
              </p>
              <ul>
                <li>“Summarize this document for me”</li>
                <li>“Explain this like I’m 10 years old”</li>
                <li>“Extract key points from this PDF”</li>
              </ul>
            </div>
          )}

          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`message-row ${
                msg.sender === "user" ? "message-row-user" : "message-row-bot"
              }`}
            >
              {msg.sender === "bot" && (
                <div className="bubble-avatar bubble-avatar-bot">AI</div>
              )}
              <div
                className={`message-bubble ${
                  msg.sender === "user"
                    ? "message-bubble-user"
                    : "message-bubble-bot"
                }`}
              >
                <div className="message-text">{msg.text}</div>
                {msg.fileName && (
                  <div className="message-file-pill">
                    📎 {msg.fileName}
                  </div>
                )}
                <div className="message-meta">
                  {msg.sender === "user" ? "You" : "Assistant"} ·{" "}
                  {msg.timestamp}
                </div>
              </div>
              {msg.sender === "user" && (
                <div className="bubble-avatar bubble-avatar-user">You</div>
              )}
            </div>
          ))}

          {loading && (
            <div className="message-row message-row-bot">
              <div className="bubble-avatar bubble-avatar-bot">AI</div>
              <div className="message-bubble message-bubble-bot">
                <div className="typing-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <div className="message-meta">Assistant · thinking…</div>
              </div>
            </div>
          )}
        </div>

        <footer className="chat-input-bar">
          {file && (
            <div className="file-chip">
              <span className="file-chip-name">📎 {file.name}</span>
              <button
                className="file-chip-remove"
                onClick={() => setFile(null)}
              >
                ✕
              </button>
            </div>
          )}

          <div className="chat-input-row">
            <label className="icon-button file-button">
              📄
              <input
                type="file"
                onChange={handleFileChange}
                className="file-input-hidden"
              />
            </label>

            <textarea
              className="chat-textarea"
              placeholder="Ask something… press Enter to send, Shift+Enter for new line"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
            />

            <button
              className="send-button"
              onClick={handleSend}
              disabled={loading || (!input && !file)}
            >
              {loading ? "Sending…" : "Send"}
            </button>
          </div>
        </footer>
      </div>
    </div>
  );
}

export default ChatUI; */

import React, { useState, useEffect, useRef } from "react";
import "./styles.css";

const ChatUI = () => {
  // Chat history (persisted)
  const [messages, setMessages] = useState(() => {
    const saved = localStorage.getItem("chatHistory");
    return saved ? JSON.parse(saved) : [];
  });

  const [input, setInput] = useState("");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  // Theme: dark / light
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem("chatTheme") || "dark";
  });

  const chatBodyRef = useRef(null);
  const fileInputRef = useRef(null);

  // Auto‑scroll
  useEffect(() => {
    if (chatBodyRef.current) {
      chatBodyRef.current.scrollTop = chatBodyRef.current.scrollHeight;
    }
  }, [messages, loading]);

  // Persist chat + theme
  useEffect(() => {
    localStorage.setItem("chatHistory", JSON.stringify(messages));
  }, [messages]);

  useEffect(() => {
    localStorage.setItem("chatTheme", theme);
  }, [theme]);

  const handleSend = async () => {
    if (!input.trim() && !file) return;

    const timestamp = new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });

    const userMessage = {
      id: Date.now(),
      role: "user",
      text: input || (file ? `Sent a file: ${file.name}` : ""),
      fileName: file ? file.name : null,
      timestamp,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    const formData = new FormData();
    if (userMessage.text) formData.append("message", userMessage.text);
    if (file) formData.append("file", file);

    setLoading(true);

    try {
      const res = await fetch("http://localhost:5000/api/chat", {
        method: "POST",
        body: formData,
      });

      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data.reply || `HTTP error! status: ${res.status}`);
      }

      const botMessage = {
        id: Date.now() + 1,
        role: "bot",
        text: data.reply || "No reply received from server.",
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      console.error("Error calling API:", err);
      const errorMessage = {
        id: Date.now() + 2,
        role: "bot",
        text: `⚠️ ${err.message}`,
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
      setFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (!selected) return;
    setFile(selected);
  };

  const clearHistory = () => {
    setMessages([]);
    localStorage.removeItem("chatHistory");
  };

  const toggleTheme = () => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  };

  const isDark = theme === "dark";

  return (
    <div className={`app-shell ${isDark ? "dark-theme" : "light-theme"}`}>
      <div className="chat-panel">
        <header className="chat-header">
          <div className="chat-header-left">
            <div className="chat-avatar">
              <span>AI</span>
            </div>
            <div>
              <div className="chat-title">Gemini Assistant</div>
              <div className="chat-subtitle">
                {isDark ? "Dark mode · Gradient" : "Light mode · Clean"}
              </div>
            </div>
          </div>

          <div className="chat-header-right">
            <button className="icon-button theme-toggle" onClick={toggleTheme}>
              {isDark ? "🌞" : "🌙"}
            </button>
            <button className="clear-btn" onClick={clearHistory}>
              🗑 Clear
            </button>
          </div>
        </header>

        <div className="chat-body" ref={chatBodyRef}>
          {messages.length === 0 && !loading && (
            <div className="chat-empty">
              <h3>Welcome 👋</h3>
              <p>Ask something, or upload a PDF / image for analysis.</p>
              <ul>
                <li>“Summarize this document”</li>
                <li>“Explain this like I’m 10”</li>
                <li>“Extract key points from this file”</li>
              </ul>
            </div>
          )}

          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`message-row ${
                msg.role === "user" ? "message-row-user" : "message-row-bot"
              }`}
            >
              {msg.role === "bot" && (
                <div className="bubble-avatar bubble-avatar-bot">AI</div>
              )}

              <div
                className={`message-bubble ${
                  msg.role === "user"
                    ? "message-bubble-user"
                    : "message-bubble-bot"
                }`}
              >
                <div className="message-text">{msg.text}</div>
                {msg.fileName && (
                  <div className="message-file-pill">📎 {msg.fileName}</div>
                )}
                <div className="message-meta">
                  {msg.role === "user" ? "You" : "Assistant"} · {msg.timestamp}
                </div>
              </div>

              {msg.role === "user" && (
                <div className="bubble-avatar bubble-avatar-user">You</div>
              )}
            </div>
          ))}

          {loading && (
            <div className="message-row message-row-bot">
              <div className="bubble-avatar bubble-avatar-bot">AI</div>
              <div className="message-bubble message-bubble-bot">
                <div className="typing-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <div className="message-meta">Assistant · thinking…</div>
              </div>
            </div>
          )}
        </div>

        <footer className="chat-input-bar">
          {file && (
            <div className="file-chip">
              <span className="file-chip-name">📎 {file.name}</span>
              <button
                className="file-chip-remove"
                onClick={() => {
                  setFile(null);
                  if (fileInputRef.current) fileInputRef.current.value = "";
                }}
              >
                ✕
              </button>
            </div>
          )}

          <div className="chat-input-row">
            {/* Custom file button — hides "No file chosen" */}
            <label className="icon-button file-button">
              📄
              <input
                ref={fileInputRef}
                type="file"
                onChange={handleFileChange}
                className="file-input-hidden"
              />
            </label>

            <textarea
              className="chat-textarea"
              placeholder="Ask something… Enter to send, Shift+Enter for new line"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
            />

            {/* Clear visible SEND button */}
            <button
              className="send-button"
              onClick={handleSend}
              disabled={loading || (!input.trim() && !file)}
            >
              {loading ? "Sending…" : "Send"}
            </button>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default ChatUI;


