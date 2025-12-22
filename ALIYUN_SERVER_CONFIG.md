# 阿里云 Windows 服务器配置总结

## ✅ 已完成的配置

### 1. 代理配置
- **配置文件**: `C:\social-auto-upload-window\conf.py`
- **HTTP_PROXY**: `http://150.107.38.113:10810`
- **HTTPS_PROXY**: `http://150.107.38.113:10810`

### 2. 后端代码优化
- **文件**: `C:\social-auto-upload-window\sau_backend.py`
- **改进内容**:
  - ✅ 优化代理配置逻辑
  - ✅ 改进错误处理和日志输出
  - ✅ 增强重试机制
  - ✅ 支持代理不可用时的降级处理

### 3. 下载功能增强
- ✅ 自动使用代理访问 Google Cloud Storage
- ✅ 支持 SSL 验证绕过（国内服务器需要）
- ✅ 增强的重试机制（最多 3 次）
- ✅ 更大的超时时间（连接 60 秒，读取 900 秒）
- ✅ 文件完整性验证

---

## ⚠️ 当前状态

### 代理连接状态
- **状态**: ❌ 连接超时
- **原因**: 云服务商安全组未配置
- **影响**: 无法通过代理访问 Google 服务

### 测试结果
```
[1/3] 测试代理服务器连接...
❌ 连接失败: Connection to 150.107.38.113 timed out

[2/3] 测试 Google Cloud Storage 连接...
❌ 连接失败: Connection to 150.107.38.113 timed out

[3/3] 检查配置文件...
HTTP_PROXY: http://150.107.38.113:10810
HTTPS_PROXY: http://150.107.38.113:10810
✅ 配置正确
```

---

## 🔧 下一步操作

### 1. 配置云服务商安全组（必须）

这是最关键的一步！需要开放代理服务器的端口。

#### 操作步骤：
1. 登录管理 `150.107.38.113` 的云服务商控制台
2. 找到该服务器的安全组/防火墙设置
3. 添加入站规则：
   - **端口**: `10810` (TCP)
   - **协议**: TCP
   - **源地址**: `39.105.227.6/32` (仅允许阿里云服务器) 或 `0.0.0.0/0` (允许所有，安全性较低)
   - **描述**: HTTP 代理端口

#### 不同云服务商的配置位置：
- **阿里云**: 云服务器 ECS → 网络与安全 → 安全组
- **腾讯云**: 云服务器 CVM → 安全组
- **AWS**: EC2 → Security Groups
- **Azure**: Network Security Groups
- **Google Cloud**: VPC Network → Firewall rules

### 2. 验证代理连接

配置安全组后，运行测试脚本：

```powershell
# 在阿里云服务器上执行
python C:\temp\test_proxy.py
```

预期输出：
```
[1/3] 测试代理服务器连接...
[OK] 连接成功，状态码: 200

[2/3] 测试 Google Cloud Storage 连接...
[OK] 连接成功，状态码: 200
```

### 3. 重启后端服务

配置完成后，重启后端服务使配置生效：

```powershell
# 如果使用 PM2
pm2 restart sau_backend

# 或者直接运行
cd C:\social-auto-upload-window
python sau_backend.py
```

### 4. 测试视频下载功能

通过前端或 API 测试视频下载功能：

```bash
curl -X POST http://39.105.227.6:5409/api/postVideo \
  -H "Content-Type: application/json" \
  -d '{
    "type": 1,
    "title": "测试视频",
    "fileList": ["https://storage.googleapis.com/your-bucket/video.mp4"],
    ...
  }'
```

---

## 📋 配置检查清单

- [x] 代理服务器已搭建（150.107.38.113:10810）
- [x] 阿里云服务器配置文件已更新
- [x] 后端代码已优化
- [ ] **云服务商安全组已配置** ⚠️ **必须完成**
- [ ] 代理连接测试通过
- [ ] 后端服务已重启
- [ ] 视频下载功能测试通过

---

## 🐛 故障排查

### 问题 1: 代理连接超时

**症状**: `Connection to 150.107.38.113 timed out`

**可能原因**:
1. 安全组未配置（最常见）
2. 代理服务器防火墙阻止
3. 代理服务未运行

**解决方法**:
1. 检查安全组配置
2. 在代理服务器上检查服务状态：`sudo systemctl status v2ray`
3. 检查端口监听：`sudo netstat -tlnp | grep 10810`

### 问题 2: SSL 错误

**症状**: `SSL: CERTIFICATE_VERIFY_FAILED`

**解决方法**: 
- 代码已自动处理，会禁用 SSL 验证（`verify=False`）
- 这是正常的，因为国内服务器访问 Google 服务经常遇到 SSL 问题

### 问题 3: 下载失败但代理连接正常

**可能原因**:
1. 视频 URL 无效
2. 文件太大，超时
3. 网络不稳定

**解决方法**:
- 检查视频 URL 是否可访问
- 查看后端日志了解详细错误
- 代码已实现自动重试（最多 3 次）

---

## 📚 相关文档

- `PROXY_SERVER_SETUP.md` - 代理服务器搭建文档
- `GOOGLE_ACCESS_SOLUTION.md` - Google 访问解决方案
- `test_proxy.py` - 代理连接测试脚本

---

## 💡 提示

1. **安全组配置是关键**：即使所有代码都正确，如果安全组未配置，代理也无法工作
2. **测试脚本位置**：`C:\temp\test_proxy.py`
3. **配置文件位置**：`C:\social-auto-upload-window\conf.py`
4. **后端日志**：查看后端运行时的输出，了解代理使用情况

---

**最后更新**: 2025-12-17
**状态**: 等待安全组配置

