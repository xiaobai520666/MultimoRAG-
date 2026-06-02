"""嵌入适配器（DeepSeek + 本地兜底 + Qwen 预留）"""

from __future__ import annotations
import hashlib
import re
import httpx
from app.providers.base import EmbeddingProvider
from app.core.config import get_settings
from app.core.exceptions import APIError

# 向量维度
DIMENSION = 1024


class LocalEmbedding(EmbeddingProvider):
    """
    本地简易嵌入实现（无需 API Key）

    基于 TF-IDF 词频统计 + 哈希投影到 1024 维向量。
    检索效果不如专业 Embedding API，但足以跑通全流程。
    后期替换为真实 Embedding API 即可。
    """

    def __init__(self):
        # 常见中文短语种子列表（用于词频向量）
        self._seed_chars = (
            "人工智能机器学习深度学习自然语言处理神经网络大模型"
            "计算机科学技术工程数据信息知识"
            "中国北京市上海深圳广州杭州成都南京武汉"
            "PythonJavaScriptJavaGoRustCppTypeScript"
            "数据库查询分析检索问答对话生成理解"
            "安全隐私保护性能优化部署运维测试"
            "abcdefghijklmnopqrstuvwxyz0123456789"
        )

    async def embed(self, texts: list[str], model: str = None) -> list[list[float]]:
        result = []
        for text in texts:
            vec = self._text_to_vec(text)
            result.append(vec)
        return result

    def _text_to_vec(self, text: str) -> list[float]:
        """基于字符/词频 + 哈希投影生成 1024 维向量"""
        text = text.lower()

        # 统计字符频率
        freq = {}
        # 单字
        for ch in text:
            freq[ch] = freq.get(ch, 0) + 1
        # 双字组合
        for i in range(len(text) - 1):
            bigram = text[i:i + 2]
            freq[bigram] = freq.get(bigram, 0) + 1

        # 投影到 1024 维
        vec = [0.0] * DIMENSION
        for token, count in freq.items():
            # 用 SHA256 哈希确定 token 对应的维度位置
            h = hashlib.sha256(token.encode()).digest()
            for j in range(8):
                idx = int.from_bytes(h[j * 4:(j + 1) * 4], 'big') % DIMENSION
                vec[idx] += count * 0.01  # 归一化系数

        # L2 归一化
        norm = sum(v * v for v in vec) ** 0.5
        if norm > 0:
            vec = [v / norm for v in vec]

        return vec


class DeepSeekEmbedding(EmbeddingProvider):
    """
    DeepSeek Embedding（通过 LLM chat 接口模拟）

    注意：DeepSeek 目前无专用 Embedding API，此实现从 LLM 回复
    中提取关键字频率作为近似向量，仅供演示。
    """

    def __init__(self, llm=None):
        self.llm = llm

    async def embed(self, texts: list[str], model: str = None) -> list[list[float]]:
        if not self.llm:
            # 降级到本地 Embedding
            local = LocalEmbedding()
            return await local.embed(texts)

        result = []
        for text in texts:
            # 让 LLM 提取关键词
            try:
                messages = [
                    {"role": "system", "content": "提取文本中的10个核心关键词，用逗号分隔。只返回关键词。"},
                    {"role": "user", "content": text[:500]},
                ]
                llm_result = await self.llm.chat(messages, max_tokens=100, temperature=0.1)
                keywords = llm_result.content

                # 用关键词 + 原文做本地嵌入
                combined = f"{text} {keywords}"
                local = LocalEmbedding()
                vecs = await local.embed([combined])
                result.append(vecs[0])
            except Exception:
                local = LocalEmbedding()
                vecs = await local.embed([text])
                result.append(vecs[0])

        return result


# 旧版 QwenEmbedding 保留
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
            embeddings.sort(key=lambda x: x.get("index", 0))
            return [e.get("embedding", []) for e in embeddings]
        except Exception as e:
            raise APIError(message="千问 Embedding API 调用失败", detail=str(e))
