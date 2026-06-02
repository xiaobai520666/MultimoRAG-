# MultimoRAG — 个人多模态 RAG 问答系统

## 项目概述

MultimoRAG 是一个面向个人的多模态知识问答系统。你可以把文本文件、图片、音频导入知识库，然后像聊天一样提问，系统会从知识库中检索相关内容并生成答案。内置轻量 Agent 能力，支持简单的工具调用。

**核心理念：** 隐私优先、API 驱动、模块化可扩展。

## 功能需求

### 第一期（当前版本）

| 功能 | 说明 |
|------|------|
| 文本知识管理 | 上传 PDF、Markdown、TXT，自动解析入库 |
| 图片知识管理 | 上传图片（JPG/PNG），OCR 提取文字后入库 |
| 音频知识管理 | 上传音频（MP3/WAV），转写文字后入库 |
| 多模态 RAG 问答 | 基于知识库的智能问答，含引用溯源 |
| 轻量 Agent | 支持查询改写、知识检索、知识摘要等 3-5 个安全工具 |
| Web 对话界面 | 浏览器端对话交互 |
| Docker 部署 | docker-compose 一键启动 |

### 第一期不做的

- 多用户/多租户
- 复杂权限系统
- 在线网页抓取
- 工作流编排
- 本地模型推理
- 实时语音对话

## 系统架构

```
┌─────────────────────────────────────────────────┐
│                   前端 (Next.js)                  │
│          Chat / Knowledge / Settings             │
└──────────────────────┬──────────────────────────┘
                       │ HTTP / JSON
┌──────────────────────▼──────────────────────────┐
│                 API 路由层 (FastAPI)               │
│    /api/v1/chat /knowledge /ingestion /agent     │
└───────┬──────────┬──────────┬───────────────────┘
        │          │          │
┌───────▼──┐ ┌─────▼──────┐ ┌▼──────────────────┐
│ ingestion│ │ retrieval  │ │     agent          │
│ 流水线   │ │ 多路检索   │ │    执行器          │
│ 解析/分块 │ │ 重排序    │ │    工具集          │
│ 嵌入     │ │            │ │                    │
└───────┬──┘ └─────┬──────┘ └─────┬──────────────┘
        │          │              │
┌───────▼──────────▼──────────────▼──────────────┐
│              Providers 模型适配层                │
│   LLM  │  Embedding  │  OCR  │  Audio transcribe │
│   (千问 API / 可切换)                             │
└─────────────────────┬───────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────┐
│                 Storage 存储层                    │
│   Qdrant (向量) │ PostgreSQL (元数据/对话) │ 文件  │
└─────────────────────────────────────────────────┘
```

### 数据流

```
上传文件 → 解析(文本/OCR/转写) → 分块 → 嵌入 → 存入 Qdrant
                                                      ↓
用户提问 → 检索 Top-K → 组装上下文 → 调用 LLM → 返回(答案+引用)
                                                      ↓
Agent 请求 → 分析意图 → 调用工具 → 整合结果 → 返回
```

## 仓库目录结构

```
multimorag/
├── CLAUDE.md                  # 仓库级操作指南
├── README.md                  # 本文件
├── docker-compose.yml         # Docker 服务编排
├── .env.example               # 环境变量模板
├── .gitignore
│
├── backend/                   # FastAPI 后端
│   ├── CLAUDE.md              # 后端模块总述
│   └── app/
│       ├── main.py            # 应用入口
│       ├── api/               # API 路由层
│       │   ├── CLAUDE.md      # 路由规范与接口清单
│       │   ├── router_v1.py   # 路由注册
│       │   ├── chat.py        # 对话接口
│       │   ├── knowledge.py   # 知识库 CRUD
│       │   ├── ingestion.py   # 文件上传与入库
│       │   ├── retrieval.py   # 检索调试接口
│       │   ├── agent.py       # Agent 执行接口
│       │   └── health.py      # 健康检查
│       ├── services/
│       │   ├── CLAUDE.md      # 服务层说明
│       │   ├── ingestion/     # 入库流水线
│       │   │   ├── CLAUDE.md  # 解析/分块/嵌入
│       │   │   ├── parser.py
│       │   │   ├── chunker.py
│       │   │   ├── embedder.py
│       │   │   └── pipeline.py
│       │   ├── retrieval/     # 检索排序
│       │   │   ├── CLAUDE.md
│       │   │   ├── retriever.py
│       │   │   └── reranker.py
│       │   ├── chat/          # 对话编排
│       │   │   ├── CLAUDE.md
│       │   │   ├── orchestrator.py
│       │   │   └── context.py
│       │   └── agent/         # Agent 工具
│       │       ├── CLAUDE.md
│       │       ├── executor.py
│       │       └── tools.py
│       ├── providers/         # 模型适配层
│       │   ├── CLAUDE.md
│       │   ├── base.py
│       │   ├── llm.py
│       │   ├── embedding.py
│       │   ├── ocr.py
│       │   └── audio.py
│       ├── storage/           # 存储层
│       │   ├── CLAUDE.md
│       │   ├── vector_store.py
│       │   ├── metadata_db.py
│       │   ├── file_store.py
│       │   └── schemas.py
│       └── core/              # 基础设施
│           ├── CLAUDE.md
│           ├── config.py
│           ├── models.py
│           └── exceptions.py
│
├── frontend/                  # Next.js 前端
│   ├── CLAUDE.md              # 前端总述
│   └── src/
│       ├── app/
│       │   ├── page.tsx
│       │   ├── chat/          # 对话页面
│       │   │   ├── CLAUDE.md
│       │   │   ├── page.tsx
│       │   │   └── components/
│       │   ├── knowledge/     # 知识库管理
│       │   │   ├── CLAUDE.md
│       │   │   ├── page.tsx
│       │   │   └── components/
│       │   └── settings/      # 设置页面
│       │       ├── CLAUDE.md
│       │       └── page.tsx
│       ├── components/        # 共享组件
│       ├── services/          # API 客户端
│       └── hooks/             # 自定义 hooks
│
└── docs/                      # 补充设计文档
```

## 快速开始

### 前置条件

- Python 3.11+
- Node.js 20+
- Docker & docker-compose（部署用）

### 本地开发

```bash
# 1. 克隆项目
git clone <repo-url> && cd multimorag

# 2. 环境变量
cp .env.example .env

# 3. 启动后端
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 4. 启动前端（另开终端）
cd frontend
npm install
npm run dev
```

### Docker 部署

```bash
docker compose up --build
```

访问 http://localhost:3000

## API 概览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/health` | 健康检查 |
| POST | `/api/v1/chat` | 发送对话消息 |
| GET | `/api/v1/knowledge` | 获取知识库列表 |
| POST | `/api/v1/knowledge` | 创建知识库 |
| DELETE | `/api/v1/knowledge/{id}` | 删除知识库 |
| POST | `/api/v1/ingestion/upload` | 上传文件 |
| GET | `/api/v1/ingestion/{id}/status` | 查询入库状态 |
| POST | `/api/v1/retrieval/search` | 检索调试 |
| POST | `/api/v1/agent/execute` | 执行 Agent 调用 |

## 配置说明

通过 `.env` 文件配置：

```bash
# API 密钥（千问）
QWEN_API_KEY=sk-xxxxx
QWEN_API_BASE=https://dashscope.aliyuncs.com/api/v1

# 数据库
POSTGRES_DSN=postgresql://user:pass@localhost:5432/multimorag

# Qdrant 向量库配置
QDRANT_HOST=qdrant
QDRANT_PORT=6333
QDRANT_API_KEY=

# 文件存储路径
UPLOAD_DIR=./data/uploads

# 服务端口
BACKEND_PORT=8000
FRONTEND_PORT=3000
```

## 技术选型说明

### 向量库：Qdrant

| 对比项 | Qdrant | Chroma | Milvus Lite |
|--------|--------|--------|-------------|
| 内存占用 | ~80MB | ~50MB | ~150MB |
| 2c2g 适配 | ✅ | ⚠️ 容器化有锁问题 | ✅ |
| 多模态过滤检索 | ✅ payload filter 成熟 | ⚠️ 基础过滤 | ✅ |
| 生产成熟度 | ✅ 生产级 | ⚠️ 适合原型 | ✅ 分布式强 |
| 2c2g 推荐度 | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |

**选择 Qdrant 的理由：** 2c2g 服务器内存敏感；Docker 部署一行启动；LangChain/LlamaIndex 原生支持；payload 过滤对多模态场景最实用。

### 分块策略

| 模态 | 策略 | 理由 |
|------|------|------|
| 文本 | 500 token 递归切分，50 token 重叠 | 平衡召回率和精度 |
| 图片 | 整张图片一块（OCR 全文） | 避免上下文断裂 |
| 音频 | 按 30-60 秒段落切分 | 语义完整 |

### Agent 工具集（第一版 3-5 个）

| 工具 | 功能 | 说明 |
|------|------|------|
| QueryRewriteTool | 查询改写 | 用户问题 → 更适合检索的形式 |
| KnowledgeSearchTool | 知识库搜索 | 调用 retrieval 模块 |
| KnowledgeSummaryTool | 知识摘要 | 生成文档/知识库摘要 |
| ContextClarifyTool | 上下文澄清 | 不确定时反问用户 |

### 检索效果评估

| 指标 | 说明 | 面试能写 |
|------|------|----------|
| Hit Rate @ K | 正确答案在前 K 条结果中的比例 | "Top-5 Hit Rate 达 XX%" |
| MRR | Mean Reciprocal Rank，首条正确答案的排名倒数 | "MRR 达 0.XX" |
| 响应时间 | API 端到端延迟 | "P95 延迟 < Xs" |
| Token 消耗 | 每次对话的 token 用量 | "单次对话 token < X" |

## 后续优化计划

- [ ] 支持更多文件类型（PPT、Excel、网页）
- [ ] Agent 工具集扩展（代码执行、API 调用）
- [ ] 多轮对话记忆优化
- [ ] 全文搜索 + 向量搜索混合检索
- [ ] 导入导出知识库
- [ ] 知识库分类与标签

## 更新日志

| 日期 | 变更内容 |
|------|----------|
| 2025-06-02 | 项目初始化，完成核心代码编写 |