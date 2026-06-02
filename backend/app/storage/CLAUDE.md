# 存储层 — backend/app/storage/

## 模块功能

统一封装所有数据存储操作，包括向量存储（Qdrant）、关系型数据库（PostgreSQL）和文件存储。业务代码不直接操作存储客户端，全部通过本模块访问。

## 需求边界

**属于本模块：**
- Qdrant 向量库的增删改查封装
- PostgreSQL 中元数据、对话记录、入库日志的管理
- 上传文件与派生文件的磁盘存储抽象
- 数据库模型定义（SQLAlchemy ORM）
- 连接管理与会话生命周期

**不属于本模块：**
- 向量嵌入计算（归 providers/embedding.py）
- 检索逻辑（归 services/retrieval/）
- 文件解析（归 services/ingestion/）

## 接口定义

```python
# vector_store.py
class VectorStore:
    async def add_documents(self, knowledge_id: str, chunks: list[Chunk]) -> None
    async def similarity_search(self, knowledge_id: str, query_embedding: list[float], top_k: int) -> list[RetrievedChunk]
    async def delete_documents(self, knowledge_id: str) -> None
    async def delete_collection(self, knowledge_id: str) -> None

# metadata_db.py
class MetadataDB:
    async def create_knowledge(self, name: str, description: str) -> Knowledge
    async def get_knowledge(self, id: str) -> Knowledge | None
    async def list_knowledge(self, page: int, size: int) -> PageResult[Knowledge]
    async def delete_knowledge(self, id: str) -> None
    async def save_message(self, knowledge_id: str, role: str, content: str) -> Message
    async def get_history(self, knowledge_id: str, limit: int) -> list[Message]
    async def save_ingestion_log(self, log: IngestionLog) -> None
    async def get_ingestion_status(self, task_id: str) -> IngestionLog | None

# file_store.py
class FileStore:
    async def save(self, file: UploadFile, subdir: str = "") -> str  # 返回路径
    async def delete(self, path: str) -> None
    async def get_path(self, relative_path: str) -> str              # 返回绝对路径
```

## 依赖与约束

- VectorStore 只依赖 Qdrant Python SDK
- MetadataDB 只依赖 SQLAlchemy + PostgreSQL
- FileStore 只依赖本地文件系统
- 跨存储的操作（如删除知识库时同时清理向量和元数据）由调用方编排