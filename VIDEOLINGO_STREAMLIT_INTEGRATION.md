# VideoLingo Streamlit 界面 - 视频转文章功能集成

## ✅ 已完成的工作

### 1. 新增功能模块

#### 核心功能模块
- **文件**: `core/st_utils/video_to_article_section.py`
- **功能**: 
  - 视频上传界面
  - 文章类型和风格选择
  - 视频转文章处理
  - 文章预览和下载
  - 文章元数据展示

#### 侧边栏配置
- **文件**: `core/st_utils/sidebar_setting.py` (已更新)
- **新增配置项**:
  - Video to Article Settings 展开面板
  - 自定义 API 配置开关
  - 文章类型默认设置
  - 文章风格默认设置

#### 主界面集成
- **文件**: `st.py` (已更新)
- **位置**: 在 "c. Dubbing" 部分之后添加 "d. Video to Article / Blog" 部分

### 2. 功能特性

#### 视频上传
- 支持拖拽上传视频文件
- 支持选择已有视频文件
- 支持格式: MP4, AVI, MOV, MKV, FLV, WMV, WEBM

#### 文章类型选择
- **blog**: 技术博客文章
- **zhihu**: 知乎长文
- **xiaohongshu**: 小红书笔记
- **note**: 学习笔记

#### 文章风格选择
- **professional**: 专业严谨
- **casual**: 轻松易懂
- **academic**: 学术规范

#### 文章展示
- Markdown 格式预览
- 文章下载功能
- 元数据展示
- 重新生成和清理功能

### 3. 配置选项

#### 侧边栏配置面板

在左侧边栏的 "Video to Article Settings" 面板中：

1. **Use Custom API for Article Generation** (开关)
   - 启用后可以为文章生成使用独立的 API 配置
   - 不影响主 LLM 配置

2. **Article API Key** (如果启用自定义 API)
   - 文章生成专用的 API Key

3. **Article Base URL** (如果启用自定义 API)
   - 文章生成专用的 Base URL

4. **Article Model** (如果启用自定义 API)
   - 文章生成专用的模型

5. **Default Article Type** (下拉选择)
   - 默认文章类型

6. **Default Article Style** (下拉选择)
   - 默认文章风格

### 4. 使用流程

#### 步骤 1: 配置 API

在左侧边栏的 "LLM Configuration" 中配置主 API，或在 "Video to Article Settings" 中配置专用 API。

#### 步骤 2: 上传视频

在主界面 "d. Video to Article / Blog" 部分：
- 点击上传区域上传视频文件
- 或从已有视频文件列表中选择

#### 步骤 3: 选择文章类型和风格

- 选择文章类型（blog/zhihu/xiaohongshu/note）
- 选择文章风格（professional/casual/academic）

#### 步骤 4: 开始转换

点击 "Start Video to Article Conversion" 按钮，系统将：
1. 转录视频（如果未跳过）
2. NLP 段落切分
3. LLM 语义总结
4. 生成 Markdown 文章

#### 步骤 5: 查看和下载文章

转换完成后：
- 在界面中预览文章内容
- 下载 Markdown 文件
- 查看文章元数据

### 5. 界面位置

视频转文章功能位于主界面的第四个部分：

1. **a. Download or Upload Video** - 下载/上传视频
2. **b. Translate and Generate Subtitles** - 翻译并生成字幕
3. **c. Dubbing** - 配音
4. **d. Video to Article / Blog** - **视频转文章** ⭐ (新增)

### 6. 文件结构

```
/opt/videolingo/VideoLingo/
├── core/
│   ├── _video_to_article.py          # 核心转换逻辑
│   └── st_utils/
│       ├── video_to_article_section.py  # Streamlit UI 模块 (新增)
│       └── sidebar_setting.py          # 侧边栏配置 (已更新)
├── st.py                              # 主界面文件 (已更新)
└── output/
    └── article/
        ├── article.md                 # 生成的文章
        └── article.json               # 文章元数据
```

### 7. 配置示例

#### 使用主 LLM 配置（默认）

无需额外配置，直接使用左侧边栏 "LLM Configuration" 中的设置。

#### 使用自定义 API 配置

1. 在侧边栏展开 "Video to Article Settings"
2. 启用 "Use Custom API for Article Generation"
3. 填写：
   - Article API Key
   - Article Base URL
   - Article Model

### 8. 访问方式

- **Streamlit 界面**: http://150.107.38.113:8502
- 在界面中找到 "d. Video to Article / Blog" 部分

### 9. 功能特点

✅ **集成到现有界面** - 无缝集成到 VideoLingo Streamlit 界面
✅ **配置灵活** - 支持使用主 API 或独立 API 配置
✅ **多种文章类型** - 支持 4 种文章类型和 3 种风格
✅ **用户友好** - 拖拽上传、实时预览、一键下载
✅ **状态管理** - 自动保存和恢复文章状态

### 10. 注意事项

1. **API 配置**: 确保在侧边栏中正确配置了 LLM API
2. **视频格式**: 支持常见视频格式，建议使用 MP4
3. **处理时间**: 大视频文件处理可能需要较长时间
4. **存储空间**: 确保有足够的存储空间保存视频和文章

### 11. 故障排查

#### 问题: 模块导入失败

```bash
# 检查模块是否存在
ls -la /opt/videolingo/VideoLingo/core/st_utils/video_to_article_section.py

# 检查服务状态
sudo systemctl status videolingo
```

#### 问题: API 调用失败

- 检查侧边栏中的 API 配置
- 查看日志: `output/gpt_log/video_to_article.json`

#### 问题: 视频上传失败

- 检查文件大小（限制 4GB）
- 检查文件格式是否支持
- 检查存储空间

---

**集成完成日期**: 2025-12-23
**状态**: ✅ 已完成并可用

访问 http://150.107.38.113:8502 即可使用新功能！

