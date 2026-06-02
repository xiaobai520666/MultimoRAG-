"""文件存储抽象"""

from __future__ import annotations
import os
import uuid
import shutil
from pathlib import Path

from app.core.config import get_settings


class FileStore:
    """本地文件存储抽象"""

    def __init__(self, base_dir: str = None):
        settings = get_settings()
        self.base_dir = Path(base_dir or settings.upload_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def save(self, file_content: bytes, original_name: str, subdir: str = "") -> str:
        """保存文件并返回相对路径"""
        ext = Path(original_name).suffix or ".bin"
        filename = f"{uuid.uuid4()}{ext}"

        target_dir = self.base_dir / subdir if subdir else self.base_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        target_path = target_dir / filename
        with open(target_path, "wb") as f:
            f.write(file_content)

        return str(target_path.relative_to(self.base_dir))

    async def delete(self, relative_path: str) -> None:
        """删除文件"""
        full_path = self.base_dir / relative_path
        if full_path.exists():
            full_path.unlink()

    def get_path(self, relative_path: str) -> str:
        """获取文件绝对路径"""
        return str(self.base_dir / relative_path)

    async def get_size(self, relative_path: str) -> int:
        """获取文件大小"""
        full_path = self.base_dir / relative_path
        if full_path.exists():
            return full_path.stat().st_size
        return 0
