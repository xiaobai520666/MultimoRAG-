"""文档解析器"""

from __future__ import annotations
from pathlib import Path


async def parse_text(file_path: str) -> str:
    """解析文本文件 (TXT/MD/PDF)"""
    ext = Path(file_path).suffix.lower()

    if ext in (".txt", ".md", ".markdown"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    if ext == ".pdf":
        # 尝试 pdfplumber，如果不可用则用 pypdf
        return _parse_pdf(file_path)

    raise ValueError(f"不支持的文本文件格式: {ext}")


def _parse_pdf(file_path: str) -> str:
    """PDF 解析"""
    try:
        import pdfplumber
        text_parts = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n\n".join(text_parts)
    except ImportError:
        pass

    # 降级使用 pypdf
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        text_parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        return "\n\n".join(text_parts)
    except ImportError:
        raise ImportError("请安装 pdfplumber 或 pypdf 以支持 PDF 解析: pip install pdfplumber pypdf")


async def parse_image(file_path: str, ocr_provider) -> str:
    """解析图片文件"""
    text = await ocr_provider.ocr(file_path)
    if not text or not text.strip():
        return ""
    return text.strip()


async def parse_audio(file_path: str, audio_provider) -> str:
    """解析音频文件"""
    result = await audio_provider.transcribe(file_path)
    return result.text
