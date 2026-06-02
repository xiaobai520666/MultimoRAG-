"""重排序（第一期按向量分数排序，预留 Rerank API 接口）"""

from __future__ import annotations
from app.core.models import RetrievedChunk


async def rerank(
    query: str,
    chunks: list[RetrievedChunk],
    top_k: int = None,
) -> list[RetrievedChunk]:
    """
    对检索结果重排序

    第一期：直接返回按向量分数排序的结果
    后续：可接入千问 Rerank API 进行精排
    """
    # 已按分数降序排列（Qdrant 返回顺序）
    if top_k:
        return chunks[:top_k]
    return chunks
