"""元数据管理（PostgreSQL / SQLite 双模式）"""

from __future__ import annotations
import uuid
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

from app.core.config import get_settings
from app.storage.schemas import Base, Knowledge, IngestionLog, ChatMessage


class MetadataDB:
    """元数据管理 — 自动适配 PostgreSQL 或 SQLite"""

    def __init__(self, engine=None):
        settings = get_settings()
        if engine:
            self.engine = engine
        else:
            dsn = settings.postgres_dsn
            if dsn.startswith("sqlite:///"):
                # SQLite 本地模式（开发用）
                db_path = dsn.replace("sqlite:///", "")
                if db_path and not os.path.isabs(db_path):
                    # 确保目录存在
                    abs_dir = os.path.abspath(settings.upload_dir)
                    os.makedirs(abs_dir, exist_ok=True)
                    db_path = os.path.join(abs_dir, db_path)
                    dsn = f"sqlite:///{db_path}"
                self.engine = create_engine(
                    dsn,
                    connect_args={"check_same_thread": False},
                )
            else:
                # PostgreSQL（生产 / Docker）
                if dsn.startswith("postgresql://"):
                    dsn = dsn.replace("postgresql://", "postgresql+psycopg://", 1)
                elif dsn.startswith("postgresql+psycopg2://"):
                    dsn = dsn.replace("postgresql+psycopg2://", "postgresql+psycopg://", 1)
                self.engine = create_engine(dsn, pool_size=5, max_overflow=10)

        self.SessionLocal = sessionmaker(bind=self.engine)

    def init_db(self):
        """初始化数据库表"""
        Base.metadata.create_all(bind=self.engine)

    @contextmanager
    def session(self) -> Session:
        """会话上下文管理器"""
        db = self.SessionLocal()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def create_knowledge(self, name: str, description: str = "") -> dict:
        with self.session() as db:
            knowledge = Knowledge(id=str(uuid.uuid4()), name=name, description=description)
            db.add(knowledge)
            db.flush()
            return {
                "id": knowledge.id,
                "name": knowledge.name,
                "description": knowledge.description,
                "created_at": str(knowledge.created_at),
                "document_count": knowledge.document_count,
            }

    def get_knowledge(self, knowledge_id: str) -> dict | None:
        with self.session() as db:
            k = db.query(Knowledge).filter(Knowledge.id == knowledge_id).first()
            if not k:
                return None
            return {
                "id": k.id,
                "name": k.name,
                "description": k.description,
                "created_at": str(k.created_at),
                "document_count": k.document_count,
            }

    def list_knowledge(self, page: int = 1, size: int = 10) -> dict:
        with self.session() as db:
            total = db.query(Knowledge).count()
            items = (
                db.query(Knowledge)
                .order_by(Knowledge.created_at.desc())
                .offset((page - 1) * size)
                .limit(size)
                .all()
            )
            return {
                "items": [
                    {
                        "id": k.id,
                        "name": k.name,
                        "description": k.description,
                        "created_at": str(k.created_at),
                        "document_count": k.document_count,
                    }
                    for k in items
                ],
                "total": total,
            }

    def delete_knowledge(self, knowledge_id: str) -> bool:
        with self.session() as db:
            k = db.query(Knowledge).filter(Knowledge.id == knowledge_id).first()
            if not k:
                return False
            # 级联删除关联记录
            db.query(IngestionLog).filter(IngestionLog.knowledge_id == knowledge_id).delete()
            db.query(ChatMessage).filter(ChatMessage.knowledge_id == knowledge_id).delete()
            db.delete(k)
            return True

    def increment_document_count(self, knowledge_id: str):
        with self.session() as db:
            k = db.query(Knowledge).filter(Knowledge.id == knowledge_id).first()
            if k:
                k.document_count += 1
                db.flush()

    def save_ingestion_log(self, log: dict):
        with self.session() as db:
            existing = db.query(IngestionLog).filter(IngestionLog.task_id == log.get("task_id")).first()
            if existing:
                # 更新已有记录的字段
                for key, value in log.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                db.flush()
            else:
                # 新建记录
                if "id" not in log:
                    log["id"] = log.get("task_id") or str(uuid.uuid4())
                entry = IngestionLog(**log)
                db.add(entry)
                db.flush()

    def get_ingestion_status(self, task_id: str) -> dict | None:
        with self.session() as db:
            log = db.query(IngestionLog).filter(IngestionLog.task_id == task_id).first()
            if not log:
                return None
            return {
                "task_id": log.task_id,
                "status": log.status,
                "progress": log.progress,
                "error": log.error,
            }

    def save_message(self, knowledge_id: str, role: str, content: str) -> str | None:
        """保存对话消息（知识库不存在时静默跳过）"""
        with self.session() as db:
            # 检查 knowledge 是否存在
            k = db.query(Knowledge).filter(Knowledge.id == knowledge_id).first()
            if not k:
                return None
            msg = ChatMessage(
                id=str(uuid.uuid4()),
                knowledge_id=knowledge_id,
                role=role,
                content=content,
            )
            db.add(msg)
            db.flush()
            return msg.id

    def get_history(self, knowledge_id: str, limit: int = 20) -> list[dict]:
        with self.session() as db:
            messages = (
                db.query(ChatMessage)
                .filter(ChatMessage.knowledge_id == knowledge_id)
                .order_by(ChatMessage.created_at.desc())
                .limit(limit)
                .all()
            )
            return [
                {"role": m.role, "content": m.content, "created_at": str(m.created_at)}
                for m in reversed(messages)
            ]
