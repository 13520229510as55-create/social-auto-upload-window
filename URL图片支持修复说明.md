# URL图片支持修复说明

## 问题描述

小红书图文发布时，如果图片路径是URL格式（如 `@http://res.cloudinary.com/...`），会提示：
```
发布失败: 图片文件不存在: @http://res.cloudinary.com/durtefzdp/image/upload/v1764509147/al49rj4og87.png (已尝试: videoFile, media, 根目录)
```

## 问题原因

`myUtils/postVideo.py` 中的 `post_image_text_xhs` 函数只检查本地文件路径，没有处理URL格式的图片。当图片路径是URL时，代码会在本地文件系统中查找，导致失败。

## 修复方案

### 1. 添加图片下载函数

在 `myUtils/postVideo.py` 中添加 `download_image_from_url` 函数：
- 从URL下载图片到本地
- 自动识别图片格式（通过Content-Type或URL扩展名）
- 生成唯一文件名（使用UUID）
- 下载到 `media` 目录

### 2. 修改图片路径处理逻辑

在 `post_image_text_xhs` 函数中：
- 检测URL格式（`http://` 或 `https://` 开头）
- 自动去掉 `@` 前缀（如果存在）
- 如果是URL，调用下载函数
- 如果是本地路径，保持原有逻辑

## 修复内容

### 新增导入
```python
import os
import uuid
import requests
from urllib.parse import urlparse
```

### 新增函数
- `download_image_from_url(url, output_dir=None)` - 从URL下载图片

### 修改函数
- `post_image_text_xhs()` - 添加URL检测和下载逻辑

## 测试结果

✅ **测试成功**
- 测试URL: `@http://res.cloudinary.com/durtefzdp/image/upload/v1764509147/al49rj4og87.png`
- 下载状态: ✅ 成功下载到media目录
- 发布状态: ✅ 图文发布成功，已跳转到成功页面
- 测试时间: 2025-12-01 01:07:51

## 支持的格式

1. **URL格式**（自动下载）:
   - `http://example.com/image.png`
   - `https://example.com/image.jpg`
   - `@http://example.com/image.png` (支持@前缀)

2. **本地文件格式**（保持原有逻辑）:
   - 文件名: `image.png` (在media或videoFile目录查找)
   - 绝对路径: `/path/to/image.png`

## 代码变更

- **文件**: `myUtils/postVideo.py`
- **变更行数**: +114行新增，-15行删除
- **提交ID**: `5e01a25`
- **版本标签**: `v1.0.1-xhs-url-image-support`

## 部署状态

✅ **代码已部署到服务器**
- 服务器路径: `/home/ubuntu/social-auto-upload/myUtils/postVideo.py`
- 功能验证: ✅ URL图片下载和发布测试通过

