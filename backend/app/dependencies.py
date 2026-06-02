"""FastAPI 依赖注入"""

from functools import lru_cache
from app.core.config import get_settings
from app.storage.metadata_db import MetadataDB
from app.storage.vector_store import VectorStore
from app.storage.file_store import FileStore
from app.providers.llm import QwenLLM
from app.providers.embedding import QwenEmbedding
from app.providers.ocr import QwenOCR
from app.providers.audio import QwenAudio


# 数据库单例
_metadata_db = None
_vector_store = None
_file_store = None
_llm = None
_embedding = None
_ocr = None
_audio = None


def get_metadata_db() -> MetadataDB:
    global _metadata_db
    if _metadata_db is None:
        _metadata_db = MetadataDB()
        _metadata_db.init_db()
    return _metadata_db


def get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store


def get_file_store() -> FileStore:
    global _file_store
    if _file_store is None:
        _file_store = FileStore()
    return _file_store


def get_llm() -> QwenLLM:
    global _llm
    if _llm is None:
        _llm = QwenLLM()
    return _llm


def get_embedding() -> QwenEmbedding:
    global _embedding
    if _embedding is None:
        _embedding = QwenEmbedding()
    return _embedding


def get_ocr() -> QwenOCR:
    global _ocr
    if _ocr is None:
        _ocr = QwenOCR()
    return _ocr


def get_audio() -> QwenAudio:
    global _audio
    if _audio is None:
        _audio = QwenAudio()
    return _audio
