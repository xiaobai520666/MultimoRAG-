"""Agent 安全工具集"""

from __future__ import annotations
from abc import ABC, abstractmethod


class BaseTool(ABC):
    """工具基类"""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def description(self) -> str: ...

    @abstractmethod
    async def run(self, **kwargs) -> str: ...


class QueryRewriteTool(BaseTool):
    """查询改写工具"""

    @property
    def name(self) -> str:
        return "query_rewrite"

    @property
    def description(self) -> str:
        return "将用户问题改写为更适合检索的形式"

    async def run(self, query: str, llm=None, **kwargs) -> str:
        if not llm:
            return query

        messages = [
            {
                "role": "system",
                "content": (
                    "你是一个查询改写助手。将用户的问题改写成更适合向量检索的形式。"
                    "保留核心关键词，去除口语化表达。直接返回改写后的查询，不要解释。"
                ),
            },
            {"role": "user", "content": query},
        ]

        result = await llm.chat(messages, max_tokens=100, temperature=0.3)
        return result.content.strip()


class KnowledgeSearchTool(BaseTool):
    """知识库搜索工具"""

    def __init__(self, retriever=None):
        self._retriever = retriever

    @property
    def name(self) -> str:
        return "knowledge_search"

    @property
    def description(self) -> str:
        return "在指定知识库中搜索相关内容"

    async def run(
        self,
        query: str,
        knowledge_id: str = None,
        retriever=None,
        **kwargs,
    ) -> str:
        if not retriever:
            return "检索器未初始化"

        chunks = await retriever.retrieve(
            knowledge_id=knowledge_id or "",
            query=query,
            top_k=3,
        )

        if not chunks:
            return "未找到相关内容"

        parts = []
        for i, c in enumerate(chunks, 1):
            parts.append(f"【{i}】{c.text}")

        return "\n\n".join(parts)


class KnowledgeSummaryTool(BaseTool):
    """知识摘要工具"""

    def __init__(self, retriever=None, llm=None):
        self._retriever = retriever
        self._llm = llm

    @property
    def name(self) -> str:
        return "knowledge_summary"

    @property
    def description(self) -> str:
        return "对搜索结果或知识库内容生成摘要"

    async def run(
        self,
        text: str = None,
        knowledge_id: str = None,
        query: str = None,
        **kwargs,
    ) -> str:
        content = text

        # 如果提供了 knowledge_id 和 query，先检索
        if knowledge_id and query and self._retriever:
            chunks = await self._retriever.retrieve(
                knowledge_id=knowledge_id,
                query=query,
                top_k=5,
            )
            content = "\n\n".join([c.text for c in chunks])

        if not content:
            return "没有可摘要的内容"

        # 用 LLM 生成摘要
        if self._llm:
            messages = [
                {
                    "role": "system",
                    "content": "你是一个内容摘要助手。请用简洁的语言总结以下内容。",
                },
                {"role": "user", "content": f"请总结以下内容：\n\n{content[:2000]}"},
            ]
            result = await self._llm.chat(messages, max_tokens=500)
            return result.content

        return content[:500]
