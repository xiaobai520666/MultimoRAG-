"""千问 OCR 适配器"""

from __future__ import annotations
import base64
import httpx
from app.providers.base import OCRProvider
from app.core.config import get_settings
from app.core.exceptions import APIError


class QwenOCR(OCRProvider):
    """千问视觉模型 OCR 适配器"""

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.qwen_api_key
        self.api_base = settings.qwen_api_base
        self.default_model = settings.qwen_ocr_model

    async def ocr(self, image_path: str) -> str:
        # 读取图片并转 base64
        with open(image_path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode("utf-8")

        url = f"{self.api_base}/services/aigc/multimodal-generation/generation"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # 判断图片格式
        ext = image_path.rsplit(".", 1)[-1].lower()
        mime = f"image/{ext}" if ext in ("png", "jpeg", "jpg", "webp", "gif") else "image/jpeg"

        payload = {
            "model": self.default_model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "image": f"data:{mime};base64,{image_b64}",
                        },
                        {"text": "请提取图片中的所有文字，只返回文字内容。"},
                    ],
                }
            ],
        }

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()

            choices = data.get("output", {}).get("choices", [])
            if not choices:
                return ""

            content = choices[0].get("message", {}).get("content", [])
            text_parts = []
            for item in content:
                if isinstance(item, dict) and "text" in item:
                    text_parts.append(item["text"])

            return " ".join(text_parts)

        except httpx.HTTPStatusError as e:
            raise APIError(
                message=f"千问 OCR API 返回错误: {e.response.status_code}",
                detail=e.response.text,
            )
        except Exception as e:
            raise APIError(message="千问 OCR API 调用失败", detail=str(e))
