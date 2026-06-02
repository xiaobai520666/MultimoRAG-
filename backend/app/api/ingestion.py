"""文件上传与入库"""

import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse

from app.core.models import ApiResponse, UploadResponse, IngestionStatus
from app.core.exceptions import ParamError
from app.storage.metadata_db import MetadataDB
from app.storage.file_store import FileStore
from app.dependencies import get_metadata_db, get_file_store
from app.services.ingestion.pipeline import IngestionPipeline
from app.dependencies import (
    get_vector_store,
    get_embedding,
    get_ocr,
    get_audio,
)


router = APIRouter()


def _detect_file_type(filename: str) -> str:
    """根据文件名推断文件类型"""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    text_exts = {"txt", "md", "markdown", "pdf"}
    image_exts = {"png", "jpg", "jpeg", "webp", "gif", "bmp"}
    audio_exts = {"mp3", "wav", "ogg", "flac", "m4a", "aac"}

    if ext in text_exts:
        return "text"
    if ext in image_exts:
        return "image"
    if ext in audio_exts:
        return "audio"

    raise ParamError(message=f"不支持的文件格式: .{ext}")


@router.post("/api/v1/ingestion/upload")
async def upload_file(
    file: UploadFile = File(...),
    knowledge_id: str = Form(...),
    db: MetadataDB = Depends(get_metadata_db),
    fs: FileStore = Depends(get_file_store),
    vs=Depends(get_vector_store),
    embedding=Depends(get_embedding),
    ocr=Depends(get_ocr),
    audio=Depends(get_audio),
):
    """上传文件并入库"""
    # 验证知识库存在
    knowledge = db.get_knowledge(knowledge_id)
    if not knowledge:
        raise ParamError(message="知识库不存在")

    # 检测文件类型
    file_type = _detect_file_type(file.filename or "unknown")

    # 保存文件
    content = await file.read()
    file_path = await fs.save(content, file.filename or "upload")

    # 创建流水线
    pipeline = IngestionPipeline(
        vector_store=vs,
        metadata_db=db,
        file_store=fs,
        embedding_provider=embedding,
        ocr_provider=ocr,
        audio_provider=audio,
    )

    # 执行入库
    try:
        full_path = fs.get_path(file_path)
        result = await pipeline.process_file(
            file_path=full_path,
            file_name=file.filename or "upload",
            file_type=file_type,
            knowledge_id=knowledge_id,
        )

        return ApiResponse(data={
            "task_id": result.document_id,
            "status": result.status,
            "chunk_count": result.chunk_count,
        })

    except Exception as e:
        return ApiResponse(code=5001, message=str(e))


@router.get("/api/v1/ingestion/{task_id}/status")
async def get_ingestion_status(
    task_id: str,
    db: MetadataDB = Depends(get_metadata_db),
):
    """查询入库状态"""
    status = db.get_ingestion_status(task_id)
    if not status:
        raise ParamError(message="入库任务不存在")

    return ApiResponse(data=status)
