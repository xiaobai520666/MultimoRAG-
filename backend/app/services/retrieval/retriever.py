"""多路检索"""

from __future__ import annotations
from app.storage.vector_store import VectorStore
from app.core.models import RetrievedChunk


class Retriever:
    """向量检索服务"""

    def __init__(self, vector_store: VectorStore, embedding_provider=None):
        self.vector_store = vector_store
        self.embedding_provider = embedding_provider

    async def retrieve(
        self,
        knowledge_id: str,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.0,
    ) -> list[RetrievedChunk]:
        """
        向量检索

        Args:
            knowledge_id: 知识库 ID
            query: 检索文本
            top_k: 返回数量
            score_threshold: 分数阈值

        Returns:
            按分数降序排列的检索结果
        """
        # 将查询向量化
        query_embedding = await self.embedding_provider.embed([query])
        if not query_embedding or not query_embedding[0]:
            return []

        # 检索
        results = await self.vector_store.similarity_search(
            knowledge_id=knowledge_id,
            query_embedding=query_embedding[0],
            top_k=top_k,
        )

        # 应用分数阈值
        if score_threshold > 0:
            results = [r for r in results if r.score >= score_threshold]

        return results
