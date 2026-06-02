# 对话编排 — backend/app/services/chat/

## 模块功能

负责 RAG 对话的完整编排：接收用户问题 → 检索知识 → 组装 Prompt → 调用 LLM → 返回带引用的答案。

## 需求边界

**属于本模块：**
- 对话上下文的组装与管理
- Prompt 模板构建（system/user/assistant）
- 引用溯源（答案到原文块的映射）
- 多轮对话历史维护

**不属于本模块：**
- 向量检索（归 retrieval/）
- LLM API 调用（归 providers/）
- Agent 工具执行（归 agent/）

## 接口定义

```python
# orchestrator.py
async def chat(
    knowledge_id: str,
    message: str,
    history: list[Message] = None,
    config: ChatConfig = None
) -> ChatResult:
    """RAG 对话主流程：检索 → 组装 → 调用 LLM → 返回"""

# context.py
def build_prompt(
    query: str,
    chunks: list[RetrievedChunk],
    history: list[Message]
) -> list[dict]:
    """构建 LLM 的 messages 列表"""
    
class ChatResult:
    reply: str
    citations: list[Citation]
    usage: dict            # token 用量

class Citation:
    chunk_id: str
    document_id: str
    text: str
    score: float
```

## 依赖与约束

- 依赖 `services/retrieval/` 获取知识块
- 依赖 `providers/llm.py` 调用 LLM
- 依赖 `core/models.py` 中的 Message 数据模型
- Prompt 模板放在本模块内部，不对外暴露