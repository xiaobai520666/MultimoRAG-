"use client";

import { useState } from "react";
import { sendMessage } from "@/services";
import { Message } from "@/services/types";

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMsg: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const reply = await sendMessage({
        knowledge_id: "default",
        message: input,
        history: messages,
      });
      setMessages((prev) => [...prev, { role: "assistant", content: reply.reply }]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `错误: ${err.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: 20 }}>
      <h1>MultimoRAG 对话</h1>

      <div style={{ height: 60, overflowY: "auto", border: "1px solid #ddd", borderRadius: 8, padding: 12, marginBottom: 12 }}>
        {messages.map((msg, i) => (
          <div key={i} style={{ marginBottom: 8 }}>
            <strong>{msg.role === "user" ? "👤 你" : "🤖 AI"}：</strong>
            <span>{msg.content}</span>
          </div>
        ))}
        {loading && <div style={{ color: "#999" }}>思考中...</div>}
      </div>

      <div style={{ display: "flex", gap: 8 }}>
        <input
          style={{ flex: 1, padding: "8px 12px", borderRadius: 8, border: "1px solid #ddd" }}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="输入你的问题..."
        />
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          style={{ padding: "8px 20px", borderRadius: 8, border: "none", background: "#1a73e8", color: "#fff", cursor: "pointer" }}
        >
          发送
        </button>
      </div>
    </div>
  );
}
