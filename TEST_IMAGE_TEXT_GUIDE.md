# 小红书图文发布功能测试指南

## 当前状态检查

### 1. 账号状态
- ✅ 找到 2 个cookie文件
- ⚠️  数据库中没有 type=1 的小红书账号
- 📝 建议：在账号管理中重新添加小红书账号，确保 type=1

### 2. 图片文件
- ❌ videoFile 目录中没有图片文件（.jpg, .png, .jpeg）
- 📝 需要先上传图片文件

### 3. 后端服务
- ❌ 后端服务未运行（localhost:5409 无法连接）
- 📝 需要先启动后端服务

## 测试步骤

### 步骤 1: 启动后端服务

```bash
cd /Users/a58/Desktop/social-auto-upload
python3 sau_backend.py
```

或者如果使用 PM2：
```bash
pm2 start sau_backend.py --name sau-backend
```

### 步骤 2: 添加小红书账号

1. 访问前端页面：http://localhost:5173 或 http://150.107.38.113:5173
2. 进入"账号管理"
3. 点击"添加账号"
4. 选择平台：**小红书**（确保选择的是小红书，不是视频号）
5. 输入账号名称
6. 扫码登录完成账号添加

### 步骤 3: 上传测试图片

**方法1: 通过接口上传**
```bash
curl -X POST http://localhost:5409/upload \
  -F "file=@/path/to/your/image.jpg"
```

**方法2: 手动放置**
将图片文件复制到 `videoFile` 目录：
```bash
cp /path/to/your/image.jpg videoFile/
```

### 步骤 4: 运行测试脚本

```bash
cd /Users/a58/Desktop/social-auto-upload
python3 test_image_text_publish.py
```

## 接口测试（手动）

如果后端服务已启动，可以直接使用 curl 测试：

```bash
curl -X POST http://localhost:5409/postImageText \
  -H "Content-Type: application/json" \
  -d '{
    "title": "测试图文标题",
    "imageList": ["test_image.jpg"],
    "accountList": ["41340e10-c50a-11f0-aa81-128298524a52.json"],
    "tags": ["测试", "图文"],
    "enableTimer": false
  }'
```

## 接口参数说明

- `title`: 图文标题（必填）
- `imageList`: 图片文件名列表，文件需在 videoFile 目录中（必填）
- `accountList`: 账号cookie文件名列表，文件需在 cookiesFile 目录中（必填）
- `tags`: 标签列表（可选）
- `enableTimer`: 是否定时发布（可选，默认false）

## 注意事项

1. **账号类型**: 确保账号的 type=1（小红书），不是 type=2（视频号）
2. **图片格式**: 支持 .jpg, .png, .jpeg 格式
3. **文件路径**: 
   - 图片文件路径相对于 `videoFile` 目录
   - 账号文件路径相对于 `cookiesFile` 目录
4. **发布过程**: 发布过程可能需要一些时间，请查看后端日志了解进度

## 故障排查

### 问题1: 找不到小红书账号
- 检查数据库：`SELECT * FROM user_info WHERE type = 1`
- 确保在账号管理中选择的是"小红书"平台

### 问题2: 找不到图片文件
- 检查 videoFile 目录是否有图片文件
- 确保文件名正确（包括扩展名）

### 问题3: 后端服务无法连接
- 检查服务是否运行：`ps aux | grep sau_backend`
- 检查端口是否被占用：`lsof -i :5409`
- 查看服务日志

### 问题4: 发布失败
- 查看后端日志了解详细错误信息
- 检查cookie文件是否有效
- 检查图片文件是否存在且可读

