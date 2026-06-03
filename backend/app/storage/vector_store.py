"""Qdrant 向量存储封装"""

from __future__ import annotations
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from typing import List
import uuid as _uuid

from app.core.config import get_settings
from app.core.models import Chunk, RetrievedChunk


# 向量维度（千问 text-embedding-v3 默认 1024 维）
DIMENSION = 1024


class VectorStore:
    """Qdrant 向量存储封装"""

    def __init__(self, client: QdrantClient = None):
        settings = get_settings()
        if client:
            self.client = client
        elif settings.qdrant_host in ("", "local"):
            # 本地模式：使用文件存储，无需 Qdrant 服务
            import os
            local_path = os.path.join(settings.upload_dir, "qdrant_data")
            os.makedirs(local_path, exist_ok=True)
            self.client = QdrantClient(path=local_path)
        else:
            self.client = QdrantClient(
                url=f"http://{settings.qdrant_host}:{settings.qdrant_port}",
                api_key=settings.qdrant_api_key or None,
            )

    def _collection_name(self, knowledge_id: str) -> str:
        return f"knowledge_{knowledge_id}"

    async def ensure_collection(self, knowledge_id: str):
        """确保知识库集合存在"""
        name = self._collection_name(knowledge_id)
        collections = [c.name for c in self.client.get_collections().collections]
        if name not in collections:
            self.client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(size=DIMENSION, distance=Distance.COSINE),
            )

    async def add_documents(self, knowledge_id: str, chunks: list[Chunk]):
        """批量添加文档向量"""
        await self.ensure_collection(knowledge_id)
        name = self._collection_name(knowledge_id)

        points = []
        for i, chunk in enumerate(chunks):
            vector = chunk.metadata.get("embedding")
            if not vector:
                continue

            point_id = str(_uuid.uuid4())
            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "knowledge_id": knowledge_id,
                        "text": chunk.text,
                        **chunk.metadata,
                    },
                )
            )

        if points:
            self.client.upsert(collection_name=name, points=points)

    async def similarity_search(
        self,
        knowledge_id: str,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[RetrievedChunk]:
        """向量相似度检索（集合不存在时返回空列表）"""
        name = self._collection_name(knowledge_id)

        # 检查集合是否存在
        collections = [c.name for c in self.client.get_collections().collections]
        if name not in collections:
            return []

        # 兼容 qdrant-client 新旧版本
        if hasattr(self.client, "query_points"):
            results = self.client.query_points(
                collection_name=name,
                query=query_embedding,
                limit=top_k,
            )
            return [
                RetrievedChunk(
                    chunk_id=str(hit.id),
                    document_id=hit.payload.get("document_id", ""),
                    text=hit.payload.get("text", ""),
                    metadata=hit.payload or {},
                    score=hit.score,
                )
                for hit in results.points
            ]
        else:
            results = self.client.search(
                collection_name=name,
                query_vector=query_embedding,
                limit=top_k,
            )
            return [
                RetrievedChunk(
                    chunk_id=hit.id,
                    document_id=hit.payload.get("document_id", ""),
                    text=hit.payload.get("text", ""),
                    metadata=hit.payload or {},
                    score=hit.score,
                )
                for hit in results
            ]

    async def delete_documents(self, knowledge_id: str, document_id: str = None):
        """删除指定文档的向量"""
        name = self._collection_name(knowledge_id)

        # 检查集合是否存在
        collections = [c.name for c in self.client.get_collections().collections]
        if name not in collections:
            return

        if document_id:
            # 删除特定文档的向量
            self.client.delete(
                collection_name=name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="document_id", match=MatchValue(value=document_id)
                        )
                    ]
                ),
            )
        else:
            # 删除整个知识库
            self.client.delete_collection(collection_name=name)

    async def get_document_count(self, knowledge_id: str) -> int:
        """获取知识库向量数量（集合不存在时返回 0）"""
        name = self._collection_name(knowledge_id)
        collections = [c.name for c in self.client.get_collections().collections]
        if name not in collections:
            return 0
        info = self.client.get_collection(collection_name=name)
        return info.points_count or 0
