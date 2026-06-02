"""RAG 对话编排"""

from __future__ import annotations
from app.core.models import (
    ChatRequest,
    ChatResponse,
    CitationItem,
    RetrievedChunk,
    Message,
)
from app.core.exceptions import NotFoundError
from app.services.retrieval.retriever import Retriever
from app.services.retrieval.reranker import rerank
from app.services.chat.context import build_prompt
from app.providers.llm import LLMProvider
from app.storage.metadata_db import MetadataDB


class ChatOrchestrator:
    """RAG 对话编排器"""

    def __init__(
        self,
        retriever: Retriever,
        llm: LLMProvider,
        metadata_db: MetadataDB,
    ):
        self.retriever = retriever
        self.llm = llm
        self.metadata_db = metadata_db

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """
        RAG 对话主流程：检索 → 组装 → 调用 LLM → 返回

        Args:
            request: 对话请求

        Returns:
            ChatResponse: 带引用的回复
        """
        # Step 1: 检索
        chunks = await self.retriever.retrieve(
            knowledge_id=request.knowledge_id,
            query=request.message,
            top_k=5,
        )

        # Step 2: 重排序
        chunks = await rerank(request.message, chunks, top_k=5)

        # Step 3: 组装 Prompt
        history = [
            Message(role=m.role, content=m.content) for m in request.history
        ]
        messages = build_prompt(
            query=request.message,
            chunks=chunks,
            history=history,
        )

        # Step 4: 调用 LLM
        result = await self.llm.chat(messages=messages)

        # Step 5: 构建引用
        citations = [
            CitationItem(
                chunk_id=c.chunk_id,
                document_id=c.document_id,
                text=c.text[:200],  # 截取前 200 字
                score=c.score,
            )
            for c in chunks[:3]  # 最多返回 3 个引用
        ]

        # Step 6: 保存消息
        self.metadata_db.save_message(
            request.knowledge_id, "user", request.message
        )
        self.metadata_db.save_message(
            request.knowledge_id, "assistant", result.content
        )

        return ChatResponse(
            reply=result.content,
            citations=citations,
            usage=result.usage,
        )
