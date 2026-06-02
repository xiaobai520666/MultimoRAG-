"""PostgreSQL 元数据管理"""

from __future__ import annotations
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

from app.core.config import get_settings
from app.storage.schemas import Base, Knowledge, IngestionLog, ChatMessage


class MetadataDB:
    """PostgreSQL 元数据管理"""

    def __init__(self, engine=None):
        settings = get_settings()
        if engine:
            self.engine = engine
        else:
            self.engine = create_engine(settings.postgres_dsn, pool_size=5, max_overflow=10)

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

    def save_message(self, knowledge_id: str, role: str, content: str) -> str:
        with self.session() as db:
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
