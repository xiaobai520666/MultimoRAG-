"""SQLAlchemy 数据模型"""

from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    DateTime,
    ForeignKey,
    Float,
    func,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Knowledge(Base):
    __tablename__ = "knowledge"

    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, default="")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    document_count = Column(Integer, default=0)


class IngestionLog(Base):
    __tablename__ = "ingestion_logs"

    id = Column(String(36), primary_key=True)
    task_id = Column(String(36), unique=True, nullable=False)
    knowledge_id = Column(String(36), ForeignKey("knowledge.id"))
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50))  # text | image | audio
    status = Column(String(20), default="uploading")
    progress = Column(Integer, default=0)
    chunk_count = Column(Integer, default=0)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True)
    knowledge_id = Column(String(36), ForeignKey("knowledge.id"))
    role = Column(String(20), nullable=False)  # user | assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
