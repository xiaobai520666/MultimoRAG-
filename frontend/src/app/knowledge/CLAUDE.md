# 知识库管理页面 — frontend/src/app/knowledge/

## 模块功能

知识库的增删改查和文件上传管理界面。

## 需求边界

**属于本模块：**
- 知识库列表展示（卡片/表格）
- 创建和删除知识库
- 文件上传（拖拽 + 选择文件）
- 文件上传进度与入库状态展示
- 支持的文件类型提示

**不属于本模块：**
- 对话功能（归 chat/）
- 文件内容预览（第一版不做）

## 接口定义

调用 `services/knowledge.ts` 和 `services/ingestion.ts`

```typescript
// 页面状态
interface KnowledgePageState {
  knowledgeList: Knowledge[]
  uploadQueue: UploadTask[]
  isLoading: boolean
}

interface UploadTask {
  id: string
  fileName: string
  fileType: string
  progress: number
  status: "uploading" | "processing" | "completed" | "failed"
  error?: string
}

// 组件
interface KnowledgeCardProps { knowledge: Knowledge; onDelete: () => void }
interface UploadZoneProps { knowledgeId: string; onUpload: (file: File) => void }
interface UploadProgressProps { tasks: UploadTask[] }
```

## 依赖与约束

- 依赖 `services/knowledge.ts`、`services/ingestion.ts`
- 文件上传支持拖拽交互
- 入库状态通过轮询 `getIngestStatus` 更新