"use client";

import { useState, useEffect } from "react";

interface AppSettings {
  apiBaseUrl: string;
  modelName: string;
  temperature: number;
  topK: number;
}

const defaults: AppSettings = {
  apiBaseUrl: "http://localhost:8000/api/v1",
  modelName: "deepseek-chat",
  temperature: 0.7,
  topK: 5,
};

export default function SettingsPage() {
  const [settings, setSettings] = useState<AppSettings>(defaults);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem("multimorag_settings");
    if (stored) {
      try { setSettings({ ...defaults, ...JSON.parse(stored) }); } catch { /* use defaults */ }
    }
  }, []);

  const handleSave = () => {
    localStorage.setItem("multimorag_settings", JSON.stringify(settings));
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const update = (key: keyof AppSettings, value: string | number) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  return (
    <div style={{ maxWidth: 600, margin: "0 auto", padding: 24 }}>
      <h1 style={{ fontSize: 24, marginBottom: 20 }}>⚙️ 系统设置</h1>

      <div style={{ background: "#fff", borderRadius: 10, padding: 24, boxShadow: "0 1px 4px rgba(0,0,0,0.06)" }}>
        <div style={fieldStyle}>
          <label style={labelStyle}>API 地址</label>
          <input style={inputStyle} value={settings.apiBaseUrl} onChange={e => update("apiBaseUrl", e.target.value)} />
          <span style={hintStyle}>后端 API 的基础 URL，开发环境默认为 localhost:8000</span>
        </div>

        <div style={fieldStyle}>
          <label style={labelStyle}>LLM 模型</label>
          <select style={inputStyle} value={settings.modelName} onChange={e => update("modelName", e.target.value)}>
            <option value="deepseek-chat">DeepSeek Chat</option>
            <option value="qwen-plus">Qwen Plus</option>
            <option value="qwen-max">Qwen Max</option>
          </select>
        </div>

        <div style={fieldStyle}>
          <label style={labelStyle}>Temperature: {settings.temperature}</label>
          <input type="range" min="0" max="2" step="0.1" value={settings.temperature}
            onChange={e => update("temperature", parseFloat(e.target.value))} style={{ width: "100%" }} />
          <span style={hintStyle}>越高回复越随机，越低越确定</span>
        </div>

        <div style={fieldStyle}>
          <label style={labelStyle}>检索数量 (Top-K): {settings.topK}</label>
          <input type="range" min="1" max="20" step="1" value={settings.topK}
            onChange={e => update("topK", parseInt(e.target.value))} style={{ width: "100%" }} />
          <span style={hintStyle}>每次从知识库检索的文档片段数量</span>
        </div>

        <button onClick={handleSave} style={{
          marginTop: 16, padding: "10px 32px", borderRadius: 8, border: "none",
          background: saved ? "#27ae60" : "#1a73e8", color: "#fff",
          cursor: "pointer", fontSize: 14, fontWeight: 600,
        }}>
          {saved ? "✓ 已保存" : "保存设置"}
        </button>
      </div>

      <div style={{ marginTop: 24, padding: 16, background: "#fffbe6", borderRadius: 8, fontSize: 13, color: "#666" }}>
        <strong>💡 提示：</strong>当前版本为个人使用设计，设置保存在浏览器本地。
        API Key 请在后端 <code>.env</code> 文件中配置。
      </div>
    </div>
  );
}

const fieldStyle: React.CSSProperties = { marginBottom: 20 };
const labelStyle: React.CSSProperties = { display: "block", fontWeight: 600, marginBottom: 6, fontSize: 14 };
const inputStyle: React.CSSProperties = { width: "100%", padding: "8px 12px", borderRadius: 6, border: "1px solid #ddd", fontSize: 14, outline: "none", boxSizing: "border-box" };
const hintStyle: React.CSSProperties = { display: "block", color: "#999", fontSize: 12, marginTop: 4 };
