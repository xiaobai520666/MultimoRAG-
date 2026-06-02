# 检索排序 — backend/app/services/retrieval/

## 模块功能

负责从向量库中检索相关知识块，并进行重排序以提高结果质量。

## 需求边界

**属于本模块：**
- 文本向量相似度检索（Qdrant）
- 多路检索（后续：全文+向量混合）
- 检索结果重排序
- 检索参数调优（top_k、score_threshold）

**不属于本模块：**
- 对话上下文组装（归 chat/）
- LLM 调用（归 providers/）
- 结果持久化（归 storage/）

## 接口定义

```python
# retriever.py
async def retrieve(
    knowledge_id: str,
    query: str,
    top_k: int = 5,
    score_threshold: float = 0.0
) -> list[RetrievedChunk]:
    """向量检索，返回按分数降序排列的块"""

# reranker.py
async def rerank(
    query: str,
    chunks: list[RetrievedChunk],
    top_k: int = None
) -> list[RetrievedChunk]:
    """对检索结果进行重排序，返回新排序"""

class RetrievedChunk:
    chunk_id: str
    document_id: str
    text: str
    metadata: dict
    score: float
```

## 依赖与约束

- 依赖 `storage/vector_store.py` 查询 Qdrant
- 依赖 `providers/reranker.py`（如果启用 Rerank API）
- retriever 返回的结果必须包含对应的原文和元数据，不返回裸向量