import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "MultimoRAG",
  description: "个人多模态 RAG 问答系统",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body style={{ margin: 0, fontFamily: "system-ui, -apple-system, sans-serif", background: "#f5f5f5" }}>
        <nav style={{
          display: "flex", gap: 24, padding: "12px 24px", background: "#1a1a2e",
          color: "#fff", alignItems: "center", boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
        }}>
          <Link href="/" style={{ fontWeight: 700, fontSize: 18, color: "#e0e0ff", textDecoration: "none" }}>
            🧠 MultimoRAG
          </Link>
          <Link href="/chat" style={navLinkStyle}>💬 对话</Link>
          <Link href="/knowledge" style={navLinkStyle}>📚 知识库</Link>
          <Link href="/settings" style={navLinkStyle}>⚙️ 设置</Link>
        </nav>
        <main style={{ minHeight: "calc(100vh - 52px)" }}>
          {children}
        </main>
      </body>
    </html>
  );
}

const navLinkStyle: React.CSSProperties = {
  color: "#ccc", textDecoration: "none", fontSize: 14,
  padding: "4px 8px", borderRadius: 4, transition: "color 0.2s",
};
