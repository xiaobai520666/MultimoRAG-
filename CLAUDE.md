# MultimoRAG — 个人多模态 RAG 问答系统

## 项目概述

MultimoRAG 是一个面向个人的多模态 RAG（检索增强生成）问答系统。支持文本、图片、音频三种内容类型的知识库构建与智能问答，内置轻量 Agent 工具调用能力。

## 仓库架构

```
multimorag/
├── CLAUDE.md              ← 本文件，仓库级操作指南
├── README.md              ← 项目总文档（需求/架构/用法/优化）
├── docker-compose.yml     ← Docker 编排
├── .env.example           ← 环境变量模板
├── backend/               ← FastAPI 后端
│   ├── CLAUDE.md          ← 后端模块总述
│   └── app/
│       ├── api/           ← API 路由层
│       ├── services/      ← 业务逻辑层（ingestion/retrieval/chat/agent）
│       ├── providers/     ← 模型 API 适配层
│       ├── storage/       ← 存储层（Qdrant / PostgreSQL / 文件）
│       └── core/          ← 配置与基础设施
├── frontend/              ← Next.js 前端
│   ├── CLAUDE.md          ← 前端模块总述
│   └── src/
│       ├── app/           ← 页面（chat/knowledge/settings）
│       ├── components/    ← 共享组件
│       ├── services/      ← API 客户端
│       └── hooks/         ← 自定义 hooks
└── docs/                  ← 补充设计文档
```

## 开发工作流

### 本地调试
```bash
# 后端
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload

# 前端
cd frontend && npm install && npm run dev
```

### Docker 部署
```bash
docker compose up --build
```

### 测试
```bash
cd backend && pytest
cd frontend && npm run test
```

## 文档更新规则

1. **每次修改代码**必须同步检查并更新 `README.md`
2. **新增模块**必须创建对应的 `CLAUDE.md`
3. **修改接口**必须更新所属模块 `CLAUDE.md` 中的接口定义
4. **废弃功能**需在 `README.md` 的更新日志中注明

## 命名规范

| 层级 | 规范 |
|------|------|
| Python 文件/函数/变量 | `snake_case` |
| API 路由 | `snake_case`，版本前缀 `/api/v1/` |
| TypeScript 文件/变量 | `camelCase` |
| TypeScript 组件/类型 | `PascalCase` |
| 目录名 | 全小写，业务含义清晰 |
| 数据库表/字段 | `snake_case` |

## 代码约定

- API 响应统一格式：`{"code": 0, "data": ..., "message": "ok"}`
- 错误码规则：`0` 成功，正数为业务错误码
- 所有外部 API 调用走 `providers/` 适配层，禁止直接调用
- 向量存储操作走 `storage/vector_store.py` 封装，禁止直接操作 Qdrant
- 异常统一使用 `core/exceptions.py` 中的自定义异常

## Code Review 要求

- 新功能必须有单元测试
- 接口变更必须同步更新 README.md 中的 API 概览
- 新增依赖需要注明用途和版本