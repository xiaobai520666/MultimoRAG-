"use client";

import { useState, useEffect } from "react";
import { sendMessage, listKnowledge } from "@/services";
import { Message, Knowledge } from "@/services/types";

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [kbList, setKbList] = useState<Knowledge[]>([]);
  const [selectedKb, setSelectedKb] = useState<string>("");
  const [error, setError] = useState<string>("");

  useEffect(() => {
    listKnowledge().then(r => {
      setKbList(r.items);
      if (r.items.length > 0) setSelectedKb(r.items[0].id);
    }).catch(() => setError("无法加载知识库列表，请确认后端已启动"));
  }, []);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    if (!selectedKb) {
      setError("请先在「知识库」页面创建一个知识库并上传文件");
      return;
    }

    const userMsg: Message = { role: "user", content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    setError("");

    try {
      const reply = await sendMessage({
        knowledge_id: selectedKb,
        message: input,
        history: messages,
      });
      setMessages(prev => [...prev, { role: "assistant", content: reply.reply }]);
    } catch (err: any) {
      setError(err.message || "请求失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 860, margin: "0 auto", padding: 24 }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <h1 style={{ margin: 0, fontSize: 24 }}>💬 RAG 对话</h1>
        <select
          value={selectedKb}
          onChange={e => setSelectedKb(e.target.value)}
          style={selectStyle}
        >
          <option value="">-- 选择知识库 --</option>
          {kbList.map(k => (
            <option key={k.id} value={k.id}>{k.name} ({k.document_count} 篇文档)</option>
          ))}
        </select>
      </div>

      {/* Error Banner */}
      {error && (
        <div style={errorBannerStyle}>
          ⚠️ {error}
          <button onClick={() => setError("")} style={{ marginLeft: 12, background: "none", border: "none", color: "#fff", cursor: "pointer" }}>✕</button>
        </div>
      )}

      {/* Messages */}
      <div style={chatContainerStyle}>
        {messages.length === 0 && (
          <div style={{ textAlign: "center", color: "#999", padding: 40 }}>
            <p style={{ fontSize: 48, margin: 0 }}>🧠</p>
            <p>选择知识库后开始对话，AI 会基于你的知识库内容回答</p>
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} style={{
            marginBottom: 16, display: "flex", flexDirection: "column",
            alignItems: msg.role === "user" ? "flex-end" : "flex-start",
          }}>
            <div style={{
              maxWidth: "80%", padding: "10px 16px", borderRadius: 12,
              background: msg.role === "user" ? "#1a73e8" : "#fff",
              color: msg.role === "user" ? "#fff" : "#333",
              boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
              whiteSpace: "pre-wrap", wordBreak: "break-word",
              fontSize: 14, lineHeight: 1.6,
            }}>
              {msg.content}
            </div>
            <span style={{ fontSize: 11, color: "#aaa", marginTop: 4 }}>
              {msg.role === "user" ? "你" : "AI"} · {new Date().toLocaleTimeString()}
            </span>
          </div>
        ))}
        {loading && (
          <div style={{ textAlign: "center", padding: 12 }}>
            <span style={{ color: "#1a73e8" }}>🤔 AI 思考中...</span>
          </div>
        )}
      </div>

      {/* Input */}
      <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
        <input
          style={inputStyle}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && handleSend()}
          placeholder={kbList.length === 0 ? "请先创建知识库..." : "输入你的问题，基于知识库回答..."}
          disabled={loading}
        />
        <button onClick={handleSend} disabled={loading || !input.trim()} style={btnStyle}>
          {loading ? "..." : "发送"}
        </button>
      </div>
    </div>
  );
}

const chatContainerStyle: React.CSSProperties = {
  height: 420, overflowY: "auto", border: "1px solid #e0e0e0",
  borderRadius: 12, padding: 16, background: "#fafafa",
};

const inputStyle: React.CSSProperties = {
  flex: 1, padding: "10px 16px", borderRadius: 8,
  border: "1px solid #ddd", fontSize: 14, outline: "none",
};

const btnStyle: React.CSSProperties = {
  padding: "10px 24px", borderRadius: 8, border: "none",
  background: "#1a73e8", color: "#fff", cursor: "pointer",
  fontSize: 14, fontWeight: 600,
};

const selectStyle: React.CSSProperties = {
  padding: "6px 12px", borderRadius: 6, border: "1px solid #ddd",
  fontSize: 13, background: "#fff", maxWidth: 250,
};

const errorBannerStyle: React.CSSProperties = {
  background: "#e74c3c", color: "#fff", padding: "10px 16px",
  borderRadius: 8, marginBottom: 12, fontSize: 13,
  display: "flex", justifyContent: "space-between", alignItems: "center",
};
