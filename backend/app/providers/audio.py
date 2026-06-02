"""千问音频转写适配器"""

from __future__ import annotations
import httpx
from app.providers.base import AudioProvider, AudioResult
from app.core.config import get_settings
from app.core.exceptions import APIError


class QwenAudio(AudioProvider):
    """千问音频转写 API 适配器"""

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.qwen_api_key
        self.api_base = settings.qwen_api_base
        self.default_model = settings.qwen_audio_model

    async def transcribe(self, audio_path: str) -> AudioResult:
        # 读取音频文件
        with open(audio_path, "rb") as f:
            audio_data = f.read()

        url = f"{self.api_base}/services/audio/asr/transcription"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "audio/mpeg",
        }

        params = {"model": self.default_model}

        try:
            async with httpx.AsyncClient(timeout=300) as client:
                resp = await client.post(
                    url,
                    content=audio_data,
                    headers=headers,
                    params=params,
                )
                resp.raise_for_status()
                data = resp.json()

            text = data.get("output", {}).get("text", "")
            return AudioResult(text=text)

        except httpx.HTTPStatusError as e:
            raise APIError(
                message=f"千问音频 API 返回错误: {e.response.status_code}",
                detail=e.response.text,
            )
        except Exception as e:
            raise APIError(message="千问音频 API 调用失败", detail=str(e))
