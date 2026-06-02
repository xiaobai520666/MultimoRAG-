"""Agent 执行器"""

from __future__ import annotations
import time
from app.core.models import (
    AgentRequest,
    AgentResponse,
    CitationItem,
    ToolCallLog,
    Message,
)
from app.services.retrieval.retriever import Retriever
from app.services.agent.tools import (
    QueryRewriteTool,
    KnowledgeSearchTool,
    KnowledgeSummaryTool,
)
from app.providers.llm import LLMProvider


class AgentExecutor:
    """Agent 执行器"""

    def __init__(
        self,
        retriever: Retriever,
        llm: LLMProvider,
    ):
        self.retriever = retriever
        self.llm = llm
        self.tools = self._register_tools()

    def _register_tools(self) -> dict:
        """注册可用工具"""
        return {
            "query_rewrite": QueryRewriteTool(),
            "knowledge_search": KnowledgeSearchTool(self.retriever),
            "knowledge_summary": KnowledgeSummaryTool(self.retriever, self.llm),
        }

    async def execute_agent(self, request: AgentRequest) -> AgentResponse:
        """
        Agent 主流程：分析意图 → 选择工具 → 执行 → 整合回复
        """
        tool_calls_log = []

        # Step 1: 分析意图，决定是否使用工具
        intent = await self._analyze_intent(request.message)

        if intent.get("use_tool"):
            # Step 2: 调用工具
            tool_name = intent.get("tool_name", "knowledge_search")
            tool = self.tools.get(tool_name)

            if tool:
                start = time.time()
                tool_input = {"query": request.message}
                tool_output = await tool.run(
                    llm=self.llm,
                    retriever=self.retriever,
                    **tool_input,
                )
                duration = int((time.time() - start) * 1000)

                tool_calls_log.append(
                    ToolCallLog(
                        tool_name=tool_name,
                        input=tool_input,
                        output=tool_output[:500],  # 截断输出
                        duration_ms=duration,
                    )
                )

                # Step 3: 整合回复
                reply = await self._synthesize_reply(
                    request.message, tool_output
                )
            else:
                reply = await self._direct_reply(request.message)
        else:
            reply = await self._direct_reply(request.message)

        # Step 4: 检索相关引用
        chunks = await self.retriever.retrieve(
            knowledge_id=request.knowledge_id,
            query=request.message,
            top_k=3,
        )
        citations = [
            CitationItem(
                chunk_id=c.chunk_id,
                document_id=c.document_id,
                text=c.text[:200],
                score=c.score,
            )
            for c in chunks
        ]

        return AgentResponse(
            reply=reply,
            tool_calls=tool_calls_log,
            citations=citations,
        )

    async def _analyze_intent(self, message: str) -> dict:
        """分析用户意图"""
        messages = [
            {
                "role": "system",
                "content": (
                    "你是一个意图分析助手。分析用户问题，决定是否需要使用工具。\n"
                    "如果是简单的知识查询，返回 use_tool: true, tool_name: knowledge_search。\n"
                    "如果需要改写查询，返回 use_tool: true, tool_name: query_rewrite。\n"
                    "如果需要生成摘要，返回 use_tool: true, tool_name: knowledge_summary。\n"
                    "否则返回 use_tool: false。\n"
                    "以 JSON 格式返回，不要多余文字。"
                ),
            },
            {"role": "user", "content": message},
        ]

        result = await self.llm.chat(messages, max_tokens=200, temperature=0.1)

        import json
        try:
            return json.loads(result.content.strip())
        except (json.JSONDecodeError, ValueError):
            return {"use_tool": True, "tool_name": "knowledge_search"}

    async def _direct_reply(self, message: str) -> str:
        """直接调用 LLM 回复"""
        messages = [
            {
                "role": "system",
                "content": "你是一个有帮助的 AI 助手。",
            },
            {"role": "user", "content": message},
        ]
        result = await self.llm.chat(messages)
        return result.content

    async def _synthesize_reply(self, original: str, tool_output: str) -> str:
        """整合工具输出为回复"""
        messages = [
            {
                "role": "system",
                "content": (
                    "你是一个 AI 助手。基于以下工具返回的信息，给用户一个完整、清晰的回答。"
                ),
            },
            {"role": "user", "content": f"原始问题：{original}\n\n工具返回：{tool_output}"},
        ]
        result = await self.llm.chat(messages)
        return result.content
