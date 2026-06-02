# 服务层 — backend/app/services/

## 模块功能

业务逻辑层，位于 API 路由层和存储/提供商层之间。负责编排 ingest、retrieval、chat、agent 四个核心业务领域。

## 依赖关系

```
api / (路由) → services / (编排) → providers / (模型 API)
                                → storage / (持久化)
```

## 子模块

| 模块 | 职责 | 对外接口 |
|------|------|----------|
| `ingestion/` | 文件解析 → 分块 → 嵌入 → 入库 | `process_file()` |
| `retrieval/` | 向量检索 → 重排序 | `retrieve()`, `rerank()` |
| `chat/` | 检索 → 组装 Prompt → LLM 调用 → 返回 | `chat()` |
| `agent/` | 意图识别 → 工具调度 → 结果整合 | `execute_agent()` |

## 约束

- 服务层不直接操作 HTTP 请求/响应对象
- 服务层不直接调用外部 API（全部通过 providers/）
- 服务层不直接操作数据库/向量库（全部通过 storage/）
- 服务层方法均为 async