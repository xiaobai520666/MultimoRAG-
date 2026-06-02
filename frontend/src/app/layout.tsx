import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "MultimoRAG",
  description: "个人多模态 RAG 问答系统",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body style={{ margin: 0, fontFamily: "system-ui, sans-serif" }}>
        {children}
      </body>
    </html>
  );
}
