# VideoLingo 视频转文章功能 - 配置指南

## 📋 概述

**Video to Article / Blog** 功能需要配置 **大模型 API** 才能正常工作。该功能使用 LLM（大语言模型）将视频转录文本转换为高质量的文章。

## ✅ 必须配置的内容

### 1. 大模型 API（必需）

视频转文章功能的核心是将转录文本转换为文章，这需要调用大模型 API。

#### 配置位置

**方法 1: 在 Streamlit 界面配置（推荐）**

1. 打开 http://150.107.38.113:8502
2. 在左侧边栏找到 **"LLM Configuration"** 部分
3. 填写以下信息：
   - **API_KEY**: 你的 API Key
   - **BASE_URL**: API 地址
   - **MODEL**: 模型名称

**方法 2: 修改配置文件**

编辑 `/opt/videolingo/VideoLingo/config.yaml`：

```yaml
api:
  key: 'your-api-key-here'           # 必需：你的 API Key
  base_url: 'https://api.openai.com/v1/chat/completions'  # 必需：API 地址
  model: 'gpt-4'                      # 必需：模型名称
  llm_support_json: false            # 可选：是否支持 JSON 格式
```

## 🔧 推荐的 API 提供商

### 1. OpenAI（推荐，质量最好）

**优点**: 质量高，稳定性好  
**缺点**: 价格较高

**配置示例**:
```yaml
api:
  key: 'sk-proj-xxxxxxxxxxxxxxxxxxxxx'
  base_url: 'https://api.openai.com/v1/chat/completions'
  model: 'gpt-4'  # 或 'gpt-3.5-turbo'（更便宜）
  llm_support_json: true
```

**获取 API Key**: https://platform.openai.com/api-keys

**推荐模型**:
- `gpt-4` - 质量最好，适合高质量文章
- `gpt-4-turbo-preview` - 平衡质量和速度
- `gpt-3.5-turbo` - 性价比高，速度快

### 2. DeepSeek（性价比高）

**优点**: 价格便宜，中文支持好  
**缺点**: 质量略低于 GPT-4

**配置示例**:
```yaml
api:
  key: 'sk-xxxxxxxxxxxxxxxxxxxxx'
  base_url: 'https://api.deepseek.com/v1/chat/completions'
  model: 'deepseek-chat'  # 或 'deepseek-coder'
  llm_support_json: false
```

**获取 API Key**: https://platform.deepseek.com/api_keys

**推荐模型**:
- `deepseek-chat` - 通用对话模型
- `deepseek-coder` - 适合技术文章

### 3. OpenRouter（当前配置，支持多种模型）

**优点**: 可以访问多种模型，包括 GPT-4、Claude 等  
**缺点**: 需要选择正确的模型名称

**配置示例**:
```yaml
api:
  key: 'sk-or-v1-xxxxxxxxxxxxx'
  base_url: 'https://openrouter.ai/api/v1/chat/completions'
  model: 'openai/gpt-4'  # 或其他模型
  llm_support_json: false
```

**获取 API Key**: https://openrouter.ai/keys

**推荐模型**:
- `openai/gpt-4` - GPT-4
- `openai/gpt-3.5-turbo` - GPT-3.5
- `anthropic/claude-3-opus` - Claude 3
- `google/gemini-pro` - Google Gemini

### 4. 其他兼容 OpenAI 格式的 API

任何兼容 OpenAI API 格式的服务都可以使用，例如：
- 本地部署的模型（如 Ollama、LocalAI）
- 其他云服务商的 API

## 🎯 配置步骤详解

### 步骤 1: 获取 API Key

根据选择的提供商，注册账号并获取 API Key。

### 步骤 2: 在 Streamlit 界面配置

1. **访问界面**: http://150.107.38.113:8502
2. **找到配置区域**: 左侧边栏 → "LLM Configuration"
3. **填写配置**:
   ```
   API_KEY: sk-xxxxxxxxxxxxx
   BASE_URL: https://api.openai.com/v1/chat/completions
   MODEL: gpt-4
   ```
4. **测试连接**: 点击配置旁边的 📡 按钮测试 API 是否有效
5. **保存**: 配置会自动保存

### 步骤 3: 验证配置

配置完成后，可以：
1. 上传一个测试视频
2. 尝试生成文章
3. 如果成功，说明配置正确

## ⚙️ 高级配置（可选）

### 使用独立的 API 配置

如果你想为文章生成使用不同的 API（不影响其他功能）：

1. 在左侧边栏展开 **"Video to Article Settings"**
2. 启用 **"Use Custom API for Article Generation"**
3. 填写：
   - Article API Key
   - Article Base URL
   - Article Model

这样可以为文章生成单独配置 API，不影响字幕翻译等其他功能。

### 配置默认文章类型和风格

在 **"Video to Article Settings"** 中：
- **Default Article Type**: 选择默认的文章类型（blog/zhihu/xiaohongshu/note）
- **Default Article Style**: 选择默认的文章风格（professional/casual/academic）

## 📊 当前配置状态

查看当前配置：

```bash
ssh ubuntu@150.107.38.113
cd /opt/videolingo/VideoLingo
cat config.yaml | grep -A 5 'api:'
```

**当前配置**:
- API Key: 已配置（OpenRouter）
- Base URL: https://openrouter.ai/api/v1/chat/completions
- Model: Xiaomi: MiMo-V2-Flash

**注意**: 当前模型可能不可用（返回 404），建议更换为其他模型。

## 🔍 配置验证

### 测试 API 配置

在服务器上运行：

```bash
cd /opt/videolingo/VideoLingo
source venv/bin/activate
python3 -c "
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
python3 -c "
from core.utils.ask_gpt import ask_gpt
try:
    response = ask_gpt('Hello, test', log_title='test')
    print('✅ API 连接成功')
    print('响应:', response[:100])
except Exception as e:
    print('❌ API 连接失败:', e)
"
```

## 💡 配置建议

### 根据用途选择模型

1. **高质量文章**（推荐 GPT-4）:
   ```yaml
   model: 'gpt-4'
   ```

2. **性价比平衡**（推荐 GPT-3.5 或 DeepSeek）:
   ```yaml
   model: 'gpt-3.5-turbo'  # 或 'deepseek-chat'
   ```

3. **中文内容**（推荐 DeepSeek）:
   ```yaml
   model: 'deepseek-chat'
   ```

### 成本考虑

- **GPT-4**: ~$0.03/1K tokens（高质量，价格高）
- **GPT-3.5-turbo**: ~$0.002/1K tokens（性价比高）
- **DeepSeek**: ~$0.0007/1K tokens（最便宜）

**估算**: 一篇 2000 字的文章大约需要 3000-5000 tokens

## ❓ 常见问题

### Q1: 必须配置大模型吗？

**A**: 是的，视频转文章功能必须配置大模型 API。该功能使用 LLM 将转录文本转换为文章，没有大模型无法生成文章。

### Q2: 可以使用免费的大模型吗？

**A**: 可以，但需要自己部署或使用免费 API：
- **Ollama**（本地部署，免费）
- **Google Colab**（免费额度）
- **Hugging Face Inference API**（有免费额度）

### Q3: 配置后还是无法生成文章？

**A**: 检查以下几点：
1. API Key 是否正确
2. Base URL 是否正确
3. 模型名称是否正确
4. 网络连接是否正常
5. API 配额是否用完

### Q4: 如何查看 API 使用日志？

```bash
# 查看 GPT 调用日志
ls -la /opt/videolingo/VideoLingo/output/gpt_log/
cat /opt/videolingo/VideoLingo/output/gpt_log/video_to_article.json | tail -20
```

### Q5: 可以同时使用多个 API 吗？

**A**: 可以，使用 "Video to Article Settings" 中的自定义 API 配置，可以为文章生成单独配置 API。

## 📝 快速配置示例

### OpenAI 快速配置

1. 获取 API Key: https://platform.openai.com/api-keys
2. 在 Streamlit 界面配置：
   - API_KEY: `sk-proj-xxxxxxxxxxxxx`
   - BASE_URL: `https://api.openai.com/v1/chat/completions`
   - MODEL: `gpt-4`
3. 点击 📡 测试连接
4. 完成！

### DeepSeek 快速配置

1. 获取 API Key: https://platform.deepseek.com/api_keys
2. 在 Streamlit 界面配置：
   - API_KEY: `sk-xxxxxxxxxxxxx`
   - BASE_URL: `https://api.deepseek.com/v1/chat/completions`
   - MODEL: `deepseek-chat`
3. 点击 📡 测试连接
4. 完成！

## 🎯 总结

**必须配置**:
- ✅ 大模型 API Key
- ✅ API Base URL
- ✅ 模型名称

**可选配置**:
- ⚪ 独立的文章生成 API（在 Video to Article Settings 中）
- ⚪ 默认文章类型和风格

**推荐配置**:
- 高质量: OpenAI GPT-4
- 性价比: DeepSeek 或 GPT-3.5-turbo
- 中文内容: DeepSeek

---

**配置完成后，就可以开始使用视频转文章功能了！** 🚀

