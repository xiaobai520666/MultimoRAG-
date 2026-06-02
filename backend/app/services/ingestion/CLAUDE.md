# 入库流水线 — backend/app/services/ingestion/

## 模块功能

负责文件从上传到向量化入库的完整流水线：解析原始文件 → 文本分块 → 向量嵌入 → 存入 Qdrant。

## 需求边界

**属于本模块：**
- 文本文件解析（TXT、Markdown、PDF）
- 图片 OCR 文字提取
- 音频文件转写
- 文本分块（按 token/段落/递归分割）
- 向量嵌入（调用 providers/embedding.py）
- 入库结果持久化（写入 Qdrant + PostgreSQL）

**不属于本模块：**
- 文件上传接收（归 api/）
- 检索与问答（归 retrieval/、chat/）
- 模型 API 实现（归 providers/）

## 接口定义

```python
# pipeline.py
async def process_file(
    file_path: str,
    file_type: str,       # "text" | "image" | "audio"
    knowledge_id: str,
    metadata: dict = None
) -> IngestResult:
    """解析 → 分块 → 嵌入 → 入库，返回入库统计"""

class IngestResult:
    document_id: str
    chunk_count: int
    status: str            # "completed" | "failed"
    error: str | None

# parser.py
async def parse_text(path: str) -> str
async def parse_image(path: str) -> str     # OCR 结果
async def parse_audio(path: str) -> str     # 转写结果

# chunker.py
def chunk_text(text: str, strategy: str = "recursive", **kwargs) -> list[Chunk]

# embedder.py
async def embed_chunks(chunks: list[Chunk]) -> list[Chunk]  # 注入向量
```

## 依赖与约束

- 依赖 `providers/ocr.py`、`providers/audio.py`、`providers/embedding.py`
- 依赖 `storage/vector_store.py` 写入 Qdrant
- 依赖 `storage/metadata_db.py` 记录入库日志
- 所有解析结果至少返回纯文本，下游不关心原始格式