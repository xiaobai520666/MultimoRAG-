"""FastAPI 依赖注入"""

from app.core.config import get_settings
from app.storage.metadata_db import MetadataDB
from app.storage.vector_store import VectorStore
from app.storage.file_store import FileStore
from app.providers.llm import DeepSeekLLM, QwenLLM
from app.providers.embedding import LocalEmbedding, QwenEmbedding
from app.providers.ocr import QwenOCR
from app.providers.audio import QwenAudio


# 单例
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


def get_llm():
    """根据配置选择 LLM 提供商"""
    global _llm
    if _llm is None:
        settings = get_settings()
        if settings.deepseek_api_key:
            _llm = DeepSeekLLM()
        elif settings.qwen_api_key:
            _llm = QwenLLM()
        else:
            _llm = DeepSeekLLM()  # 尝试默认
    return _llm


def get_embedding():
    """根据配置选择 Embedding 提供商"""
    global _embedding
    if _embedding is None:
        settings = get_settings()
        provider = settings.embedding_provider
        if provider == "qwen" and settings.qwen_api_key:
            _embedding = QwenEmbedding()
        else:
            # 默认使用本地 Embedding（无需 API Key）
            _embedding = LocalEmbedding()
    return _embedding


def get_ocr():
    """OCR 提供方（需要多模态 API Key）"""
    global _ocr
    if _ocr is None:
        _ocr = QwenOCR()
    return _ocr


def get_audio():
    """音频转写提供方（需要多模态 API Key）"""
    global _audio
    if _audio is None:
        _audio = QwenAudio()
    return _audio
