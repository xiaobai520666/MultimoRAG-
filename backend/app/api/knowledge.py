"""知识库 CRUD"""

from fastapi import APIRouter, Depends

from app.core.models import (
    ApiResponse,
    CreateKnowledgeRequest,
    KnowledgeResponse,
    PageResult,
)
from app.core.exceptions import NotFoundError
from app.storage.metadata_db import MetadataDB
from app.storage.vector_store import VectorStore
from app.dependencies import get_metadata_db, get_vector_store


router = APIRouter()


@router.get("/api/v1/knowledge", response_model=ApiResponse)
async def list_knowledge(
    page: int = 1,
    size: int = 10,
    db: MetadataDB = Depends(get_metadata_db),
):
    """获取知识库列表"""
    result = db.list_knowledge(page=page, size=size)
    return ApiResponse(
        data={"items": result["items"], "total": result["total"]}
    )


@router.post("/api/v1/knowledge", response_model=ApiResponse)
async def create_knowledge(
    request: CreateKnowledgeRequest,
    db: MetadataDB = Depends(get_metadata_db),
):
    """创建知识库"""
    knowledge = db.create_knowledge(name=request.name, description=request.description)
    return ApiResponse(data=knowledge)


@router.delete("/api/v1/knowledge/{knowledge_id}", response_model=ApiResponse)
async def delete_knowledge(
    knowledge_id: str,
    db: MetadataDB = Depends(get_metadata_db),
    vs: VectorStore = Depends(get_vector_store),
):
    """删除知识库"""
    knowledge = db.get_knowledge(knowledge_id)
    if not knowledge:
        raise NotFoundError(message="知识库不存在")

    await vs.delete_documents(knowledge_id)
    db.delete_knowledge(knowledge_id)

    return ApiResponse(data={})
