# 图文URLs数组修复说明

## 问题描述

`/production/image-text` 接口保存的 `urls` 是一个数组，但发送给 `https://aicode.ltd/webhook/publich-images` 时，应该也是一个 `urls` 数组，应该和保存接口的内容一致。

## 问题分析

### 保存接口
- 接口：`POST /production/image-text`
- 参数：`urls` (数组)
- 存储：将 `urls` 数组转换为JSON字符串保存到 `media_ids` 字段

### 发送到Webhook
- Webhook URL：`https://aicode.ltd/webhook/publich-images`
- 问题：之前只发送了单个 `url` 字段，没有发送 `urls` 数组

## 修复方案

### 修改文件
- `sau_frontend/src/views/PublishCenter.vue`

### 修复内容

1. **将 `media_ids` 转换为 `urls` 数组**
   ```javascript
   // 处理 media_ids -> urls 转换（与保存接口保持一致）
   if (record.media_ids) {
     let urlsArray = []
     if (Array.isArray(record.media_ids)) {
       urlsArray = record.media_ids.filter(url => url && typeof url === 'string')
     } else if (typeof record.media_ids === 'string') {
       try {
         const parsed = JSON.parse(record.media_ids)
         if (Array.isArray(parsed)) {
           urlsArray = parsed.filter(url => url && typeof url === 'string')
         } else {
           urlsArray = [record.media_ids]
         }
       } catch (e) {
         urlsArray = [record.media_ids]
       }
     }
     
     // 将 media_ids 转换为 urls 数组（与保存接口保持一致）
     if (urlsArray.length > 0) {
       requestBody.urls = urlsArray
       delete requestBody.media_ids  // 删除 media_ids 字段
     }
   }
   ```

2. **保留 `url` 字段作为兼容**（用于单图场景）
   - 取 `urls` 数组的第一个URL作为 `url` 字段

### 发送到Webhook的数据格式

修复后，发送到 `https://aicode.ltd/webhook/publich-images` 的数据格式：

```json
{
  "id": 14,
  "title": "标题",
  "content": "内容",
  "urls": [
    "https://example.com/image1.png",
    "https://example.com/image2.png",
    "https://example.com/image3.png"
  ],
  "url": "https://example.com/image1.png",  // 兼容字段，取第一个URL
  "record_id": 14,
  "platform": "小红书",
  "content_type": "image-text"
}
```

## 验证

### 保存接口
- ✅ 接收 `urls` 数组
- ✅ 保存到 `media_ids` 字段（JSON字符串）

### 发送到Webhook
- ✅ 从 `media_ids` 解析出 `urls` 数组
- ✅ 发送 `urls` 数组到webhook
- ✅ 与保存接口的数据格式一致

## 注意事项

1. **兼容性**：保留了 `url` 字段（取第一个URL），用于兼容可能需要单图URL的场景
2. **数据一致性**：`urls` 数组与保存接口的 `urls` 参数完全一致
3. **字段清理**：发送到webhook时，删除了 `media_ids` 字段，使用 `urls` 替代

## 相关文件

- `sau_frontend/src/views/PublishCenter.vue` - 发布中心组件
- `sau_backend.py` - 后端API（`/production/image-text`）


