# 核心基础设施 — backend/app/core/

## 模块功能

提供后端运行的基础设施：配置管理、数据模型定义、异常体系。不包含业务逻辑，所有模块依赖本模块。

## 需求边界

**属于本模块：**
- 环境变量读取与配置对象
- Pydantic 数据模型（请求/响应/内部 DTO）
- 自定义异常体系与错误码
- 日志配置
- 通用工具函数

**不属于本模块：**
- 业务逻辑
- API 路由
- 外部 API 调用

## 接口定义

```python
# config.py
class Settings(BaseSettings):
    qwen_api_key: str
    qwen_api_base: str = "https://dashscope.aliyuncs.com/api/v1"
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_key: str = ""
    postgres_dsn: str = "postgresql://user:pass@localhost:5432/multimorag"
    upload_dir: str = "./data/uploads"
    backend_port: int = 8000
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"

def get_settings() -> Settings: ...

# exceptions.py
class AppException(Exception):
    code: int
    message: str
    detail: str | None

class NotFoundError(AppException):      # code=4004
class ParamError(AppException):         # code=4001
class InternalError(AppException):      # code=5001
class APIError(AppException):           # code=5002

# models.py — Pydantic 数据模型
# 请求
class ChatRequest(BaseModel): ...
class CreateKnowledgeRequest(BaseModel): ...
class SearchRequest(BaseModel): ...
# 响应
class ApiResponse(BaseModel, Generic[T]): ...
class ChatResponse(BaseModel): ...
# 内部 DTO
class Message(BaseModel): ...
class Chunk(BaseModel): ...
class RetrievedChunk(BaseModel): ...
class Citation(BaseModel): ...
```

## 依赖与约束

- 零业务依赖，只依赖 pydantic、pydantic-settings 等基础设施库
- 所有模块都通过 `from app.core import ...` 引用本模块
- 日志配置统一在本模块完成