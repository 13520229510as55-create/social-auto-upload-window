# VideoLingo 视频转文章 - 快速开始指南

## 🚀 快速开始（3 步）

### 步骤 1: 配置 API 接口

编辑配置文件 `/opt/videolingo/VideoLingo/config.yaml`：

```yaml
api:
  key: 'your-api-key-here'           # 替换为你的 API Key
  base_url: 'https://api.openai.com/v1/chat/completions'  # API 地址
  model: 'gpt-4'                      # 模型名称
  llm_support_json: false
```

#### 推荐的 API 提供商：

1. **OpenAI** (推荐)
   ```yaml
   api:
     key: 'sk-proj-xxxxxxxxxxxxx'
     base_url: 'https://api.openai.com/v1/chat/completions'
     model: 'gpt-4'  # 或 'gpt-3.5-turbo'
   ```

2. **DeepSeek** (性价比高)
   ```yaml
   api:
     key: 'sk-xxxxxxxxxxxxx'
     base_url: 'https://api.deepseek.com/v1/chat/completions'
     model: 'deepseek-chat'
   ```

3. **OpenRouter** (当前已配置)
   ```yaml
   api:
     key: 'sk-or-v1-xxxxxxxxxxxxx'
     base_url: 'https://openrouter.ai/api/v1/chat/completions'
     model: 'openai/gpt-4'
   ```

### 步骤 2: 准备视频文件

将视频文件放到项目目录：

```bash
# 连接到服务器
ssh ubuntu@150.107.38.113

# 上传视频文件（从本地）
scp /path/to/your/video.mp4 ubuntu@150.107.38.113:/opt/videolingo/VideoLingo/output/video.mp4

# 或在服务器上直接复制
cp /path/to/video.mp4 /opt/videolingo/VideoLingo/output/video.mp4
```

### 步骤 3: 调用转换

#### 方法 A: 使用 Python 脚本（推荐）

```bash
cd /opt/videolingo/VideoLingo
source venv/bin/activate
python test_video_to_article.py
```

#### 方法 B: 使用 REST API

```bash
# 1. 启动 API 服务
cd /opt/videolingo/VideoLingo
source venv/bin/activate
python api_video_to_article.py &

# 2. 上传视频
curl -X POST "http://150.107.38.113:8503/api/upload-video" \
  -F "file=@/path/to/video.mp4"

# 3. 提交转换任务
curl -X POST "http://150.107.38.113:8503/api/video-to-article" \
  -H "Content-Type: application/json" \
  -d '{
    "video_path": "output/uploaded_videos/xxx.mp4",
    "article_type": "blog",
    "style": "professional"
  }'
```

---

## 📋 详细配置说明

### 当前配置状态

当前已配置的 API：
- **提供商**: OpenRouter
- **模型**: Xiaomi: MiMo-V2-Flash
- **Base URL**: https://openrouter.ai/api/v1/chat/completions

### 如何更换 API

1. **编辑配置文件**：
   ```bash
   ssh ubuntu@150.107.38.113
   nano /opt/videolingo/VideoLingo/config.yaml
   ```

2. **修改 API 配置部分**：
   ```yaml
   api:
     key: 'your-new-api-key'
     base_url: 'your-api-base-url'
     model: 'your-model-name'
   ```

3. **保存并测试**：
   ```bash
   cd /opt/videolingo/VideoLingo
   source venv/bin/activate
   python test_video_to_article.py
   ```

---

## 🎯 调用示例

### Python 代码示例

```python
from core._video_to_article import video_to_article

# 转换为技术博客
result = video_to_article(
    video_path="output/video.mp4",
    article_type="blog",      # blog, zhihu, xiaohongshu, note
    style="professional"     # professional, casual, academic
)

print(result["article"])
```

### cURL 命令示例

```bash
# 完整流程
# 1. 上传视频
VIDEO_PATH=$(curl -s -X POST "http://150.107.38.113:8503/api/upload-video" \
  -F "file=@video.mp4" | jq -r '.path')

# 2. 提交任务
TASK_ID=$(curl -s -X POST "http://150.107.38.113:8503/api/video-to-article" \
  -H "Content-Type: application/json" \
  -d "{\"video_path\": \"$VIDEO_PATH\", \"article_type\": \"blog\"}" \
  | jq -r '.task_id')

# 3. 等待完成（轮询）
while true; do
  STATUS=$(curl -s "http://150.107.38.113:8503/api/task/$TASK_ID" | jq -r '.status')
  [ "$STATUS" = "completed" ] && break
  [ "$STATUS" = "failed" ] && exit 1
  sleep 5
done

# 4. 下载文章
curl -s "http://150.107.38.113:8503/api/download/$TASK_ID" -o article.md
```

---

## 📝 文章类型和风格

### 文章类型 (article_type)

- **blog**: 技术博客文章 - 适合技术分享、教程
- **zhihu**: 知乎长文 - 适合深度内容、观点分享
- **xiaohongshu**: 小红书笔记 - 适合轻松内容、生活分享
- **note**: 学习笔记 - 适合知识整理、要点总结

### 文章风格 (style)

- **professional**: 专业严谨 - 适合正式场合
- **casual**: 轻松易懂 - 适合日常交流
- **academic**: 学术规范 - 适合学术内容

---

## 📂 输出文件

转换完成后，文章会保存在：
- **Markdown 文件**: `output/article/article.md`
- **元数据文件**: `output/article/article.json`

---

## 🔍 验证配置

### 测试 API 配置是否正确

```bash
cd /opt/videolingo/VideoLingo
source venv/bin/activate
python -c "
from core.utils import load_key
print('API Key:', load_key('api.key')[:30] + '...')
print('Base URL:', load_key('api.base_url'))
print('Model:', load_key('api.model'))
"
```

### 测试 API 连接

```bash
cd /opt/videolingo/VideoLingo
source venv/bin/activate
python -c "
from core.utils.ask_gpt import ask_gpt
try:
    response = ask_gpt('Hello, test', log_title='test')
    print('✅ API 连接成功')
except Exception as e:
    print(f'❌ API 连接失败: {e}')
"
```

---

## 📚 相关文档

- **详细配置指南**: `/opt/videolingo/VideoLingo/CONFIG_AND_USAGE.md`
- **使用文档**: `/opt/videolingo/VideoLingo/VIDEO_TO_ARTICLE_GUIDE.md`
- **API 文档**: `http://150.107.38.113:8503/docs` (启动 API 服务后)

---

## 🐛 常见问题

### Q: 如何获取 API Key？

- **OpenAI**: https://platform.openai.com/api-keys
- **DeepSeek**: https://platform.deepseek.com/api_keys
- **OpenRouter**: https://openrouter.ai/keys

### Q: 支持哪些模型？

支持所有兼容 OpenAI API 格式的模型。

### Q: 如何查看日志？

```bash
# API 调用日志
ls -la /opt/videolingo/VideoLingo/output/gpt_log/

# 服务日志
sudo journalctl -u videolingo-article-api -f
```

---

**快速开始日期**: 2025-12-22

