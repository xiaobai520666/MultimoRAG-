# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

MultimoRAG 是一个面向个人的多模态 RAG（检索增强生成）问答系统。支持文本、图片、音频三种内容类型的知识库构建与智能问答，内置轻量 Agent 工具调用能力。

技术栈：Next.js 14 (App Router) + FastAPI (Python 3.11) + DeepSeek LLM + Qdrant + PostgreSQL 16 + Docker Compose。

## 常用命令

### 本地开发

```bash
# 仅启动基础设施（PostgreSQL + Qdrant）
docker compose up -d postgres qdrant

# 后端（端口 8000）
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8000

# 前端（端口 3000），需先创建 .env.local 写入 NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
cd frontend && npm install && npm run dev
```

### Docker 一键部署

```bash
cp .env.example .env   # 编辑填入 DEEPSEEK_API_KEY，QDRANT_HOST=qdrant
docker compose up -d --build
```

### 代码检查

```bash
cd frontend && npm run lint        # next lint
cd backend && ruff check .         # 如已安装 ruff
```

### 测试

**当前仓库没有任何测试用例。** `pytest` 和 `npm run test` 会失败。添加测试后使用：

```bash
cd backend && pytest                          # 全部后端测试
cd backend && pytest path/to/test.py::函数名    # 单个测试
cd frontend && npm run test                   # 前端测试（需先在 package.json 配置）
```

## 架构

### 分层依赖关系

```
api/（路由、参数校验、响应包装）
  → services/（业务编排，全 async）
    → providers/（外部 API 适配器 — 禁止业务代码直接调用）
    → storage/（Qdrant / PostgreSQL / 文件系统 — 禁止业务代码直接操作）
```

每层只能调用紧邻的下一层。API 层绝不直接碰 providers 或 storage。

### 依赖注入机制（backend/app/dependencies.py）

所有服务依赖通过模块级单例 + getter 函数管理，首次调用时懒初始化：

- `get_llm()` → 有 `DEEPSEEK_API_KEY` 返回 `DeepSeekLLM`，否则尝试 `QwenLLM`
- `get_embedding()` → 读 `EMBEDDING_PROVIDER` 环境变量：`"local"` 默认走 `LocalEmbedding`，`"qwen"` 且在 Qwen Key 存在时走 `QwenEmbedding`
- `get_vector_store()` / `get_metadata_db()` / `get_file_store()` → 存储层单例
- `get_ocr()` / `get_audio()` → 固定返回 `QwenOCR` / `QwenAudio`（需 Qwen Key 才能正常工作）

FastAPI 路由通过 `Depends(get_llm)` 注入。新增 Provider 时遵循相同模式：写 getter → 读配置 → 返回对应实现。

### Provider 调用链（LLM 与 Embedding）

**LLM 路径：** `DeepSeekLLM`（主力）→ `QwenLLM`（备选）。两者均调用 OpenAI 兼容的 `/chat/completions` 端点。超时 120s，默认 `temperature=0.7`，`max_tokens=2048`。

**Embedding 路径：** 由 `EMBEDDING_PROVIDER` 决定：
- `"local"`（默认）：`LocalEmbedding` — 基于字符/双字词频统计 + SHA256 哈希投影到 **1024 维**向量，做 L2 归一化。无需 API Key，但检索效果差，是临时方案。
- `"qwen"`：`QwenEmbedding` — 调用千问 text-embedding-v3 API。
- `DeepSeekEmbedding` 代码中存在但未接入配置开关 — 它让 LLM 先提取关键词再降级到 LocalEmbedding。

**关键常量：** 向量维度 `DIMENSION = 1024` 在 `providers/embedding.py` 和 `storage/vector_store.py` 各定义了一份，修改时必须两边同步。

### 向量存储（Qdrant）

- 集合命名规则：`knowledge_{knowledge_id}`
- 距离度量：Cosine
- 所有操作前先检查集合是否存在，不存在时返回空列表/0 而非抛异常
- Point payload 字段：`knowledge_id`、`text`、`document_id`，外加 chunk 的全部 metadata

### 异常处理模式

`AppException` 及其子类（`ParamError`=4001、`NotFoundError`=4004、`InternalError`=5001、`APIError`=5002）由 `main.py` 全局异常处理器统一捕获，**始终返回 HTTP 200**，错误码放在 JSON body 中。调用方不能依赖 HTTP 状态码判断成败，必须检查 `response.code`。

错误码速查：

| code | 异常类 | 含义 |
|------|--------|------|
| 0 | — | 成功 |
| 4001 | `ParamError` | 参数错误 |
| 4004 | `NotFoundError` | 资源不存在 |
| 5001 | `InternalError` | 内部错误 |
| 5002 | `APIError` | 外部 API 调用失败 |

### 核心数据流

**入库流程：** 上传文件 → `FileStore.save()` → 解析（文本/OCR/转写）→ 分块（递归切分，500 token，50 重叠）→ 向量化 → 写入 Qdrant + 记录到 PostgreSQL。

**RAG 问答：** 用户消息 → 查询向量化 → `VectorStore.similarity_search()`（top_k=5）→ 组装 Prompt（检索块 + 对话历史）→ `LLMProvider.chat()` → 返回答案 + 引用溯源。

**Agent 执行：** 用户消息 → LLM 意图分析 → 调度已注册工具（QueryRewrite / KnowledgeSearch / KnowledgeSummary）→ 整合工具输出 → LLM 生成最终回复 → 返回答案 + 工具调用日志。

### 前端结构要点

- Next.js 14 App Router + TypeScript，路径别名 `@/*` → `./src/*`
- 无第三方 UI 库，样式用 Tailwind CSS class
- `services/api.ts` — 基础 HTTP 封装（get / post / uploadFile）
- `services/index.ts` — 业务 API 函数并 re-export
- `services/types.ts` — 共享 TS 类型
- 三个页面：`/chat`（对话）、`/knowledge`（知识库 CRUD + 文件上传）、`/settings`（配置存 localStorage，不依赖后端）
- 组件分层：`Chat/`（消息气泡、引用块）、`Layout/`（侧栏、顶栏）、`common/`（加载/空/错误态）

### Docker 编排

4 个服务：`postgres`（16-alpine）、`qdrant`（latest）、`backend`、`frontend`。backend 依赖 postgres（healthy）和 qdrant（started）；frontend 依赖 backend。后端 Dockerfile 中 pip 使用阿里云镜像源加速。

本地开发 vs Docker 部署的关键区别：

| 配置项 | 本地开发 | Docker 部署 |
|--------|----------|------------|
| `QDRANT_HOST` | `localhost` | `qdrant`（容器名） |
| `POSTGRES_DSN` | `...@localhost:5432/...` | `...@postgres:5432/...` |
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000/api/v1` | `/api/v1`（经 Nginx） |

## 代码约定

- API 前缀 `/api/v1/`，响应格式：`{"code": 0, "data": ..., "message": "ok"}`
- Python：`snake_case`；TypeScript：文件/变量 `camelCase`，组件/类型 `PascalCase`
- 所有外部 API 调用必须走 `providers/` 适配层，禁止直接调用
- 所有向量库操作必须走 `storage/vector_store.py` 封装，禁止直接操作 Qdrant
- 自定义异常必须使用 `core/exceptions.py`
- Service 层方法全部 `async`
- 文件路径使用正斜杠 `/`
- v1 无用户认证，CORS 开放所有来源（面向个人使用）

## 文档更新规则

1. 每次修改代码必须同步检查并更新 `README.md`
2. 新增模块必须创建对应的 `CLAUDE.md`
3. 修改接口必须更新所属模块 `CLAUDE.md` 中的接口定义
4. 废弃功能需在 `README.md` 的更新日志中注明

## 已知限制

1. **Embedding 质量低：** LocalEmbedding 使用 TF-IDF + 哈希投影，检索效果远不如专业 API。后期需切换到 Qwen/DeepSeek Embedding API。
2. **OCR/音频依赖 Qwen API：** 未配置 Qwen Key 时会调用失败。
3. **无用户认证：** 第一版面向个人使用。
4. **无流式响应：** LLM 回复为一次性返回，未实现 SSE。
5. **无测试用例：** 仓库尚未添加任何自动化测试。
