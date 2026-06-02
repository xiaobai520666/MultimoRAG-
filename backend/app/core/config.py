"""应用配置管理"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置，从 .env 文件或环境变量读取"""

    # DeepSeek API（当前使用）
    deepseek_api_key: str = ""
    deepseek_api_base: str = "https://api.deepseek.com/v1"
    deepseek_llm_model: str = "deepseek-chat"

    # 千问 API（嵌入/OCR/音频预留）
    qwen_api_key: str = ""
    qwen_api_base: str = "https://dashscope.aliyuncs.com/api/v1"
    qwen_llm_model: str = "qwen-plus"
    qwen_embedding_model: str = "text-embedding-v3"
    qwen_ocr_model: str = "qwen-vl-max"
    qwen_audio_model: str = "paraformer-realtime-v2"

    # 嵌入提供方: deepseek / qwen / local
    embedding_provider: str = "local"

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_key: str = ""

    # PostgreSQL
    postgres_dsn: str = "postgresql://multimorag:multimorag@localhost:5432/multimorag"

    # 文件存储
    upload_dir: str = "./data/uploads"

    # 服务配置
    backend_port: int = 8000
    log_level: str = "INFO"

    # 分块配置
    chunk_size: int = 500
    chunk_overlap: int = 50

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例（带缓存）"""
    return Settings()
