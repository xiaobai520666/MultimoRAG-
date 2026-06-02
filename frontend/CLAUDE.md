# 前端模块 — frontend

## 模块功能

Next.js 前端应用，提供 RAG 系统的浏览器交互界面。包含对话、知识库管理、设置三大页面。

## 需求边界

**属于本模块：**
- 对话聊天界面（消息输入、流式响应展示、引用溯源）
- 知识库管理界面（增删改查）
- 文件上传界面（拖拽/选择文件）
- 系统设置页面（API 配置等）
- 后端 API 的 HTTP 客户端封装

**不属于本模块：**
- 身份认证与权限管理（第一版个人使用）
- 实时通知
- 离线功能

## 接口定义

前端通过 `src/services/` 目录下封装的 API 客户端与后端通信：

```typescript
// services/api.ts — 基础 HTTP 封装
class ApiClient {
  async get<T>(path: string): Promise<T>
  async post<T>(path: string, body: any): Promise<T>
  async upload<T>(path: string, file: File, extra: Record<string, string>): Promise<T>
}

// services/chat.ts
async function sendMessage(knowledgeId: string, message: string, history: Message[]): Promise<ChatResult>

// services/knowledge.ts
async function listKnowledge(page: number, size: number): Promise<PageResult<Knowledge>>
async function createKnowledge(name: string, desc: string): Promise<Knowledge>
async function deleteKnowledge(id: string): Promise<void>

// services/ingestion.ts
async function uploadFile(file: File, knowledgeId: string): Promise<IngestTask>
async function getIngestStatus(taskId: string): Promise<IngestStatus>
```

## 依赖与约束

- Node.js 20+
- Next.js 14+ (App Router)
- CSS 方案：Tailwind CSS
- HTTP 客户端：fetch（或 axios）
- 所有 API 调用通过 `services/` 封装，页面组件不直接使用 fetch