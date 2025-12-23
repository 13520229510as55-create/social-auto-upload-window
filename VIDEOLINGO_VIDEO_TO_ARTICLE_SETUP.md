# VideoLingo 视频转文章功能部署总结

## ✅ 已完成的工作

### 1. 核心功能模块
- **文件**: `/opt/videolingo/VideoLingo/core/_video_to_article.py`
- **功能**: 实现完整的视频转文章流程
  - 视频转录 (ASR)
  - NLP 段落切分
  - LLM 语义总结
  - Markdown 文章生成

### 2. REST API 接口
- **文件**: `/opt/videolingo/VideoLingo/api_video_to_article.py`
- **端口**: 8503
- **功能**: 提供 RESTful API 接口

### 3. 使用文档
- **文件**: `/opt/videolingo/VideoLingo/VIDEO_TO_ARTICLE_GUIDE.md`
- **内容**: 详细的使用说明和示例

### 4. 启动脚本和服务
- **启动脚本**: `/opt/videolingo/VideoLingo/start_article_api.sh`
- **Systemd 服务**: `videolingo-article-api.service`

## 🚀 快速开始

### 启动 API 服务

```bash
# 方法 1: 使用 systemd 服务（推荐）
ssh ubuntu@150.107.38.113
sudo systemctl start videolingo-article-api
sudo systemctl enable videolingo-article-api

# 方法 2: 手动启动
cd /opt/videolingo/VideoLingo
source venv/bin/activate
python api_video_to_article.py
```

### API 端点

- **根路径**: `http://150.107.38.113:8503/`
- **API 文档**: `http://150.107.38.113:8503/docs` (Swagger UI)
- **上传视频**: `POST /api/upload-video`
- **提交任务**: `POST /api/video-to-article`
- **查询状态**: `GET /api/task/{task_id}`
- **获取文章**: `GET /api/article/{task_id}`
- **下载文章**: `GET /api/download/{task_id}`

## 📝 使用示例

### Python 代码示例

```python
from core._video_to_article import video_to_article

# 转换为技术博客
result = video_to_article(
    video_path="output/video.mp4",
    article_type="blog",
    style="professional"
)

print(result["article"])
```

### cURL 示例

```bash
# 1. 上传视频
curl -X POST "http://150.107.38.113:8503/api/upload-video" \
  -F "file=@video.mp4"

# 2. 提交转换任务
curl -X POST "http://150.107.38.113:8503/api/video-to-article" \
  -H "Content-Type: application/json" \
  -d '{
    "video_path": "output/uploaded_videos/xxx.mp4",
    "article_type": "blog",
    "style": "professional"
  }'

# 3. 查询任务状态
curl "http://150.107.38.113:8503/api/task/{task_id}"

# 4. 获取文章
curl "http://150.107.38.113:8503/api/article/{task_id}"

# 5. 下载文章
curl "http://150.107.38.113:8503/api/download/{task_id}" -o article.md
```

## 📋 支持的文章类型

- **blog**: 技术博客文章
- **zhihu**: 知乎长文
- **xiaohongshu**: 小红书笔记
- **note**: 学习笔记

## 🎨 支持的文章风格

- **professional**: 专业严谨
- **casual**: 轻松易懂
- **academic**: 学术规范

## ⚙️ 配置说明

### API 配置

在 `config.yaml` 中配置：

```yaml
api:
  key: 'your-api-key'
  base_url: 'https://api.openai.com/v1/chat/completions'
  model: 'gpt-4'
```

或在 API 请求中动态指定。

## 📂 输出文件

- **文章文件**: `output/article/article.md`
- **元数据**: `output/article/article.json`

## 🔧 服务管理

```bash
# 启动服务
sudo systemctl start videolingo-article-api

# 停止服务
sudo systemctl stop videolingo-article-api

# 重启服务
sudo systemctl restart videolingo-article-api

# 查看状态
sudo systemctl status videolingo-article-api

# 查看日志
sudo journalctl -u videolingo-article-api -f

# 设置开机自启
sudo systemctl enable videolingo-article-api
```

## 📚 相关文档

- **使用指南**: `/opt/videolingo/VideoLingo/VIDEO_TO_ARTICLE_GUIDE.md`
- **API 文档**: `http://150.107.38.113:8503/docs`
- **项目文档**: `/opt/videolingo/VideoLingo/README.md`

## 🐛 故障排查

### 1. 服务无法启动

```bash
# 检查日志
sudo journalctl -u videolingo-article-api -n 50

# 检查端口
sudo netstat -tlnp | grep 8503
```

### 2. API 调用失败

- 检查 API Key 是否正确
- 检查网络连接
- 查看 API 日志 `output/gpt_log/`

### 3. 转录失败

- 检查视频文件是否存在
- 检查 Whisper 模型是否正确安装
- 查看日志文件 `output/log/`

## 💡 注意事项

1. **端口冲突**: 确保 8503 端口未被占用
2. **防火墙**: 确保防火墙已开放 8503 端口
3. **API 配额**: 注意 LLM API 的使用配额
4. **文件大小**: 大视频文件处理可能需要较长时间

## 📞 支持

- 查看项目 Issues: https://github.com/Huanshere/VideoLingo/issues
- 查看服务日志: `sudo journalctl -u videolingo-article-api -f`
- 查看 API 日志: `output/gpt_log/`

---

**部署日期**: 2025-12-22
**状态**: ✅ 已完成并可用

