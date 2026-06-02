"""入库流水线编排"""

from __future__ import annotations
import uuid
from pathlib import Path

from app.core.config import get_settings
from app.core.models import Chunk, IngestionResult
from app.core.exceptions import InternalError
from app.services.ingestion.parser import parse_text, parse_image, parse_audio
from app.services.ingestion.chunker import chunk_text
from app.services.ingestion.embedder import embed_chunks
from app.storage.vector_store import VectorStore
from app.storage.metadata_db import MetadataDB
from app.storage.file_store import FileStore


class IngestionPipeline:
    """文件入库流水线"""

    def __init__(
        self,
        vector_store: VectorStore,
        metadata_db: MetadataDB,
        file_store: FileStore,
        embedding_provider=None,
        ocr_provider=None,
        audio_provider=None,
    ):
        self.vector_store = vector_store
        self.metadata_db = metadata_db
        self.file_store = file_store
        self.embedding_provider = embedding_provider
        self.ocr_provider = ocr_provider
        self.audio_provider = audio_provider

    async def process_file(
        self,
        file_path: str,
        file_name: str,
        file_type: str,
        knowledge_id: str,
    ) -> IngestionResult:
        """
        解析 → 分块 → 嵌入 → 入库

        Args:
            file_path: 文件路径
            file_name: 文件名
            file_type: text | image | audio
            knowledge_id: 知识库 ID

        Returns:
            IngestionResult: 入库结果
        """
        task_id = str(uuid.uuid4())

        # 记录开始
        self.metadata_db.save_ingestion_log({
            "task_id": task_id,
            "knowledge_id": knowledge_id,
            "file_name": file_name,
            "file_type": file_type,
            "status": "processing",
            "progress": 10,
        })

        try:
            # Step 1: 解析
            text = await self._parse(file_path, file_type)
            if not text or not text.strip():
                raise InternalError(message="文件内容为空或无法提取文字")

            self.metadata_db.save_ingestion_log({
                "task_id": task_id,
                "status": "processing",
                "progress": 40,
            })

            # Step 2: 分块
            settings = get_settings()
            chunks = chunk_text(text, chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap)
            if not chunks:
                raise InternalError(message="文本分块后为空")

            # 添加文档元信息
            document_id = str(uuid.uuid4())
            for chunk in chunks:
                chunk.metadata["document_id"] = document_id
                chunk.metadata["file_name"] = file_name
                chunk.metadata["file_type"] = file_type

            self.metadata_db.save_ingestion_log({
                "task_id": task_id,
                "status": "processing",
                "progress": 60,
            })

            # Step 3: 嵌入
            chunks = await embed_chunks(chunks, self.embedding_provider)

            self.metadata_db.save_ingestion_log({
                "task_id": task_id,
                "status": "processing",
                "progress": 80,
            })

            # Step 4: 入库
            await self.vector_store.add_documents(knowledge_id, chunks)

            # 更新元数据
            self.metadata_db.save_ingestion_log({
                "task_id": task_id,
                "status": "completed",
                "progress": 100,
                "chunk_count": len(chunks),
            })
            self.metadata_db.increment_document_count(knowledge_id)

            return IngestionResult(
                document_id=document_id,
                chunk_count=len(chunks),
                status="completed",
                error=None,
            )

        except Exception as e:
            self.metadata_db.save_ingestion_log({
                "task_id": task_id,
                "status": "failed",
                "progress": 0,
                "error": str(e),
            })
            raise

    async def _parse(self, file_path: str, file_type: str) -> str:
        """根据文件类型调用解析器"""
        if file_type == "text":
            return await parse_text(file_path)
        elif file_type == "image":
            return await parse_image(file_path, self.ocr_provider)
        elif file_type == "audio":
            return await parse_audio(file_path, self.audio_provider)
        else:
            raise ValueError(f"不支持的文件类型: {file_type}")
