# 模型适配层 — backend/app/providers/

## 模块功能

所有外部模型 API 的统一适配层。使用适配器模式封装 LLM、Embedding、OCR、音频转写调用，上层业务代码不直接依赖任何具体 API 供应商。

## 需求边界

**属于本模块：**
- LLM 对话/补全 API 适配（千问 API）
- 文本向量嵌入 API 适配
- 图片 OCR 文字提取 API 适配
- 音频转写 API 适配
- 供应商切换机制（通过配置切换实现）

**不属于本模块：**
- Prompt 构建与对话编排（归 chat/）
- 文档解析逻辑（归 ingestion/）
- API 密钥管理（归 core/config.py）

## 接口定义

```python
# base.py
class LLMProvider(ABC):
    @abstractmethod
    async def chat(self, messages: list[dict], **kwargs) -> LLMResult: ...

class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]: ...

class OCRProvider(ABC):
    @abstractmethod
    async def ocr(self, image_path: str) -> str: ...

class AudioProvider(ABC):
    @abstractmethod
    async def transcribe(self, audio_path: str) -> str: ...

# llm.py — 千问实现
class QwenLLM(LLMProvider):
    async def chat(self, messages, **kwargs) -> LLMResult: ...

# embedding.py — 千问实现
class QwenEmbedding(EmbeddingProvider):
    async def embed(self, texts) -> list[list[float]]: ...

# ocr.py — 千问实现
class QwenOCR(OCRProvider):
    async def ocr(self, image_path) -> str: ...

# audio.py — 千问实现
class QwenAudio(AudioProvider):
    async def transcribe(self, audio_path) -> str: ...

class LLMResult:
    content: str
    usage: dict
    finish_reason: str
```

## 依赖与约束

- 依赖 `core/config.py` 获取 API 密钥和端点
- 所有供应商实现必须继承 `base.py` 中的抽象基类
- 不允许业务代码直接 import 具体供应商类，必须通过工厂函数获取实例
- 新增供应商只需实现抽象基类，修改配置即可切换