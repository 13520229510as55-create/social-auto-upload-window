# Windows 服务器安装 OpenSSH 服务器指南

## 🎯 目标
安装 OpenSSH 服务器后，可以通过 SSH 直接连接服务器并自动部署项目。

## 📋 安装方法

### 方法1：使用安装脚本（推荐）

1. **将以下文件上传到服务器**：
   - `install_openssh_server.bat` 或 `install_openssh_server.ps1`

2. **在服务器上以管理员身份运行**：
   ```cmd
   REM 右键点击 install_openssh_server.bat
   REM 选择"以管理员身份运行"
   ```
   或
   ```powershell
   PowerShell -ExecutionPolicy Bypass -File install_openssh_server.ps1
   ```

### 方法2：手动安装（图形界面）

1. **打开设置**
   - 按 `Win + I` 打开 Windows 设置
   - 或点击"开始" → "设置"

2. **进入可选功能**
   - 点击"应用"
   - 点击"可选功能"

3. **安装 OpenSSH 服务器**
   - 点击"查看功能"或"添加功能"
   - 搜索"OpenSSH 服务器"
   - 勾选并点击"安装"

4. **启动服务**
   - 按 `Win + R`，输入 `services.msc`
   - 找到"OpenSSH SSH Server"
   - 右键 → "属性" → 启动类型改为"自动"
   - 点击"启动"

5. **配置防火墙**
   - 打开"Windows Defender 防火墙"
   - 点击"高级设置"
   - 点击"入站规则" → "新建规则"
   - 选择"端口" → TCP → 端口 22
   - 允许连接 → 完成

### 方法3：使用 PowerShell 命令

以管理员身份打开 PowerShell，执行：

```powershell
# 安装 OpenSSH 服务器
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0

# 启动服务并设置为自动启动
Start-Service sshd
Set-Service -Name sshd -StartupType 'Automatic'

# 添加防火墙规则
New-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -DisplayName "OpenSSH Server (sshd)" -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
```

## ✅ 验证安装

### 1. 检查服务状态
```cmd
sc query sshd
```
应该显示 `STATE: RUNNING`

### 2. 检查端口监听
```cmd
netstat -ano | findstr :22
```
应该显示 `0.0.0.0:22` 正在监听

### 3. 测试连接（从 Mac）
```bash
ssh administrator@39.105.227.6
```
如果提示输入密码，说明安装成功！

## 🔒 安全配置（可选但推荐）

### 1. 修改默认端口（可选）
编辑 `C:\ProgramData\ssh\sshd_config`：
```
Port 2222  # 改为其他端口
```
然后重启服务：
```cmd
net stop sshd
net start sshd
```

### 2. 禁用密码登录，使用密钥（推荐）
在 Mac 上生成密钥：
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

将公钥复制到服务器：
```bash
ssh-copy-id administrator@39.105.227.6
```

## 🌐 配置阿里云安全组

1. 登录阿里云控制台
2. 进入"云服务器 ECS" → "网络与安全" → "安全组"
3. 找到你的服务器对应的安全组
4. 添加规则：
   - 规则方向：入方向
   - 协议类型：TCP
   - 端口范围：22/22
   - 授权对象：0.0.0.0/0（或你的 IP）

## 🚀 安装完成后

一旦 OpenSSH 服务器安装完成并可以连接，我就可以直接通过 SSH 自动部署项目了！

执行以下命令测试连接：
```bash
ssh administrator@39.105.227.6
```

如果连接成功，告诉我，我会立即开始自动部署！

