"use client";

import { useState, useEffect } from "react";
import { listKnowledge, createKnowledge, deleteKnowledge, uploadFile } from "@/services";
import { Knowledge } from "@/services/types";

export default function KnowledgePage() {
  const [knowledgeList, setKnowledgeList] = useState<Knowledge[]>([]);
  const [name, setName] = useState("");
  const [desc, setDesc] = useState("");
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    loadKnowledge();
  }, []);

  const loadKnowledge = async () => {
    const result = await listKnowledge();
    setKnowledgeList(result.items);
  };

  const handleCreate = async () => {
    if (!name.trim()) return;
    await createKnowledge(name, desc);
    setName("");
    setDesc("");
    await loadKnowledge();
  };

  const handleDelete = async (id: string) => {
    if (!confirm("确定删除这个知识库？")) return;
    await deleteKnowledge(id);
    await loadKnowledge();
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !knowledgeList.length) return;

    setUploading(true);
    try {
      await uploadFile(file, knowledgeList[0].id);
      alert("上传成功！");
    } catch (err: any) {
      alert(`上传失败: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: 20 }}>
      <h1>知识库管理</h1>

      <div style={{ marginBottom: 24 }}>
        <h3>创建知识库</h3>
        <input
          style={{ padding: 8, marginRight: 8, borderRadius: 4, border: "1px solid #ddd" }}
          placeholder="知识库名称"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <input
          style={{ padding: 8, marginRight: 8, borderRadius: 4, border: "1px solid #ddd" }}
          placeholder="描述（可选）"
          value={desc}
          onChange={(e) => setDesc(e.target.value)}
        />
        <button
          onClick={handleCreate}
          style={{ padding: "8px 16px", borderRadius: 4, border: "none", background: "#1a73e8", color: "#fff", cursor: "pointer" }}
        >
          创建
        </button>
      </div>

      <div style={{ marginBottom: 24 }}>
        <h3>上传文件</h3>
        <input type="file" onChange={handleUpload} disabled={uploading || !knowledgeList.length} />
        {uploading && <span>上传中...</span>}
      </div>

      <div>
        <h3>知识库列表 ({knowledgeList.length})</h3>
        {knowledgeList.map((k) => (
          <div key={k.id} style={{ display: "flex", justifyContent: "space-between", padding: 12, borderBottom: "1px solid #eee" }}>
            <div>
              <strong>{k.name}</strong>
              <span style={{ marginLeft: 12, color: "#999" }}>{k.description}</span>
              <span style={{ marginLeft: 12, color: "#999" }}>{k.document_count} 篇文档</span>
            </div>
            <button
              onClick={() => handleDelete(k.id)}
              style={{ padding: "4px 12px", borderRadius: 4, border: "1px solid #ff4d4f", background: "#fff", color: "#ff4d4f", cursor: "pointer" }}
            >
              删除
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
