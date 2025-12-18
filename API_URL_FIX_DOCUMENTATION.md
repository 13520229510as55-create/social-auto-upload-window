# API URL 重复前缀问题修复文档

## 问题描述

在访问 `https://yutt.xyz/api/api/production/records` 时出现 404 错误，原因是 URL 中出现了重复的 `/api/api/` 前缀。

## 根本原因

多个组件和工具文件中都实现了各自的 `resolveApiBaseUrl` 函数，逻辑不一致，导致在某些情况下会重复添加 `/api` 前缀。

## 解决方案

### 1. 创建统一的工具函数

创建了 `sau_frontend/src/utils/apiConfig.js`，提供统一的 API URL 解析逻辑：

- `resolveApiBaseUrl()`: 解析 API 基础 URL，自动处理各种场景
- `buildApiUrl(path)`: 构建完整的 API URL
- `getApiPathPrefix()`: 获取 API 路径前缀

### 2. 统一规则

工具函数遵循以下统一规则：

1. **yutt.xyz 域名**：强制使用 `/api`（相对路径）
2. **localhost/127.0.0.1**：忽略环境变量，使用 `/api`（相对路径）
3. **其他情况**：根据环境变量决定
4. **自动检测**：避免重复添加 `/api` 前缀

### 3. 更新的文件

以下文件已更新为使用统一的工具函数：

- ✅ `sau_frontend/src/views/ProductionCenter.vue`
- ✅ `sau_frontend/src/views/PublishCenter.vue`
- ✅ `sau_frontend/src/views/HotspotCenter.vue`
- ✅ `sau_frontend/src/views/AccountManagement.vue` (包括 SSE 连接部分)
- ✅ `sau_frontend/src/utils/request.js`
- ✅ `sau_frontend/src/views/request.js` (已修复)
- ✅ `sau_frontend/src/api/material.js`
- ✅ `sau_frontend/src/views/material.js`

### 4. 关键修复点

**最重要**：对于 yutt.xyz 域名，无论环境变量如何设置，都强制返回 `/api`（相对路径）。这确保了：
- 即使 `VITE_API_BASE_URL=https://yutt.xyz/api`，也会返回 `/api`
- 避免了环境变量导致的重复 `/api` 问题
- 所有直接使用环境变量构建 API URL 的地方都已替换为使用 `@/utils/apiConfig` 中的工具函数

## 使用方法

### 在 Vue 组件中使用

```javascript
import { resolveApiBaseUrl, buildApiUrl } from '@/utils/apiConfig'

// 获取 API 基础 URL
const apiBaseUrl = resolveApiBaseUrl()

// 构建完整的 API URL
const url = buildApiUrl('/production/records')
```

### 在工具函数中使用

```javascript
import { buildApiUrl } from '@/utils/apiConfig'

// 构建下载 URL
const downloadUrl = buildApiUrl(`/download/${filePath}`)
```

## 测试验证

### 正确的 URL 格式

- ✅ `https://yutt.xyz/api/production/records` - 正确
- ❌ `https://yutt.xyz/api/api/production/records` - 错误（已修复）

### 测试命令

```bash
# 测试 API 端点
curl 'https://yutt.xyz/api/production/records' \
  -H 'Accept: application/json'

# 应该返回 200 状态码和 JSON 数据
```

## 预防措施

### 1. 禁止直接实现 API URL 解析逻辑

**❌ 不要这样做：**
```javascript
// 错误：不要在每个组件中重复实现
const resolveApiBaseUrl = () => {
  const API_PATH_PREFIX = import.meta.env.VITE_API_PATH_PREFIX || '/api'
  let API_BASE_URL = import.meta.env.VITE_API_BASE_URL
  // ... 重复的逻辑
}
```

**✅ 应该这样做：**
```javascript
// 正确：使用统一的工具函数
import { resolveApiBaseUrl } from '@/utils/apiConfig'
const apiBaseUrl = resolveApiBaseUrl()
```

### 2. 代码审查检查清单

在代码审查时，检查以下内容：

- [ ] 是否直接使用了 `import.meta.env.VITE_API_BASE_URL` 或 `VITE_API_PATH_PREFIX`？
- [ ] 是否有自定义的 `resolveApiBaseUrl` 函数？
- [ ] 是否手动拼接了 `/api` 前缀？
- [ ] 是否使用了 `@/utils/apiConfig` 中的工具函数？

### 3. ESLint 规则建议

可以考虑添加 ESLint 规则，禁止直接使用环境变量构建 API URL：

```javascript
// .eslintrc.js
rules: {
  'no-restricted-imports': [
    'error',
    {
      paths: [
        {
          name: 'import.meta.env',
          importNames: ['VITE_API_BASE_URL', 'VITE_API_PATH_PREFIX'],
          message: '请使用 @/utils/apiConfig 中的工具函数来构建 API URL'
        }
      ]
    }
  ]
}
```

## 相关文件

- 工具函数：`sau_frontend/src/utils/apiConfig.js`
- 后端路由：`sau_backend.py` (路由定义在 `/production/records`)
- Nginx 配置：`/etc/nginx/sites-available/yutt.xyz` (代理 `/api/` 到后端)

## 更新日期

2025-12-05

