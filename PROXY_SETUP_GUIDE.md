# 代理服务器配置指南

## 🌐 网络架构

```
Windows 服务器 (39.105.227.6)
    ↓
代理服务器 (150.107.38.113)
    ↓ V2Ray (SOCKS5: 10809) + Privoxy (HTTP: 8118)
    ↓
互联网 (Google 等服务)
```

## ✅ 当前状态

### 代理服务器 (150.107.38.113)
- ✅ V2Ray 运行正常 (SOCKS5: 10809)
- ✅ Privoxy HTTP 代理运行正常 (8118端口)
- ✅ 可以成功访问 Google 等外网服务

### Windows 服务器 (39.105.227.6)
- ✅ 后端服务运行正常 (端口 5409)
- ✅ 前端服务运行正常 (端口 5173)
- ⚠️  代理连接受阿里云安全组限制

## ⚠️ 当前问题

**无法从 Windows 服务器直接访问代理服务器的 8118 端口**

原因：阿里云安全组规则阻止了外部访问。

## 🔧 解决方案

### 方案 1：配置阿里云安全组（推荐）

1. 登录[阿里云控制台](https://ecs.console.aliyun.com/)
2. 找到代理服务器 `150.107.38.113` 的安全组设置
3. 添加入方向规则：
   - 端口范围：`8118/8118`
   - 授权对象：`39.105.227.6/32` （只允许 Windows 服务器访问）
   - 协议：TCP
   - 优先级：1

**完成后测试：**
```powershell
# 在 Windows 服务器上运行
Test-NetConnection -ComputerName 150.107.38.113 -Port 8118
```

### 方案 2：使用 SSH 隧道

在 Windows 服务器上建立 SSH 隧道：

1. 创建文件 `C:\social-auto-upload-window\setup_proxy_tunnel.ps1`：

```powershell
# 启动 SSH 隧道
Write-Host "正在建立 SSH 隧道..." -ForegroundColor Cyan

# 检查是否已有隧道
$existing = Get-Process ssh -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*7890*"}
if ($existing) {
    Write-Host "SSH 隧道已在运行" -ForegroundColor Green
    exit 0
}

# 启动隧道（需要手动输入密码：15831929073asAS）
ssh -L 7890:127.0.0.1:8118 ubuntu@150.107.38.113 -N
```

2. 修改 `conf.py`：

```python
HTTP_PROXY = 'http://127.0.0.1:7890'
HTTPS_PROXY = 'http://127.0.0.1:7890'
```

3. 启动服务：

```batch
REM 终端1：启动 SSH 隧道
powershell -ExecutionPolicy Bypass -File setup_proxy_tunnel.ps1

REM 终端2：启动服务
python sau_backend.py
```

### 方案 3：直接连接（已启用）

代码已包含以下容错机制：
- 自动重试（最多3次）
- SSL 验证可选
- 连接超时15分钟

**优点：** 无需额外配置
**缺点：** 下载速度可能较慢，且可能失败

## 📝 配置文件状态

### conf.py
```python
HTTP_PROXY = 'http://127.0.0.1:7890'  # 已添加
HTTPS_PROXY = 'http://127.0.0.1:7890'  # 已添加
```

## 🧪 测试代理

### 在代理服务器上测试
```bash
ssh ubuntu@150.107.38.113
curl -x http://127.0.0.1:8118 https://www.google.com -I
```

### 在 Windows 服务器上测试
```powershell
# 测试网络连通性
Test-NetConnection -ComputerName 150.107.38.113 -Port 8118

# 测试代理（如果端口可访问）
$env:HTTP_PROXY="http://150.107.38.113:8118"
curl -x $env:HTTP_PROXY https://www.google.com -I
```

## 📞 联系信息

- 代理服务器：150.107.38.113
  - 用户：ubuntu
  - V2Ray SOCKS5：10809
  - Privoxy HTTP：8118

- Windows 服务器：39.105.227.6  
  - 用户：administrator
  - 后端：5409
  - 前端：5173

## 🔍 故障排查

### 1. 检查代理服务状态
```bash
ssh ubuntu@150.107.38.113
sudo systemctl status privoxy
ps aux | grep v2ray
```

### 2. 检查端口监听
```bash
ss -tlnp | grep -E '8118|10809'
```

### 3. 测试代理功能
```bash
curl -x http://127.0.0.1:8118 https://www.google.com -I
```

### 4. 查看日志
```bash
# Privoxy 日志
tail -f /var/log/privoxy/logfile

# V2Ray 日志  
journalctl -u v2ray -f
```

## 📅 维护记录

- 2025-12-24: 初始配置完成
  - ✅ V2Ray 运行正常
  - ✅ Privoxy 安装并配置
  - ⚠️  需要配置阿里云安全组规则

