# MultimoRAG — 个人多模态 RAG 问答系统

## 项目概述

MultimoRAG 是一个面向个人的多模态知识问答系统。你可以把文本文件、图片、音频导入知识库，然后像聊天一样提问，系统会从知识库中检索相关内容并生成答案。内置轻量 Agent 能力，支持简单的工具调用。

**核心理念：** 隐私优先、API 驱动、模块化可扩展。

## 功能需求

### 第一期（当前版本）

| 功能 | 说明 | 状态 |
|------|------|------|
| 文本知识管理 | 上传 PDF、Markdown、TXT，自动解析入库 | ✅ |
| 图片知识管理 | 上传图片（JPG/PNG），OCR 提取文字后入库 | ⚠️ 需 Qwen API Key |
| 音频知识管理 | 上传音频（MP3/WAV），转写文字后入库 | ⚠️ 需 Qwen API Key |
| 多模态 RAG 问答 | 基于知识库的智能问答，含引用溯源 | ✅ |
| 轻量 Agent | 支持查询改写、知识检索、知识摘要等工具 | ✅ |
| Web 对话界面 | 浏览器端对话交互（聊天/知识库管理/设置） | ✅ |
| Docker 一键部署 | docker-compose 启动全部服务 | ✅ |

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
│                   前端 (Next.js 14)               │
│          Chat / Knowledge / Settings             │
└──────────────────────┬──────────────────────────┘
                       │ HTTP / JSON
              ┌────────▼────────┐
              │  Nginx (反向代理) │
              └──┬──────────┬───┘
                 │          │
┌────────────────▼──┐  ┌──▼──────────────────────┐
│  Frontend :3000    │  │  Backend API :8000       │
│  (Next.js SSR)     │  │  (FastAPI)               │
└────────────────────┘  └──┬──────────┬───────────┘
                           │          │
              ┌────────────▼──┐  ┌───▼───────────┐
              │  Retrieval    │  │   Agent         │
              │  检索+重排序   │  │   意图+工具     │
              └──────┬────────┘  └──┬─────────────┘
                     │              │
              ┌──────▼──────────────▼─────────────┐
              │        Providers 模型适配层         │
              │  DeepSeek(LLM) │ LocalEmbedding     │
              │  QwenOCR(预留) │ QwenAudio(预留)     │
              └────────────────┬───────────────────┘
                               │
              ┌────────────────▼───────────────────┐
              │          Storage 存储层              │
              │  Qdrant(向量) │ PostgreSQL(元数据)   │
              │  FileStore(文件)                     │
              └────────────────────────────────────┘
```

### 数据流

```
上传文件 → 解析(文本/OCR/转写) → 分块 → 嵌入 → 存入 Qdrant
                                                         ↓
用户提问 → 检索 Top-K → 重排序 → 组装上下文 → 调用 DeepSeek → 返回(答案+引用)
                                                         ↓
Agent 请求 → 分析意图 → 调用工具 → 整合结果 → 返回
```

## 技术栈

| 层 | 技术 | 说明 |
|---|------|------|
| 前端 | Next.js 14 (App Router) + TypeScript | SSR, 文件路由 |
| 后端 | FastAPI (Python 3.11) | 异步, 自动 API 文档 |
| LLM | DeepSeek (deepseek-chat) | OpenAI 兼容接口, 后期切 Qwen |
| Embedding | LocalEmbedding (TF-IDF + 哈希投影) | 临时方案, 无需 API Key, 后期换真实 Embedding API |
| 向量库 | Qdrant | 内存 ~80MB, 支持 payload 过滤 |
| 关系库 | PostgreSQL 16 | 知识库元数据, 对话历史 |
| 反向代理 | Nginx | 统一入口, /api/ 代理到后端 |
| 部署 | Docker Compose | 4 服务: postgres, qdrant, backend, frontend |

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
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py            # 应用入口
│       ├── dependencies.py    # 依赖注入
│       ├── api/               # API 路由层
│       │   ├── router_v1.py   # 路由注册
│       │   ├── chat.py        # POST /api/v1/chat
│       │   ├── knowledge.py   # CRUD /api/v1/knowledge
│       │   ├── ingestion.py   # POST /api/v1/ingestion/upload
│       │   ├── retrieval.py   # POST /api/v1/retrieval/search
│       │   ├── agent.py       # POST /api/v1/agent/execute
│       │   └── health.py      # GET /api/v1/health
│       ├── services/          # 业务逻辑层
│       │   ├── ingestion/     # 入库流水线 (parse→chunk→embed→store)
│       │   ├── retrieval/     # 检索 + 重排序
│       │   ├── chat/          # RAG 对话编排 + 上下文组装
│       │   └── agent/         # Agent 执行器 + 工具集
│       ├── providers/         # 模型适配层
│       │   ├── llm.py         # DeepSeek LLM + Qwen 预留
│       │   ├── embedding.py   # LocalEmbedding + Qwen 预留
│       │   ├── ocr.py         # Qwen OCR
│       │   └── audio.py       # Qwen 音频转写
│       ├── storage/           # 存储层
│       │   ├── vector_store.py    # Qdrant 封装
│       │   ├── metadata_db.py     # PostgreSQL 封装
│       │   ├── file_store.py      # 文件存储
│       │   └── schemas.py         # ORM 模型
│       └── core/              # 基础设施
│           ├── config.py      # 配置管理
│           ├── models.py      # Pydantic 数据模型
│           └── exceptions.py  # 自定义异常
│
├── frontend/                  # Next.js 前端
│   ├── CLAUDE.md              # 前端总述
│   ├── Dockerfile
│   ├── tsconfig.json
│   └── src/
│       ├── app/
│       │   ├── page.tsx       # 首页 → 重定向到 /chat
│       │   ├── layout.tsx     # 根布局
│       │   ├── chat/          # 对话页面
│       │   ├── knowledge/     # 知识库管理
│       │   └── settings/      # 设置页面
│       └── services/          # API 客户端封装
│           ├── api.ts         # 基础 HTTP 客户端
│           ├── index.ts       # 业务 API 函数
│           └── types.ts       # TypeScript 类型定义
│
└── docs/                      # 补充设计文档
```

## 快速开始

### 前置条件

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose

### 本地开发（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/xiaobai520666/MultimoRAG-.git
cd MultimoRAG-

# 2. 创建本地环境变量
cp .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY
# 本地开发时 QDRANT_HOST=localhost

# 3. 启动基础设施（PostgreSQL + Qdrant）
docker compose up -d postgres qdrant

# 4. 启动后端
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 5. 启动前端（另开终端）
cd frontend
npm install
# 创建 .env.local：
#   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
npm run dev
```

访问 http://localhost:3000

### Docker 部署（生产）

```bash
# 1. 克隆并配置
git clone https://github.com/xiaobai520666/MultimoRAG-.git
cd MultimoRAG-
cp .env.example .env
# 编辑 .env，填入 API Key，QDRANT_HOST=qdrant

# 2. 一键启动
docker compose up -d --build

# 3. 配置 Nginx 反向代理（可选，用于隐藏端口号）
# 将 /etc/nginx/sites-enabled/default 替换为:
#   location / { proxy_pass http://127.0.0.1:3000; }
#   location /api/ { proxy_pass http://127.0.0.1:8000/api/; }
```

## API 概览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/health` | 健康检查 |
| POST | `/api/v1/chat` | 发送对话消息（RAG 问答） |
| GET | `/api/v1/knowledge` | 获取知识库列表 |
| POST | `/api/v1/knowledge` | 创建知识库 |
| DELETE | `/api/v1/knowledge/{id}` | 删除知识库 |
| POST | `/api/v1/ingestion/upload` | 上传文件 |
| GET | `/api/v1/ingestion/{id}/status` | 查询入库状态 |
| POST | `/api/v1/retrieval/search` | 检索调试接口 |
| POST | `/api/v1/agent/execute` | 执行 Agent 调用 |

**统一响应格式：**
```json
{
  "code": 0,
  "data": { ... },
  "message": "ok"
}
```
`code=0` 成功，正数为业务错误码。

## 配置说明

通过 `.env` 文件配置：

```bash
# === 核心 API ===
DEEPSEEK_API_KEY=sk-xxxxx              # DeepSeek API 密钥
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
DEEPSEEK_LLM_MODEL=deepseek-chat

# === 嵌入 ===
EMBEDDING_PROVIDER=local               # local(默认) | qwen

# === 向量库 Qdrant ===
QDRANT_HOST=localhost                  # Docker 部署时用 qdrant
QDRANT_PORT=6333
QDRANT_API_KEY=

# === PostgreSQL ===
POSTGRES_USER=multimorag
POSTGRES_PASSWORD=multimorag
POSTGRES_DB=multimorag
POSTGRES_PORT=5432

# === 文件存储 ===
UPLOAD_DIR=./data/uploads

# === 服务端口 ===
BACKEND_PORT=8000
FRONTEND_PORT=3000

# === Qwen 预留（后期多模态切换） ===
QWEN_API_KEY=
QWEN_API_BASE=https://dashscope.aliyuncs.com/api/v1
```

### 本地开发 vs Docker 部署的区别

| 配置项 | 本地开发 | Docker 部署 |
|--------|----------|------------|
| `QDRANT_HOST` | `localhost` | `qdrant` |
| `POSTGRES_DSN` | `postgresql://...@localhost:5432/...` | `postgresql://...@postgres:5432/...` |
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000/api/v1` | `/api/v1`（经 Nginx 代理） |

## 技术选型说明

### 向量库：Qdrant

| 对比项 | Qdrant | Chroma | Milvus Lite |
|--------|--------|--------|-------------|
| 内存占用 | ~80MB | ~50MB | ~150MB |
| 2c2g 适配 | ✅ 稳定 | ⚠️ 容器化有锁问题 | ✅ |
| payload 过滤 | ✅ 成熟 | ⚠️ 基础 | ✅ |
| 生产成熟度 | ✅ 生产级 | ⚠️ 适合原型 | ✅ 分布式强 |
| **2c2g 推荐度** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |

**选择 Qdrant 的理由：** 2c2g 服务器内存敏感；Docker 一行启动；payload 过滤对多模态场景最实用。

### 分块策略

| 模态 | 策略 | 参数 |
|------|------|------|
| 文本 | 递归切分 | 500 token, 50 token 重叠 |
| 图片 | 整张一块 | OCR 全文 |
| 音频 | 段落切分 | 30-60 秒语义段落 |

### Agent 工具集（第一版 3 个）

| 工具 | 功能 | 说明 |
|------|------|------|
| QueryRewriteTool | 查询改写 | 用户问题 → 更适合检索的形式 |
| KnowledgeSearchTool | 知识库搜索 | 调用 retrieval 模块 |
| KnowledgeSummaryTool | 知识摘要 | 检索 + LLM 生成摘要 |

### 检索效果评估（计划中）

| 指标 | 说明 |
|------|------|
| Hit Rate @ K | 正确答案在前 K 条结果中的比例 |
| MRR | Mean Reciprocal Rank，首条正确答案的排名倒数 |
| 响应时间 | API 端到端延迟 |
| Token 消耗 | 每次对话的 token 用量 |

## 当前限制与已知问题

1. **Embedding 质量低：** LocalEmbedding 使用 TF-IDF + 哈希投影，检索效果远不如专业 Embedding API。后期需切换到 Qwen/DeepSeek Embedding API。
2. **OCR/音频需 Qwen API：** 图片 OCR 和音频转写依赖 Qwen 多模态 API，目前未配置 Qwen Key 会调用失败。
3. **无用户认证：** 第一版面向个人使用，无登录/权限系统。
4. **无流式响应：** LLM 回复为一次性返回，未实现 SSE 流式输出。

## 后续优化计划

- [ ] 接入真实 Embedding API（Qwen text-embedding-v3）
- [ ] LLM 回复流式输出（SSE）
- [ ] 混合检索（全文 + 向量）
- [ ] Rerank API 接入
- [ ] 更多文件类型（PPT、Excel、网页）
- [ ] Agent 工具集扩展
- [ ] 检索效果评估体系
- [ ] 知识库导入导出

## 更新日志

| 日期 | 变更内容 |
|------|----------|
| 2025-06-02 | 项目初始化，完成核心代码编写：FastAPI 后端 + Next.js 前端 + Docker 部署 |
| 2025-06-02 | LLM 切换为 DeepSeek，Embedding 使用 LocalEmbedding 临时方案 |
| 2025-06-02 | Docker 镜像源切换到阿里云，加速国内构建 |
| 2025-06-02 | 修复 VectorStore 空集合处理、MetadataDB 知识库不存在的容错 |
| 2025-06-02 | 部署到服务器 (47.104.242.174)，Nginx 反向代理统一入口 |
