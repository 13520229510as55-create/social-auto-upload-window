# 阿里云服务器访问 Google Cloud Storage 解决方案

## 问题说明

国内服务器（如阿里云）无法直接访问 Google Cloud Storage，会遇到以下问题：
- SSL 握手失败
- 连接被重置 (10054)
- 网络超时
- 防火墙阻止

## 解决方案

### 方案 1: 使用代理服务器（推荐）

#### 1.1 配置代理

编辑 `conf.py` 文件，添加代理配置：

```python
# 代理配置
HTTP_PROXY = "http://your_proxy_host:proxy_port"  # 例如: http://127.0.0.1:7890
HTTPS_PROXY = "http://your_proxy_host:proxy_port"  # 或使用环境变量
```

#### 1.2 使用环境变量（推荐）

在 Windows 服务器上设置环境变量：

```cmd
set HTTP_PROXY=http://your_proxy_host:proxy_port
set HTTPS_PROXY=http://your_proxy_host:proxy_port
```

或者在 PowerShell 中：

```powershell
$env:HTTP_PROXY="http://your_proxy_host:proxy_port"
$env:HTTPS_PROXY="http://your_proxy_host:proxy_port"
```

#### 1.3 代理服务器选择

**选项 A: 使用本地代理软件**
- Clash for Windows
- V2Ray
- Shadowsocks
- 通常监听在 `127.0.0.1:7890` 或类似端口

**选项 B: 使用云代理服务**
- 购买支持 Google 访问的代理服务
- 配置代理地址和端口

**选项 C: 自建代理服务器**
- 在海外服务器上搭建代理
- 配置代理地址供国内服务器使用

### 方案 2: 使用 VPN

在 Windows 服务器上安装 VPN 客户端，全局代理所有流量。

### 方案 3: 使用中转服务器

1. 在可访问 Google 的服务器上下载文件
2. 通过 SCP/FTP 传输到阿里云服务器
3. 在阿里云服务器上使用本地文件

### 方案 4: 迁移到国内存储服务

将文件从 Google Cloud Storage 迁移到：
- 阿里云 OSS
- 腾讯云 COS
- 七牛云
- 其他国内对象存储服务

## 快速配置步骤

### 步骤 1: 安装代理软件（如果使用本地代理）

1. 下载并安装 Clash for Windows 或其他代理软件
2. 配置代理规则，确保可以访问 Google 服务
3. 启动代理服务，记录代理端口（通常是 7890）

### 步骤 2: 配置 conf.py

编辑 `C:\social-auto-upload-window\conf.py`：

```python
# 代理配置
HTTP_PROXY = "http://127.0.0.1:7890"  # 根据实际代理端口修改
HTTPS_PROXY = "http://127.0.0.1:7890"
```

### 步骤 3: 重启后端服务

重启后端服务使配置生效。

## 测试代理是否工作

在服务器上运行以下命令测试：

```python
import requests
proxies = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890'
}
response = requests.get('https://storage.googleapis.com', proxies=proxies, timeout=10, verify=False)
print(f"状态码: {response.status_code}")
```

如果返回 200 或 403（而不是连接错误），说明代理工作正常。

## 注意事项

1. **代理性能**: 使用代理会增加下载时间，特别是大文件
2. **代理稳定性**: 确保代理服务稳定，避免下载中断
3. **安全性**: 如果使用第三方代理，注意数据安全
4. **成本**: 代理服务可能需要付费

## 当前代码已支持

✅ 自动检测代理配置
✅ 支持 HTTP 和 HTTPS 代理
✅ 自动应用到所有 Google 服务请求
✅ 禁用 SSL 验证（避免 SSL 握手问题）

## 推荐方案

对于生产环境，推荐：
1. **短期**: 使用代理服务器（方案 1）
2. **长期**: 迁移到国内存储服务（方案 4）

