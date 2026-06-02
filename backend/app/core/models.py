"""Pydantic 数据模型"""

from __future__ import annotations
from typing import Generic, TypeVar
from pydantic import BaseModel, Field
from typing import List, Optional


T = TypeVar("T")


# ========== 通用 ==========

class ApiResponse(BaseModel, Generic[T]):
    code: int = 0
    data: Optional[T] = None
    message: str = "ok"


class PageResult(BaseModel, Generic[T]):
    items: List[T]
    total: int


# ========== 知识库 ==========

class CreateKnowledgeRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="知识库名称")
    description: str = Field("", max_length=500, description="知识库描述")


class KnowledgeResponse(BaseModel):
    id: str
    name: str
    description: str
    created_at: str
    document_count: int


# ========== 文件上传 ==========

class UploadResponse(BaseModel):
    task_id: str
    status: str = "uploading"
    file_name: str


class IngestionStatus(BaseModel):
    task_id: str
    status: str  # uploading | processing | completed | failed
    progress: int = 0
    error: Optional[str] = None


# ========== 对话 ==========

class MessageItem(BaseModel):
    role: str  # user | assistant | system
    content: str


class ChatRequest(BaseModel):
    knowledge_id: str
    message: str = Field(..., min_length=1, description="用户消息")
    history: List[MessageItem] = Field(default_factory=list, description="对话历史")


class CitationItem(BaseModel):
    chunk_id: str
    document_id: str
    text: str
    score: float


class ChatResponse(BaseModel):
    reply: str
    citations: List[CitationItem]
    usage: dict = Field(default_factory=dict)


# ========== 检索 ==========

class SearchRequest(BaseModel):
    knowledge_id: str
    query: str
    top_k: int = Field(5, ge=1, le=20)


class RetrievedChunkItem(BaseModel):
    chunk_id: str
    document_id: str
    text: str
    metadata: dict = Field(default_factory=dict)
    score: float


class SearchResponse(BaseModel):
    results: List[RetrievedChunkItem]


# ========== Agent ==========

class AgentRequest(BaseModel):
    knowledge_id: str
    message: str = Field(..., min_length=1)
    history: List[MessageItem] = Field(default_factory=list)


class ToolCallLog(BaseModel):
    tool_name: str
    input: dict = Field(default_factory=dict)
    output: str
    duration_ms: int


class AgentResponse(BaseModel):
    reply: str
    tool_calls: List[ToolCallLog]
    citations: List[CitationItem]


# ========== 内部 DTO ==========

class Chunk(BaseModel):
    """入库分块"""
    text: str
    metadata: dict = Field(default_factory=dict)


class RetrievedChunk(BaseModel):
    """检索结果"""
    chunk_id: str
    document_id: str
    text: str
    metadata: dict = Field(default_factory=dict)
    score: float


class Message(BaseModel):
    """对话消息"""
    role: str
    content: str


class IngestionResult(BaseModel):
    """入库结果"""
    document_id: str
    chunk_count: int
    status: str  # completed | failed
    error: Optional[str] = None
