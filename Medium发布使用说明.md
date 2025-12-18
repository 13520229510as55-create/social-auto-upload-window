# Medium 自动化发布使用说明

## 功能概述

Medium 自动化发布脚本支持：
- ✅ 自动发布文章到 Medium 平台
- ✅ 支持 HTML 和 Markdown 格式内容
- ✅ 支持标签添加（最多5个）
- ✅ 支持定时发布
- ✅ 支持副标题和规范URL设置
- ✅ 支持公开/未列出发布状态
- ✅ Cookie 自动保存和更新

## 安装依赖

确保已安装以下依赖：
```bash
pip install playwright
playwright install chromium
```

## 快速开始

### 1. 生成 Cookie 文件

首次使用需要登录 Medium 并保存 Cookie：

```python
import asyncio
from uploader.medium_uploader import medium_cookie_gen

async def setup():
    account_file = "cookiesFile/medium_account.json"
    await medium_cookie_gen(account_file)

asyncio.run(setup())
```

运行后会打开浏览器，请手动登录 Medium，登录完成后会自动保存 Cookie。

### 2. 发布文章

#### 方式一：使用便捷函数

```python
import asyncio
from uploader.medium_uploader import post_article_to_medium
from datetime import datetime, timedelta

async def publish():
    # 立即发布
    await post_article_to_medium(
        title="My First Automated Article",
        content="<h2>Introduction</h2><p>This is my article content.</p>",
        tags=["python", "automation", "medium"],
        account_file="cookiesFile/medium_account.json",
        subtitle="A subtitle for the article",
        publish_status="public"  # 或 "unlisted"
    )
    
    # 定时发布（明天下午3点）
    publish_time = datetime.now() + timedelta(days=1)
    publish_time = publish_time.replace(hour=15, minute=0, second=0)
    
    await post_article_to_medium(
        title="Scheduled Article",
        content="<p>This will be published tomorrow.</p>",
        tags=["scheduled"],
        account_file="cookiesFile/medium_account.json",
        publish_date=publish_time
    )

asyncio.run(publish())
```

#### 方式二：使用类

```python
import asyncio
from uploader.medium_uploader import MediumArticle
from datetime import datetime

async def publish():
    article = MediumArticle(
        title="My Article Title",
        content="<h2>Content</h2><p>Article body here.</p>",
        tags=["tag1", "tag2", "tag3"],
        account_file="cookiesFile/medium_account.json",
        subtitle="Optional subtitle",
        canonical_url="https://example.com/original-post",  # 可选
        publish_status="public"  # 或 "unlisted"
    )
    
    await article.main()

asyncio.run(publish())
```

## 参数说明

### MediumArticle 类参数

- `title` (str, 必需): 文章标题
- `content` (str, 必需): 文章内容，支持 HTML 或 Markdown
- `tags` (list, 可选): 标签列表，最多5个
- `publish_date` (datetime, 可选): 发布时间，None 表示立即发布
- `account_file` (str, 可选): Cookie 文件路径
- `subtitle` (str, 可选): 副标题
- `canonical_url` (str, 可选): 规范URL（用于SEO）
- `publish_status` (str, 可选): 发布状态
  - `'public'`: 公开（默认）
  - `'unlisted'`: 未列出

## 内容格式

### HTML 格式

```python
content = """
<h2>Introduction</h2>
<p>This is a paragraph.</p>
<ul>
    <li>Item 1</li>
    <li>Item 2</li>
</ul>
"""
```

### Markdown 格式

脚本会自动将 Markdown 转换为 HTML（基础转换）：

```python
content = """
## Introduction
This is a paragraph.

- Item 1
- Item 2
"""
```

## 定时发布

设置 `publish_date` 参数即可实现定时发布：

```python
from datetime import datetime, timedelta

# 明天下午3点发布
publish_time = datetime.now() + timedelta(days=1)
publish_time = publish_time.replace(hour=15, minute=0, second=0)

await post_article_to_medium(
    title="Scheduled Article",
    content="<p>Content</p>",
    publish_date=publish_time,
    account_file="cookiesFile/medium_account.json"
)
```

## 错误处理

### Cookie 失效

如果 Cookie 失效，脚本会提示重新登录：

```python
from uploader.medium_uploader import medium_setup

# 检查并更新 Cookie
account_file = "cookiesFile/medium_account.json"
await medium_setup(account_file, handle=True)  # handle=True 会自动打开浏览器重新登录
```

### 发布失败

如果发布失败，脚本会抛出异常，可以捕获并处理：

```python
try:
    await post_article_to_medium(
        title="Test",
        content="<p>Content</p>",
        account_file="cookiesFile/medium_account.json"
    )
except Exception as e:
    print(f"发布失败: {str(e)}")
```

## 注意事项

1. **标签限制**: Medium 最多支持5个标签，超过会自动截取前5个
2. **内容格式**: 建议使用 HTML 格式，确保格式正确显示
3. **Cookie 安全**: Cookie 文件包含登录信息，请妥善保管
4. **发布频率**: 注意 Medium 的发布频率限制，避免过于频繁
5. **网络环境**: 确保网络连接稳定，建议使用代理（如需要）

## 集成到后端 API

可以在 `sau_backend.py` 中添加 Medium 发布接口：

```python
from uploader.medium_uploader import post_article_to_medium
from datetime import datetime

@app.route('/postToMedium', methods=['POST'])
def post_to_medium():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    tags = data.get('tags', [])
    account_file = data.get('accountFile')
    
    # 异步执行发布
    asyncio.run(post_article_to_medium(
        title=title,
        content=content,
        tags=tags,
        account_file=account_file
    ))
    
    return jsonify({"code": 200, "msg": "发布成功"})
```

## 测试

运行测试脚本：

```bash
python uploader/medium_uploader/main.py
```

## 常见问题

### Q: Cookie 文件在哪里？
A: 默认保存在 `cookiesFile/medium_account.json`，可以自定义路径。

### Q: 支持图片上传吗？
A: 当前版本主要支持文本内容，图片需要先上传到图床，然后在内容中使用图片URL。

### Q: 如何批量发布？
A: 可以循环调用 `post_article_to_medium` 函数，注意控制发布频率。

### Q: 定时发布准确吗？
A: 定时发布依赖于 Medium 平台的功能，脚本会尝试设置，但最终由 Medium 平台控制。

## 更新日志

- v1.0.0: 初始版本，支持基本发布功能
  - 支持文章发布
  - 支持标签添加
  - 支持定时发布
  - 支持 Cookie 管理

