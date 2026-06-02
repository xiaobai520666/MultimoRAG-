"""模型适配层 — 抽象基类"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class LLMResult:
    content: str
    usage: dict
    finish_reason: Optional[str] = None


@dataclass
class AudioResult:
    text: str
    language: str = "zh"


class LLMProvider(ABC):
    @abstractmethod
    async def chat(
        self,
        messages: list[dict],
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResult:
        """对话补全"""
        ...


class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed(self, texts: list[str], model: str = None) -> list[list[float]]:
        """文本向量化"""
        ...


class OCRProvider(ABC):
    @abstractmethod
    async def ocr(self, image_path: str) -> str:
        """图片文字提取"""
        ...


class AudioProvider(ABC):
    @abstractmethod
    async def transcribe(self, audio_path: str) -> AudioResult:
        """音频转写"""
        ...
