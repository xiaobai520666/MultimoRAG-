"""Agent 执行接口"""

from fastapi import APIRouter, Depends

from app.core.models import ApiResponse, AgentRequest
from app.dependencies import get_llm, get_vector_store, get_embedding
from app.storage.vector_store import VectorStore
from app.providers.llm import LLMProvider
from app.providers.embedding import QwenEmbedding
from app.services.retrieval.retriever import Retriever
from app.services.agent.executor import AgentExecutor


router = APIRouter()


@router.post("/api/v1/agent/execute")
async def execute_agent(
    request: AgentRequest,
    vs: VectorStore = Depends(get_vector_store),
    llm: LLMProvider = Depends(get_llm),
    embedding: QwenEmbedding = Depends(get_embedding),
):
    """执行 Agent 调用"""
    retriever = Retriever(vector_store=vs, embedding_provider=embedding)
    executor = AgentExecutor(retriever=retriever, llm=llm)

    result = await executor.execute_agent(request)

    return ApiResponse(data={
        "reply": result.reply,
        "tool_calls": [tc.model_dump() for tc in result.tool_calls],
        "citations": [c.model_dump() for c in result.citations],
    })
