# API 路由层 — backend/app/api/

## 模块功能

定义所有 HTTP API 端点，负责请求校验、路由分发、响应格式化。不包含业务逻辑，只做编排和转发。

## 需求边界

**属于本模块：**
- 路由注册与版本管理（v1）
- 请求参数校验（Pydantic）
- 统一响应格式包装（code/data/message）
- 错误码映射与异常捕获
- 健康检查端点

**不属于本模块：**
- 具体业务逻辑（调用 services）
- 模型 API 调用（调用 providers）
- 数据持久化操作（调用 storage）

## 接口定义

| 方法 | 路径 | 请求体 | 响应 data | 说明 |
|------|------|--------|-----------|------|
| GET | `/api/v1/health` | - | `{"status": "ok"}` | 健康检查 |
| POST | `/api/v1/chat` | `{knowledge_id, message, history[]}` | `{reply, citations[]}` | 对话问答 |
| GET | `/api/v1/knowledge` | query: `page, size` | `{items[], total}` | 知识库列表 |
| POST | `/api/v1/knowledge` | `{name, description}` | `{id, name, ...}` | 创建知识库 |
| DELETE | `/api/v1/knowledge/{id}` | - | `{}` | 删除知识库 |
| POST | `/api/v1/ingestion/upload` | multipart: file, knowledge_id | `{task_id, status}` | 上传文件 |
| GET | `/api/v1/ingestion/{id}/status` | - | `{task_id, status, progress}` | 入库状态 |
| POST | `/api/v1/retrieval/search` | `{knowledge_id, query, top_k}` | `{results[]}` | 检索调试 |
| POST | `/api/v1/agent/execute` | `{knowledge_id, message}` | `{reply, tool_calls[]}` | Agent 执行 |

错误码：
| code | 说明 |
|------|------|
| 0 | 成功 |
| 4001 | 参数错误 |
| 4004 | 资源不存在 |
| 5001 | 内部错误 |
| 5002 | 外部 API 调用失败 |

## 依赖与约束

- 依赖 `services/` 层执行业务逻辑
- 依赖 `core/models.py` 中的请求/响应模型
- 依赖 `core/exceptions.py` 中的异常处理