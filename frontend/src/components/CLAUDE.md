# 共享组件 — frontend/src/components/

## 模块功能

跨页面复用的 UI 组件集合。

## 目录结构

| 目录 | 组件 | 说明 |
|------|------|------|
| `Chat/` | ChatInput, MessageList, MessageBubble, CitationBlock | 对话相关 |
| `Layout/` | AppLayout, Sidebar, Header | 整体布局 |
| `common/` | Loading, EmptyState, ErrorState, Modal, Toast, Button, FileIcon | 通用组件 |

## 约束

- 组件仅负责渲染，不直接调用 API
- 需要调用 API 的场景通过 props 传入回调
- 所有组件支持 TypeScript 类型定义