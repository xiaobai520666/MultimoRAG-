"""DeepSeek LLM 适配器（千问作为可选后备）"""

from __future__ import annotations
import httpx
from app.providers.base import LLMProvider, LLMResult
from app.core.config import get_settings
from app.core.exceptions import APIError


class DeepSeekLLM(LLMProvider):
    """DeepSeek API 适配器（OpenAI 兼容接口）"""

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.deepseek_api_key
        self.api_base = settings.deepseek_api_base

    async def chat(
        self,
        messages: list[dict],
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResult:
        url = f"{self.api_base}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()

            choice = data.get("choices", [{}])[0]
            message = choice.get("message", {})
            usage = data.get("usage", {})

            return LLMResult(
                content=message.get("content", ""),
                usage=usage,
                finish_reason=choice.get("finish_reason"),
            )
        except httpx.HTTPStatusError as e:
            raise APIError(
                message=f"DeepSeek API 返回错误: {e.response.status_code}",
                detail=e.response.text,
            )
        except Exception as e:
            raise APIError(message="DeepSeek API 调用失败", detail=str(e))


# 旧版 QwenLLM 保留作为备用
class QwenLLM(LLMProvider):
    """千问 LLM API 适配器（后备）"""

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.qwen_api_key
        self.api_base = settings.qwen_api_base
        self.default_model = settings.qwen_llm_model

    async def chat(
        self,
        messages: list[dict],
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResult:
        url = f"{self.api_base}/services/aigc/text-generation/chat"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()

            choice = data.get("choices", [{}])[0]
            message = choice.get("message", {})
            usage = data.get("usage", {})

            return LLMResult(
                content=message.get("content", ""),
                usage=usage,
                finish_reason=choice.get("finish_reason"),
            )
        except httpx.HTTPStatusError as e:
            raise APIError(
                message=f"千问 API 返回错误: {e.response.status_code}",
                detail=e.response.text,
            )
        except Exception as e:
            raise APIError(message="千问 API 调用失败", detail=str(e))
