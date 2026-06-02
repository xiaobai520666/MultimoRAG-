"use client";

import { useState, useEffect } from "react";

interface AppSettings {
  apiKey: string;
  apiBaseUrl: string;
  modelName: string;
  temperature: number;
  topK: number;
}

const STORAGE_KEY = "multimorag_settings";

export default function SettingsPage() {
  const [settings, setSettings] = useState<AppSettings>({
    apiKey: "",
    apiBaseUrl: "https://dashscope.aliyuncs.com/api/v1",
    modelName: "qwen-plus",
    temperature: 0.7,
    topK: 5,
  });
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      setSettings(JSON.parse(saved));
    }
  }, []);

  const handleSave = () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const update = (key: keyof AppSettings, value: any) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <div style={{ maxWidth: 600, margin: "0 auto", padding: 20 }}>
      <h1>设置</h1>

      <div style={{ marginBottom: 16 }}>
        <label style={{ display: "block", marginBottom: 4 }}>API 密钥</label>
        <input
          style={{ width: "100%", padding: 8, borderRadius: 4, border: "1px solid #ddd" }}
          type="password"
          value={settings.apiKey}
          onChange={(e) => update("apiKey", e.target.value)}
        />
      </div>

      <div style={{ marginBottom: 16 }}>
        <label style={{ display: "block", marginBottom: 4 }}>API 端点</label>
        <input
          style={{ width: "100%", padding: 8, borderRadius: 4, border: "1px solid #ddd" }}
          value={settings.apiBaseUrl}
          onChange={(e) => update("apiBaseUrl", e.target.value)}
        />
      </div>

      <div style={{ marginBottom: 16 }}>
        <label style={{ display: "block", marginBottom: 4 }}>模型名称</label>
        <input
          style={{ width: "100%", padding: 8, borderRadius: 4, border: "1px solid #ddd" }}
          value={settings.modelName}
          onChange={(e) => update("modelName", e.target.value)}
        />
      </div>

      <div style={{ marginBottom: 16 }}>
        <label style={{ display: "block", marginBottom: 4 }}>Temperature: {settings.temperature}</label>
        <input
          type="range"
          min={0}
          max={1}
          step={0.1}
          value={settings.temperature}
          onChange={(e) => update("temperature", parseFloat(e.target.value))}
        />
      </div>

      <div style={{ marginBottom: 24 }}>
        <label style={{ display: "block", marginBottom: 4 }}>Top K: {settings.topK}</label>
        <input
          type="range"
          min={1}
          max={20}
          value={settings.topK}
          onChange={(e) => update("topK", parseInt(e.target.value))}
        />
      </div>

      <button
        onClick={handleSave}
        style={{ padding: "8px 20px", borderRadius: 4, border: "none", background: "#1a73e8", color: "#fff", cursor: "pointer" }}
      >
        {saved ? "已保存 ✓" : "保存"}
      </button>
    </div>
  );
}
