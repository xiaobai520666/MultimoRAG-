"""向量嵌入服务"""

from __future__ import annotations
from app.core.models import Chunk


async def embed_chunks(chunks: list[Chunk], embedding_provider) -> list[Chunk]:
    """批量向量化"""
    if not chunks:
        return []

    texts = [chunk.text for chunk in chunks]
    embeddings = await embedding_provider.embed(texts)

    for chunk, embedding in zip(chunks, embeddings):
        chunk.metadata["embedding"] = embedding

    return chunks


async def embed_text(text: str, embedding_provider) -> list[float]:
    """单个文本向量化"""
    embeddings = await embedding_provider.embed([text])
    return embeddings[0] if embeddings else []
