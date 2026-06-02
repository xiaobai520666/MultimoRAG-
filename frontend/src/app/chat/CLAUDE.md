# 对话页面 — frontend/src/app/chat/

## 模块功能

主对话界面，用户在此与知识库进行 RAG 问答交互和 Agent 对话。

## 需求边界

**属于本模块：**
- 消息发送与流式响应展示
- 对话历史列表
- 知识库选择器
- 引用来源展示（可点击查看原文块）
- Agent 工具调用日志展示（非侵入式）
- 空状态、加载态、错误态处理

**不属于本模块：**
- 文件上传管理（归 knowledge/）
- 系统设置（归 settings/）

## 接口定义

调用 `services/chat.ts` 和 `services/knowledge.ts`

```typescript
// 页面状态
interface ChatPageState {
  messages: Message[]
  selectedKnowledge: Knowledge | null
  knowledgeList: Knowledge[]
  isLoading: boolean
}

// 组件属性
interface MessageListProps { messages: Message[] }
interface MessageBubbleProps { message: Message }
interface CitationPreviewProps { citation: Citation }
interface KnowledgeSelectorProps { list: Knowledge[]; selected: string; onChange: (id: string) => void }
```

## 依赖与约束

- 依赖 `services/chat.ts`、`services/knowledge.ts`
- 依赖共享组件 `components/Chat/`、`components/common/`
- 知识库选择器复用 knowledge 模块的数据