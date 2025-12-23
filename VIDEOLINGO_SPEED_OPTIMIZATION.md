# VideoLingo 视频转文章速度优化指南

## 🐌 为什么视频转文章这么慢？

### 主要原因分析

#### 1. **Whisper 模型大小**（最主要原因）

当前配置：`whisper.model: 'large-v3'`

**问题**：
- `large-v3` 是最大的模型（约 3GB），在 CPU 上运行非常慢
- 80MB 视频 ≈ 几分钟音频，使用 large-v3 可能需要 **10-30 分钟** 甚至更久
- 没有 GPU 加速，纯 CPU 处理速度慢 10-100 倍

**速度对比**（CPU 模式，1分钟音频）：
- `tiny`: ~10-20 秒
- `base`: ~20-30 秒
- `small`: ~30-60 秒
- `medium`: ~1-2 分钟
- `large-v3`: ~3-5 分钟 ⚠️ **非常慢**

#### 2. **系统资源限制**

- **内存**: 3.8GB 总内存，3.1GB 已使用，只有 416MB 空闲
- **CPU**: 无 GPU 加速，纯 CPU 处理
- **存储**: 可能影响 I/O 性能

#### 3. **处理流程复杂**

视频转文章需要多个步骤：
1. 视频 → 音频提取（快，几秒）
2. **ASR 转录**（最慢，10-30分钟）⚠️
3. NLP 段落切分（中等，1-2分钟）
4. LLM 文章生成（中等，1-3分钟）

## ⚡ 优化方案

### 方案 1: 使用更小的 Whisper 模型（推荐，最快）

**优点**: 速度快 5-10 倍，质量仍然很好  
**缺点**: 准确度略低于 large-v3

#### 配置步骤：

1. **在 Streamlit 界面配置**：
   - 访问: http://150.107.38.113:8502
   - 左侧边栏 → **Subtitles Settings**
   - 找到 **WhisperX Runtime**（当前是 `local`）
   - 注意：模型选择在代码中，需要修改配置文件

2. **修改配置文件**：

```bash
ssh ubuntu@150.107.38.113
cd /opt/videolingo/VideoLingo
nano config.yaml
```

修改为：
```yaml
whisper:
  model: 'medium'  # 或 'small'（更快）或 'base'（最快）
  language: 'zh'
  runtime: 'local'
```

**推荐配置**：
- **平衡速度和准确度**: `medium`（推荐）
- **最快速度**: `small` 或 `base`
- **最高准确度**: `large-v3`（当前，但很慢）

**速度提升**：
- `medium`: 比 large-v3 快 **5-8 倍**
- `small`: 比 large-v3 快 **8-12 倍**
- `base`: 比 large-v3 快 **12-20 倍**

### 方案 2: 使用云端 API（推荐，最快且准确）

**优点**: 速度快，准确度高，不占用本地资源  
**缺点**: 需要 API Key，可能有费用

#### 配置步骤：

1. **使用 302.ai API**（推荐）：

```yaml
whisper:
  runtime: 'cloud'  # 改为 cloud
  whisperX_302_api_key: 'your_302_api_key'  # 填写你的 API Key
```

**获取 API Key**: https://302.ai

**速度**: 云端 GPU 处理，比本地 CPU 快 **20-50 倍**

2. **使用 ElevenLabs API**：

```yaml
whisper:
  runtime: 'elevenlabs'
  elevenlabs_api_key: 'your_elevenlabs_api_key'
```

### 方案 3: 启用 GPU 加速（如果有 GPU）

如果有 NVIDIA GPU：

```bash
# 检查 GPU
nvidia-smi

# 安装 GPU 版本的 PyTorch
cd /opt/videolingo/VideoLingo
source venv/bin/activate
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**速度提升**: 比 CPU 快 **10-50 倍**

### 方案 4: 优化系统资源

1. **释放内存**：
```bash
# 关闭不必要的服务
sudo systemctl stop <其他服务>
```

2. **增加交换空间**（如果内存不足）：
```bash
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 📊 速度对比表

| 配置方案 | 1分钟音频处理时间 | 10分钟视频处理时间 | 准确度 |
|---------|-----------------|------------------|--------|
| large-v3 (CPU) | 3-5 分钟 | 30-50 分钟 | ⭐⭐⭐⭐⭐ |
| medium (CPU) | 30-60 秒 | 5-10 分钟 | ⭐⭐⭐⭐ |
| small (CPU) | 20-40 秒 | 3-7 分钟 | ⭐⭐⭐ |
| base (CPU) | 10-20 秒 | 2-3 分钟 | ⭐⭐ |
| large-v3 (GPU) | 10-20 秒 | 2-3 分钟 | ⭐⭐⭐⭐⭐ |
| 云端 API (302.ai) | 5-10 秒 | 1-2 分钟 | ⭐⭐⭐⭐⭐ |

## 🎯 推荐配置（根据需求）

### 场景 1: 追求速度（推荐）

```yaml
whisper:
  model: 'medium'  # 或 'small'
  runtime: 'local'
  language: 'zh'
```

**预计时间**: 10分钟视频 → 5-10分钟处理

### 场景 2: 追求准确度

```yaml
whisper:
  model: 'large-v3'
  runtime: 'cloud'  # 使用云端 API
  whisperX_302_api_key: 'your_key'
```

**预计时间**: 10分钟视频 → 1-2分钟处理

### 场景 3: 平衡速度和准确度（最推荐）

```yaml
whisper:
  model: 'medium'
  runtime: 'cloud'  # 云端处理
  whisperX_302_api_key: 'your_key'
```

**预计时间**: 10分钟视频 → 2-3分钟处理

## 🔧 快速优化步骤

### 立即优化（最快方法）

1. **修改配置文件**：
```bash
ssh ubuntu@150.107.38.113
cd /opt/videolingo/VideoLingo
nano config.yaml
```

2. **将模型改为 medium**：
```yaml
whisper:
  model: 'medium'  # 从 large-v3 改为 medium
```

3. **保存并重启服务**：
```bash
sudo systemctl restart videolingo
```

**效果**: 速度提升 **5-8 倍**

## 📝 当前状态

- **视频文件**: 80MB (`实拍4号房.mov`)
- **音频文件**: 179KB (已提取)
- **当前模型**: `large-v3` (CPU 模式)
- **预计转录时间**: 30-50 分钟 ⚠️
- **系统资源**: 内存紧张，无 GPU

## 💡 建议

1. **立即优化**: 将模型改为 `medium`，速度提升 5-8 倍
2. **长期优化**: 使用云端 API（302.ai），速度提升 20-50 倍
3. **如果视频很长**: 考虑分段处理或使用更小的模型

## ❓ 常见问题

### Q: 为什么 large-v3 这么慢？

A: large-v3 是最大的模型（3GB），在 CPU 上需要大量计算。没有 GPU 时，处理速度会非常慢。

### Q: 改用 medium 会影响准确度吗？

A: 会有轻微影响，但对于大多数场景，medium 的准确度已经足够好（约 95%+）。

### Q: 如何知道当前处理到哪一步？

A: 查看 Streamlit 界面，会显示处理进度。或查看日志：
```bash
sudo journalctl -u videolingo -f
```

### Q: 可以中断当前处理吗？

A: 可以，但需要重新开始。建议等待当前处理完成，或优化配置后重新处理。

---

**立即优化**: 将 `whisper.model` 从 `large-v3` 改为 `medium`，速度提升 5-8 倍！

