"""检索调试接口"""

from fastapi import APIRouter, Depends

from app.core.models import ApiResponse, SearchRequest
from app.dependencies import get_vector_store, get_embedding
from app.storage.vector_store import VectorStore
from app.providers.embedding import QwenEmbedding
from app.services.retrieval.retriever import Retriever
from app.services.retrieval.reranker import rerank


router = APIRouter()


@router.post("/api/v1/retrieval/search")
async def search(
    request: SearchRequest,
    vs: VectorStore = Depends(get_vector_store),
    embedding: QwenEmbedding = Depends(get_embedding),
):
    """检索调试"""
    retriever = Retriever(vector_store=vs, embedding_provider=embedding)
    chunks = await retriever.retrieve(
        knowledge_id=request.knowledge_id,
        query=request.query,
        top_k=request.top_k,
    )

    # 重排序
    chunks = await rerank(request.query, chunks, top_k=request.top_k)

    return ApiResponse(data={
        "results": [
            {
                "chunk_id": c.chunk_id,
                "document_id": c.document_id,
                "text": c.text,
                "metadata": c.metadata,
                "score": c.score,
            }
            for c in chunks
        ]
    })
