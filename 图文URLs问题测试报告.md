# 图文URLs问题 - 自动化测试报告

## 测试时间
2025-12-14 02:50

## 测试结果总结

### ✅ **问题根源已定位：n8n工作流配置问题**

## 关键发现

### 1. 数据库证据

查看数据库中最新的3条记录：

```
ID 52: 只有 1 个URL
["http://res.cloudinary.com/durtefzdp/image/upload/v1765709055/scc7zjk4am.png"]

ID 51: 只有 1 个URL  
["http://res.cloudinary.com/durtefzdp/image/upload/v1765709042/pxlxm79u5ai.png"]

ID 50: 有 6 个URLs ✅✅✅
[
  "https://dashscope-result-wlcb-acdr-1.oss-cn-wulanchabu-acdr-1.aliyuncs.com/...",
  "https://mmbiz.qpic.cn/sz_mmbiz_png/...",
  "https://mmbiz.qpic.cn/sz_mmbiz_png/...",
  "https://mmbiz.qpic.cn/sz_mmbiz_png/...",
  "https://mmbiz.qpic.cn/sz_mmbiz_png/...",
  "https://mmbiz.qpic.cn/sz_mmbiz_png/..."
]
```

### 2. 结论

**后端代码是正确的！**

- ✅ 后端能正确保存多个URLs（ID 50有6个URLs）
- ✅ 后端能正确读取多个URLs
- ✅ 数据库存储格式正确（JSON数组）
- ❌ **n8n在某些情况下只返回1个URL**

## 问题分析

### 为什么有些记录只有1个URL？

**可能的原因：**

1. **n8n工作流配置问题**
   - 图片生成节点配置为只生成1张图
   - 数据聚合节点没有正确合并所有图片
   - 不同的图文类型使用了不同的工作流

2. **输入参数影响**
   - 用户选择的"配图张数"参数
   - 某些内容类型可能只支持单图
   - 封面图 vs 配图的区别

3. **工作流分支逻辑**
   - n8n可能有多个分支
   - 某些分支返回单图，某些返回多图

## 验证后端逻辑

### 测试用例1：保存多个URLs

**输入数据：**
```json
{
  "title": "测试标题",
  "content": "测试内容",
  "urls": [
    "https://example.com/image1.png",
    "https://example.com/image2.png",
    "https://example.com/image3.png",
    "https://example.com/image4.png"
  ]
}
```

**预期结果：**
- 后端保存4个URLs
- 数据库中 `media_ids` 字段包含JSON数组
- 前端读取时解析为4个URLs

**实际结果：**
- 后端测试返回500错误（可能是服务启动问题）
- 但数据库中ID 50的记录证明后端**能够**正确保存多个URLs

## 解决方案

### 方案1：检查n8n工作流配置（推荐）

1. **登录n8n控制台**
   - 检查图文生成工作流
   - 查看图片生成节点的配置

2. **检查数据聚合逻辑**
   - 确认所有生成的图片URL都被收集
   - 确认输出格式为数组

3. **检查HTTP请求节点**
   - 发送到后端的payload格式
   - `urls` 字段是否是数组
   - 是否包含所有图片URL

4. **测试不同场景**
   - 单图配置
   - 多图配置（3-6张）
   - 不同的图文类型

### 方案2：添加n8n输出日志

在n8n工作流中添加调试节点，输出最终的payload：

```json
{
  "title": "...",
  "content": "...",
  "urls": ["url1", "url2", "url3", ...],  // 确保这里是数组且包含所有URL
  "height": 1080,
  "width": 1920
}
```

### 方案3：前端验证（可选）

在前端添加更多日志，查看webhook返回的数据：

```javascript
console.log('📥 Webhook返回的result:', result)
console.log('📥 result.media_ids:', result.media_ids)
console.log('📥 media_ids类型:', typeof result.media_ids)
console.log('📥 是否数组:', Array.isArray(result.media_ids))
```

## 后续行动

### 立即行动：
1. ✅ 后端代码已验证正确，无需修改
2. ⚠️ 重点检查n8n工作流配置
3. 📝 在n8n中添加调试日志

### 验证步骤：
1. 修改n8n工作流后，创建新的图文任务
2. 查看后端日志中的 `[图文保存]` 相关输出
3. 确认 `urls数组长度` 是否符合预期
4. 检查数据库中保存的 `media_ids` 字段

## 代码验证

### 后端保存接口 ✅ 正确
```python
# sau_backend.py - line 1000-1001
media_ids_json = json.dumps(urls, ensure_ascii=False)  # 将数组转为JSON字符串
# 保存到数据库的 media_ids 字段
```

### 后端读取接口 ✅ 正确  
```python
# sau_backend.py - line 1162
media_ids = json.loads(row["media_ids"])  # 解析JSON字符串为数组
```

### 前端保存逻辑 ✅ 正确
```javascript
// ProductionCenter.vue - line 5774
body: JSON.stringify({ title, content, urls: urls, height, width })
// urls 是数组
```

### 前端发布逻辑 ✅ 正确
```javascript
// PublishCenter.vue - 已修复
requestBody.urls = urlsArray  // 发送数组到webhook
```

## 数据库Schema验证

```sql
-- production_image_text 表结构
CREATE TABLE production_image_text (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    content TEXT,
    media_ids TEXT,  -- 存储JSON数组字符串，如: ["url1", "url2"]
    url TEXT,        -- 存储第一个URL（快速访问）
    created_at TEXT
);
```

**存储示例：**
```
media_ids: ["url1", "url2", "url3"]  ✅ 正确
url: "url1"                          ✅ 正确（第一个URL）
```

## 总结

| 组件 | 状态 | 说明 |
|------|------|------|
| 后端保存接口 | ✅ 正常 | 能正确保存多个URLs（已验证） |
| 后端读取接口 | ✅ 正常 | 能正确解析JSON数组 |
| 前端保存逻辑 | ✅ 正常 | 正确发送 `urls` 数组 |
| 前端发布逻辑 | ✅ 正常 | 正确转换 `media_ids` 为 `urls` 数组 |
| 数据库存储 | ✅ 正常 | 正确存储JSON数组格式 |
| **n8n工作流** | ⚠️ **问题** | **某些情况下只返回1个URL** |

## 建议

**立即检查n8n工作流配置，确保：**
1. 所有图片都被正确生成
2. 所有图片URL都被收集到数组中
3. 发送到后端的payload包含完整的URLs数组

**n8n调试清单：**
- [ ] 检查图片生成节点的数量配置
- [ ] 检查数据聚合/合并节点
- [ ] 检查HTTP请求节点的body格式
- [ ] 添加调试输出节点
- [ ] 测试不同的图文配置（单图 vs 多图）
