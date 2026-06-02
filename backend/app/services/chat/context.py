"""对话上下文组装"""

from __future__ import annotations
from app.core.models import RetrievedChunk, Message


def build_prompt(
    query: str,
    chunks: list[RetrievedChunk],
    history: list[Message] = None,
) -> list[dict]:
    """
    构建 LLM messages 列表

    格式:
    - system: 角色设定 + 检索到的知识
    - history: 对话历史
    - user: 当前问题
    """
    system_message = _build_system_prompt(chunks)

    messages = [
        {"role": "system", "content": system_message},
    ]

    # 添加对话历史（最多 10 轮）
    if history:
        for msg in history[-10:]:
            messages.append({"role": msg.role, "content": msg.content})

    # 添加当前问题
    messages.append({"role": "user", "content": query})

    return messages


def _build_system_prompt(chunks: list[RetrievedChunk]) -> str:
    """构建系统提示"""
    context_parts = []

    if chunks:
        context_parts.append("根据以下知识内容回答问题：\n")
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(f"【知识片段 {i}】")
            context_parts.append(chunk.text)
            context_parts.append("")

    context_parts.append(
        "你是一个有帮助的AI助手。请基于以上知识内容回答用户问题。\n"
        "如果知识库中没有相关信息，请诚实告知用户。\n"
        "回答时使用与用户相同的语言。"
    )

    return "\n".join(context_parts)
