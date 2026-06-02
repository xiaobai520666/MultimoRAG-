"""对话问答"""

from fastapi import APIRouter, Depends

from app.core.models import (
    ApiResponse,
    ChatRequest,
)
from app.dependencies import get_metadata_db, get_vector_store, get_llm, get_embedding
from app.storage.metadata_db import MetadataDB
from app.storage.vector_store import VectorStore
from app.providers.llm import LLMProvider
from app.providers.embedding import QwenEmbedding
from app.services.retrieval.retriever import Retriever
from app.services.chat.orchestrator import ChatOrchestrator


router = APIRouter()


@router.post("/api/v1/chat")
async def chat(
    request: ChatRequest,
    db: MetadataDB = Depends(get_metadata_db),
    vs: VectorStore = Depends(get_vector_store),
    llm: LLMProvider = Depends(get_llm),
    embedding: QwenEmbedding = Depends(get_embedding),
):
    """发送对话消息，获取 RAG 回复"""
    retriever = Retriever(vector_store=vs, embedding_provider=embedding)
    orchestrator = ChatOrchestrator(
        retriever=retriever,
        llm=llm,
        metadata_db=db,
    )

    result = await orchestrator.chat(request)
    return ApiResponse(data={
        "reply": result.reply,
        "citations": [c.model_dump() for c in result.citations],
        "usage": result.usage,
    })
