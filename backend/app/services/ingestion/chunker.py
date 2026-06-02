"""文本分块策略"""

from __future__ import annotations
from app.core.models import Chunk


def chunk_text(
    text: str,
    strategy: str = "recursive",
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    **kwargs,
) -> list[Chunk]:
    """文本分块"""
    if not text or not text.strip():
        return []

    if strategy == "recursive":
        return _recursive_chunk(text, chunk_size, chunk_overlap)
    elif strategy == "paragraph":
        return _paragraph_chunk(text, chunk_size, chunk_overlap)
    else:
        return _recursive_chunk(text, chunk_size, chunk_overlap)


def _recursive_chunk(text: str, chunk_size: int, overlap: int) -> list[Chunk]:
    """递归分块：按段落/句子边界切分"""
    chunks = []
    # 先按双换行分段
    paragraphs = text.split("\n\n")

    current = ""
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # 如果当前块 + 新段落不超过限制，继续追加
        if len(current) + len(para) + 2 <= chunk_size:
            if current:
                current += "\n\n" + para
            else:
                current = para
        else:
            # 保存当前块
            if current:
                chunks.append(Chunk(text=current, metadata={}))
            # 新段落如果太长，继续按句子切
            if len(para) > chunk_size:
                sentences = _split_by_sentence(para, chunk_size)
                for s in sentences:
                    chunks.append(Chunk(text=s, metadata={}))
                current = ""
            else:
                current = para

    if current:
        chunks.append(Chunk(text=current, metadata={}))

    return chunks


def _paragraph_chunk(text: str, chunk_size: int, overlap: int) -> list[Chunk]:
    """按段落分块"""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 2 <= chunk_size:
            if current:
                current += "\n\n" + para
            else:
                current = para
        else:
            if current:
                chunks.append(Chunk(text=current, metadata={}))
            current = para

    if current:
        chunks.append(Chunk(text=current, metadata={}))

    return chunks


def _split_by_sentence(text: str, max_len: int) -> list[str]:
    """按句子切分超长文本"""
    sentences = []
    current = ""

    for char in text:
        current += char
        if char in "。！？.!?\n":
            sentences.append(current.strip())
            current = ""

    if current.strip():
        sentences.append(current.strip())

    # 合并短句子到接近 max_len 的块
    chunks = []
    current_chunk = ""
    for s in sentences:
        if len(current_chunk) + len(s) <= max_len:
            if current_chunk:
                current_chunk += s
            else:
                current_chunk = s
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = s

    if current_chunk:
        chunks.append(current_chunk)

    return chunks
