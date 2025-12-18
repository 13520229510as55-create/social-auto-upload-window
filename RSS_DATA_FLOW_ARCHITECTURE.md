# RSS 数据流转架构设计

## 📋 方案概述

统一通过 n8n 工作流处理三个平台的数据，实现优雅、低成本的数据流转。

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                     数据源层                                  │
├─────────────────────────────────────────────────────────────┤
│  RSSHub (RSS)  │  MediaCrawler (API)  │  WeWe-RSS (RSS)     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                    n8n 工作流层                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ RSS Trigger  │  │ HTTP Request │  │ RSS Trigger  │     │
│  │ (RSSHub)     │  │ (MediaCrawler)│  │ (WeWe-RSS)   │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                  │              │
│         └─────────────────┴──────────────────┘             │
│                          ↓                                   │
│              ┌──────────────────────┐                        │
│              │  数据标准化处理节点    │                        │
│              │  (统一数据格式转换)    │                        │
│              └──────────┬───────────┘                        │
│                         ↓                                     │
│              ┌──────────────────────┐                        │
│              │  数据去重节点         │                        │
│              │  (基于唯一标识)        │                        │
│              └──────────┬───────────┘                        │
│                         ↓                                     │
│              ┌──────────────────────┐                        │
│              │  HTTP Request        │                        │
│              │  (保存到服务器)        │                        │
│              └──────────────────────┘                        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                   后端服务层                                  │
│              /api/content/save (统一接口)                    │
└─────────────────────────────────────────────────────────────┘
```

## 📊 数据格式标准化

### 统一数据模型

```json
{
  "source": "rsshub|mediacrawler|wewe-rss",
  "source_platform": "twitter|xiaohongshu|wechat",
  "content_id": "唯一标识",
  "title": "标题",
  "content": "正文内容",
  "author": "作者",
  "author_id": "作者ID",
  "url": "原文链接",
  "published_at": "2024-01-01T00:00:00Z",
  "media_urls": ["图片/视频URL数组"],
  "tags": ["标签数组"],
  "metadata": {
    "原始数据": "保留原始字段"
  }
}
```

## 🔄 数据流转方案

### 方案 1: RSSHub → n8n (RSS Trigger)

**n8n 工作流配置：**
1. **RSS Feed Trigger**
   - URL: `https://rsshub.app/twitter/user/username`
   - 轮询间隔: 15分钟
   - 输出: RSS Feed Items

2. **Function 节点 - 数据标准化**
   ```javascript
   // 将 RSS 格式转换为统一格式
   const items = $input.all();
   return items.map(item => ({
     json: {
       source: 'rsshub',
       source_platform: 'twitter',
       content_id: item.json.guid || item.json.link,
       title: item.json.title,
       content: item.json.content || item.json.description,
       author: item.json.creator || item.json['dc:creator'],
       url: item.json.link,
       published_at: item.json.pubDate,
       media_urls: extractMediaUrls(item.json.content),
       tags: [],
       metadata: item.json
     }
   }));
   ```

### 方案 2: MediaCrawler → n8n (HTTP Request + Schedule)

**MediaCrawler 改造方案：**

#### 选项 A: 添加 HTTP API 接口（推荐）

在 MediaCrawler 中添加一个简单的 Flask/FastAPI 服务：

```python
# mediacrawler_api.py
from flask import Flask, jsonify, request
import json
from pathlib import Path

app = Flask(__name__)

@app.route('/api/crawl', methods=['POST'])
def crawl_data():
    """触发爬取并返回数据"""
    data = request.json
    platform = data.get('platform')
    # 调用 MediaCrawler 爬取
    # 返回标准化数据
    return jsonify({
        "code": 200,
        "data": standardized_data
    })

@app.route('/api/latest', methods=['GET'])
def get_latest():
    """获取最新爬取的数据"""
    # 从数据库或文件读取最新数据
    return jsonify({
        "code": 200,
        "data": latest_data
    })
```

**n8n 工作流配置：**
1. **Schedule Trigger** (定时触发，如每小时)
2. **HTTP Request 节点**
   - Method: POST
   - URL: `http://mediacrawler:port/api/crawl`
   - Body: `{"platform": "xhs", "type": "search"}`

#### 选项 B: 使用文件监听（更简单）

MediaCrawler 输出到指定目录，n8n 监听文件变化：

```python
# MediaCrawler 改造：输出到 webhook 目录
output_dir = Path("webhook_output")
output_file = output_dir / f"{platform}_{timestamp}.json"
```

**n8n 工作流配置：**
1. **Schedule Trigger**
2. **Read Binary File 节点** (读取最新文件)
3. **JSON Parse 节点**

### 方案 3: WeWe-RSS → n8n (RSS Trigger)

**n8n 工作流配置：**
1. **RSS Feed Trigger**
   - URL: `http://150.107.38.113:4000/feeds/all.rss`
   - 轮询间隔: 30分钟

2. **Function 节点 - 数据标准化**
   ```javascript
   // 类似 RSSHub 的处理
   const items = $input.all();
   return items.map(item => ({
     json: {
       source: 'wewe-rss',
       source_platform: 'wechat',
       content_id: item.json.guid || item.json.link,
       title: item.json.title,
       content: item.json.content || item.json.description,
       author: item.json['dc:creator'] || '微信公众号',
       url: item.json.link,
       published_at: item.json.pubDate,
       media_urls: extractMediaUrls(item.json.content),
       tags: [],
       metadata: item.json
     }
   }));
   ```

## 🔧 后端统一接口

### 新增统一保存接口

```python
# sau_backend.py
@app.route('/api/content/save', methods=['POST'])
def save_content():
    """
    统一的内容保存接口
    接收来自 n8n 的标准化数据
    """
    data = request.get_json(silent=True) or {}
    
    # 验证必填字段
    required_fields = ['source', 'content_id', 'title']
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({
            "code": 400,
            "msg": f"缺少必要字段: {', '.join(missing_fields)}",
            "data": None
        }), 400
    
    try:
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            cursor = conn.cursor()
            
            # 检查是否已存在（去重）
            cursor.execute('''
                SELECT id FROM content_sources 
                WHERE content_id = ? AND source = ?
            ''', (data.get('content_id'), data.get('source')))
            
            existing = cursor.fetchone()
            if existing:
                return jsonify({
                    "code": 200,
                    "msg": "内容已存在，跳过",
                    "data": {"id": existing[0]}
                }), 200
            
            # 插入新记录
            china_time = get_china_time()
            cursor.execute('''
                INSERT INTO content_sources (
                    source,
                    source_platform,
                    content_id,
                    title,
                    content,
                    author,
                    author_id,
                    url,
                    published_at,
                    media_urls,
                    tags,
                    metadata,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('source'),
                data.get('source_platform'),
                data.get('content_id'),
                data.get('title', ''),
                data.get('content', ''),
                data.get('author', ''),
                data.get('author_id', ''),
                data.get('url', ''),
                data.get('published_at', ''),
                json.dumps(data.get('media_urls', []), ensure_ascii=False),
                json.dumps(data.get('tags', []), ensure_ascii=False),
                json.dumps(data.get('metadata', {}), ensure_ascii=False),
                china_time
            ))
            conn.commit()
            record_id = cursor.lastrowid
        
        return jsonify({
            "code": 200,
            "msg": "内容保存成功",
            "data": {"id": record_id}
        }), 200
    
    except Exception as e:
        print(f"保存内容失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "msg": f"保存失败: {str(e)}",
            "data": None
        }), 500
```

### 数据库表结构

```sql
CREATE TABLE IF NOT EXISTS content_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,              -- rsshub, mediacrawler, wewe-rss
    source_platform TEXT,               -- twitter, xiaohongshu, wechat
    content_id TEXT NOT NULL,           -- 唯一标识
    title TEXT,
    content TEXT,
    author TEXT,
    author_id TEXT,
    url TEXT,
    published_at TEXT,
    media_urls TEXT,                    -- JSON 数组
    tags TEXT,                          -- JSON 数组
    metadata TEXT,                       -- JSON 对象
    created_at TEXT,
    UNIQUE(content_id, source)          -- 防止重复
);
```

## 🎯 n8n 工作流设计

### 工作流 1: RSSHub 数据流

```yaml
工作流名称: RSSHub Content Flow
触发方式: RSS Feed Trigger
节点:
  1. RSS Feed Trigger
     - URL: {{ $env.RSSHUB_BASE_URL }}/twitter/user/{{ username }}
     - 间隔: 15分钟
  2. Function: 数据标准化
  3. Function: 数据去重检查
  4. HTTP Request: 保存到服务器
     - URL: http://your-server/api/content/save
     - Method: POST
```

### 工作流 2: MediaCrawler 数据流

```yaml
工作流名称: MediaCrawler Content Flow
触发方式: Schedule Trigger (每小时)
节点:
  1. Schedule Trigger
     - Cron: 0 * * * * (每小时)
  2. HTTP Request: 触发爬取
     - URL: http://mediacrawler:port/api/crawl
     - Method: POST
     - Body: {"platform": "xhs", "type": "search"}
  3. Wait: 等待爬取完成 (5分钟)
  4. HTTP Request: 获取数据
     - URL: http://mediacrawler:port/api/latest
  5. Function: 数据标准化
  6. Function: 数据去重检查
  7. HTTP Request: 保存到服务器
```

### 工作流 3: WeWe-RSS 数据流

```yaml
工作流名称: WeWe-RSS Content Flow
触发方式: RSS Feed Trigger
节点:
  1. RSS Feed Trigger
     - URL: http://150.107.38.113:4000/feeds/all.rss
     - 间隔: 30分钟
  2. Function: 数据标准化
  3. Function: 数据去重检查
  4. HTTP Request: 保存到服务器
```

## 💡 优化建议

### 1. 数据去重策略

在 n8n 中添加去重节点：

```javascript
// Function 节点：去重检查
const items = $input.all();
const seen = new Set();
const unique = [];

for (const item of items) {
  const key = `${item.json.source}_${item.json.content_id}`;
  if (!seen.has(key)) {
    seen.add(key);
    unique.push(item);
  }
}

return unique;
```

### 2. 错误处理和重试

在 n8n 中配置：
- 错误处理节点
- 重试机制（最多3次）
- 失败通知（邮件/Telegram）

### 3. 批量处理

对于大量数据，使用 n8n 的 Split in Batches 节点：
- 每批处理 10-20 条
- 避免单次请求过大

### 4. 监控和日志

- 在 n8n 中添加日志节点
- 记录处理成功/失败数量
- 定期检查数据质量

## 📈 成本优化

### 1. 减少轮询频率
- RSSHub: 15分钟 → 30分钟
- WeWe-RSS: 30分钟 → 1小时
- MediaCrawler: 每小时 → 每2小时

### 2. 智能去重
- 在 n8n 层面去重，减少无效请求
- 数据库层面唯一索引，防止重复插入

### 3. 资源复用
- 使用同一个 n8n 实例
- 共享数据库连接
- 统一日志系统

### 4. 缓存策略
- n8n 缓存最近处理的内容ID
- 减少数据库查询

## 🚀 实施步骤

### 阶段 1: 基础搭建（1-2天）
1. 创建数据库表
2. 实现统一保存接口
3. 测试接口功能

### 阶段 2: n8n 工作流配置（2-3天）
1. 配置 RSSHub 工作流
2. 配置 WeWe-RSS 工作流
3. 测试数据流转

### 阶段 3: MediaCrawler 改造（3-5天）
1. 添加 HTTP API 接口
2. 配置 n8n MediaCrawler 工作流
3. 测试完整流程

### 阶段 4: 优化和监控（持续）
1. 添加去重逻辑
2. 配置监控告警
3. 优化性能

## 📝 总结

**优势：**
- ✅ 统一数据格式
- ✅ 统一处理流程
- ✅ 易于维护和扩展
- ✅ 成本可控

**关键点：**
- MediaCrawler 需要添加 HTTP API（最小改造）
- n8n 作为统一的数据处理中心
- 后端提供统一的保存接口
- 数据格式标准化是关键

