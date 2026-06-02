# Agent 工具 — backend/app/services/agent/

## 模块功能

提供轻量 Agent 能力，支持意图分析、工具调用与结果整合。第一期限制在安全、可控的工具集内。

## 需求边界

**属于本模块：**
- 用户意图识别（RAG 问答 vs 工具调用）
- 工具注册与调度
- 工具执行结果整合到对话回复
- 工具调用链路追踪

**不属于本模块：**
- 通用对话（归 chat/）
- 任意代码执行
- 网络请求（除非有明确工具注册）
- 系统命令执行

## 接口定义

```python
# executor.py
async def execute_agent(
    knowledge_id: str,
    message: str,
    history: list[Message] = None
) -> AgentResult:
    """Agent 主流程：分析意图 → 检索/调工具 → 整合回复"""

# tools.py
class BaseTool(ABC):
    name: str
    description: str
    
    @abstractmethod
    async def run(self, **kwargs) -> str: ...

# 第一期工具清单
class QueryRewriteTool(BaseTool):     # 查询改写
class KnowledgeSearchTool(BaseTool):  # 知识库搜索
class KnowledgeSummaryTool(BaseTool): # 知识摘要

class AgentResult:
    reply: str
    tool_calls: list[ToolCallLog]
    citations: list[Citation]

class ToolCallLog:
    tool_name: str
    input: dict
    output: str
    duration_ms: int
```

## 依赖与约束

- 依赖 `providers/llm.py` 做意图分析
- 依赖 `services/retrieval/` 做知识搜索
- 工具必须显式注册，不允许动态执行
- 第一期最多 5 个工具，后续扩展需审核