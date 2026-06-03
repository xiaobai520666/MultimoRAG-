"use client";

import { useState, useEffect } from "react";
import { listKnowledge, createKnowledge, deleteKnowledge, uploadFile } from "@/services";
import { Knowledge } from "@/services/types";

export default function KnowledgePage() {
  const [kbList, setKbList] = useState<Knowledge[]>([]);
  const [name, setName] = useState("");
  const [desc, setDesc] = useState("");
  const [error, setError] = useState("");
  const [uploading, setUploading] = useState<string>(""); // kb id being uploaded to
  const [loading, setLoading] = useState(true);

  const load = async () => {
    try {
      const r = await listKnowledge();
      setKbList(r.items);
      setError("");
    } catch (e: any) {
      setError("无法连接后端，请确认 localhost:8000 已启动");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const handleCreate = async () => {
    if (!name.trim()) return;
    try {
      await createKnowledge(name, desc);
      setName(""); setDesc("");
      await load();
    } catch (e: any) {
      setError(e.message);
    }
  };

  const handleDelete = async (id: string, kbName: string) => {
    if (!confirm(`确定删除「${kbName}」？所有文档将被清除。`)) return;
    try {
      await deleteKnowledge(id);
      await load();
    } catch (e: any) {
      setError(e.message);
    }
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>, kbId: string) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(kbId);
    try {
      await uploadFile(file, kbId);
      await load();
    } catch (err: any) {
      setError(`上传失败: ${err.message}`);
    } finally {
      setUploading("");
    }
  };

  if (loading) return <div style={{ textAlign: "center", padding: 40, color: "#999" }}>加载中...</div>;

  return (
    <div style={{ maxWidth: 860, margin: "0 auto", padding: 24 }}>
      <h1 style={{ fontSize: 24, marginBottom: 20 }}>📚 知识库管理</h1>

      {error && (
        <div style={{ background: "#e74c3c", color: "#fff", padding: "10px 16px", borderRadius: 8, marginBottom: 16, fontSize: 13 }}>
          {error}
          <button onClick={() => setError("")} style={{ marginLeft: 12, background: "none", border: "none", color: "#fff", cursor: "pointer" }}>✕</button>
        </div>
      )}

      {/* Create Form */}
      <div style={{ ...cardStyle, marginBottom: 24 }}>
        <h3 style={{ margin: "0 0 12px 0", fontSize: 16 }}>创建新知识库</h3>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <input
            style={inputStyle}
            placeholder="知识库名称 *"
            value={name}
            onChange={e => setName(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleCreate()}
          />
          <input
            style={{ ...inputStyle, flex: 2 }}
            placeholder="描述（可选）"
            value={desc}
            onChange={e => setDesc(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleCreate()}
          />
          <button onClick={handleCreate} disabled={!name.trim()} style={btnPrimary}>
            ➕ 创建
          </button>
        </div>
      </div>

      {/* KB List */}
      {kbList.length === 0 ? (
        <div style={{ textAlign: "center", padding: 40, color: "#999" }}>
          <p style={{ fontSize: 48, margin: 0 }}>📭</p>
          <p>还没有知识库，创建一个开始吧</p>
        </div>
      ) : (
        kbList.map(kb => (
          <div key={kb.id} style={{ ...cardStyle, marginBottom: 16 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <div style={{ flex: 1 }}>
                <strong style={{ fontSize: 16 }}>{kb.name}</strong>
                <span style={{ marginLeft: 12, color: "#999", fontSize: 13 }}>
                  {kb.document_count} 篇文档 · {new Date(kb.created_at).toLocaleDateString("zh-CN")}
                </span>
                {kb.description && <p style={{ color: "#666", fontSize: 13, margin: "4px 0 0 0" }}>{kb.description}</p>}
              </div>
              <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                <label style={{
                  padding: "6px 14px", borderRadius: 6, border: "1px solid #1a73e8",
                  color: "#1a73e8", cursor: "pointer", fontSize: 13,
                }}>
                  {uploading === kb.id ? "上传中..." : "📎 上传"}
                  <input type="file" onChange={e => handleUpload(e, kb.id)} style={{ display: "none" }}
                    accept=".txt,.md,.markdown,.pdf,.png,.jpg,.jpeg,.mp3,.wav"
                  />
                </label>
                <button onClick={() => handleDelete(kb.id, kb.name)} style={btnDanger}>
                  🗑 删除
                </button>
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  );
}

const cardStyle: React.CSSProperties = {
  background: "#fff", borderRadius: 10, padding: "16px 20px",
  boxShadow: "0 1px 4px rgba(0,0,0,0.06)", border: "1px solid #eee",
};

const inputStyle: React.CSSProperties = {
  flex: 1, minWidth: 160, padding: "8px 12px", borderRadius: 6,
  border: "1px solid #ddd", fontSize: 14, outline: "none",
};

const btnPrimary: React.CSSProperties = {
  padding: "8px 18px", borderRadius: 6, border: "none",
  background: "#1a73e8", color: "#fff", cursor: "pointer", fontSize: 13, fontWeight: 600,
};

const btnDanger: React.CSSProperties = {
  padding: "6px 14px", borderRadius: 6, border: "1px solid #ff4d4f",
  background: "#fff", color: "#ff4d4f", cursor: "pointer", fontSize: 13,
};
