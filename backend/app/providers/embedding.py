"""千问 Embedding 适配器"""

from __future__ import annotations
import httpx
from app.providers.base import EmbeddingProvider
from app.core.config import get_settings
from app.core.exceptions import APIError


class QwenEmbedding(EmbeddingProvider):
    """千问文本向量 API 适配器"""

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.qwen_api_key
        self.api_base = settings.qwen_api_base
        self.default_model = settings.qwen_embedding_model

    async def embed(self, texts: list[str], model: str = None) -> list[list[float]]:
        url = f"{self.api_base}/services/embeddings/text-embedding/text-embedding"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model or self.default_model,
            "input": {"texts": texts},
        }

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()

            embeddings = data.get("output", {}).get("embeddings", [])
            # 按 index 排序确保顺序一致
            embeddings.sort(key=lambda x: x.get("index", 0))
            return [e.get("embedding", []) for e in embeddings]

        except httpx.HTTPStatusError as e:
            raise APIError(
                message=f"千问 Embedding API 返回错误: {e.response.status_code}",
                detail=e.response.text,
            )
        except Exception as e:
            raise APIError(message="千问 Embedding API 调用失败", detail=str(e))
