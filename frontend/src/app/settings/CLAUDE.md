# 设置页面 — frontend/src/app/settings/

## 模块功能

系统设置管理界面，配置 API 连接参数和应用偏好。

## 需求边界

**属于本模块：**
- API 密钥配置（千问 API Key）
- API 端点地址配置
- 模型参数调整（top_k、temperature）
- 语言首选项
- 配置本地持久化（localStorage）

**不属于本模块：**
- 用户认证（第一版个人使用，不做登录）
- 多用户偏好

## 接口定义

```typescript
// 设置模型
interface AppSettings {
  apiKey: string
  apiBaseUrl: string
  modelName: string
  temperature: number
  topK: number
  language: "zh" | "en"
}

interface SettingsPageState {
  settings: AppSettings
  isDirty: boolean
  isSaved: boolean
}

// 组件
interface SettingFieldProps { label: string; value: any; onChange: (v: any) => void }
```

## 依赖与约束

- 设置存储在 localStorage 中
- 页面加载时读取 localStorage 初始化
- 变更后自动保存或手动点击保存
- 不依赖后端任何接口