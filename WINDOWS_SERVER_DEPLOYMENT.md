# Windows 服务器部署指南

## 📋 服务器信息
- **IP**: 39.105.227.6
- **端口**: 3389 (RDP)
- **账号**: administrator
- **密码**: 15831929073asAS

## 🚀 部署步骤

### 第一步：准备部署文件（已在 Mac 本地完成）

部署文件已生成在：
- **部署包**: `~/social-auto-upload-window-deploy.zip`
- **部署脚本**: `~/deploy_on_windows.bat` (或 `deploy_on_windows.ps1`)

### 第二步：上传文件到服务器

1. **使用远程桌面连接服务器**
   - 打开"远程桌面连接"（Windows）或 Microsoft Remote Desktop（Mac）
   - 输入服务器地址：`39.105.227.6:3389`
   - 用户名：`administrator`
   - 密码：`15831929073asAS`

2. **上传文件**
   - 将以下文件从 Mac 复制到服务器：
     - `~/social-auto-upload-window-deploy.zip` → `C:\temp\social-auto-upload-window-deploy.zip`
     - `deploy_on_windows.bat` → `C:\temp\deploy_on_windows.bat`

   **方法1：使用远程桌面的文件共享**
   - 在远程桌面连接时，勾选"本地资源" → "驱动器"
   - 连接后，在服务器上打开"此电脑"，可以看到你的 Mac 磁盘
   - 直接复制文件到 `C:\temp\`

   **方法2：使用网盘/云存储**
   - 将文件上传到网盘（OneDrive、百度网盘等）
   - 在服务器上下载到 `C:\temp\`

### 第三步：在服务器上执行部署

1. **打开 PowerShell 或 CMD（以管理员身份运行）**

2. **执行部署脚本**
   ```cmd
   cd C:\temp
   deploy_on_windows.bat
   ```

   或者使用 PowerShell：
   ```powershell
   cd C:\temp
   .\deploy_on_windows.bat
   ```

3. **等待部署完成**
   - 脚本会自动：
     - 解压项目文件到 `C:\social-auto-upload-window`
     - 检查并安装 Python 依赖（使用清华源）
     - 检查并安装 Node.js 依赖（使用淘宝镜像）
     - 安装 Playwright 浏览器驱动

### 第四步：启动服务

部署完成后，有两种启动方式：

#### 方法1：使用启动脚本（推荐）
```cmd
cd C:\social-auto-upload-window
start-win.bat
```
这会自动打开两个窗口：
- 后端服务（端口 5409）
- 前端服务（端口 5173）

#### 方法2：手动启动
**启动后端**（在一个 CMD 窗口）：
```cmd
cd C:\social-auto-upload-window
python sau_backend.py
```

**启动前端**（在另一个 CMD 窗口）：
```cmd
cd C:\social-auto-upload-window\sau_frontend
npm run dev -- --host 0.0.0.0
```

### 第五步：配置防火墙

确保 Windows 防火墙允许以下端口：
- **5173** (前端)
- **5409** (后端)

**配置方法**：
1. 打开"Windows Defender 防火墙"
2. 点击"高级设置"
3. 点击"入站规则" → "新建规则"
4. 选择"端口" → 输入端口号（5173 或 5409）
5. 允许连接 → 完成

### 第六步：访问服务

在浏览器中访问：
- **前端**: `http://39.105.227.6:5173`
- **后端 API**: `http://39.105.227.6:5409`

## 🔧 环境要求

### 必需软件

1. **Python 3.10+**
   - 下载：https://www.python.org/downloads/
   - 安装时勾选"Add Python to PATH"

2. **Node.js LTS (18.x 或 20.x)**
   - 下载：https://nodejs.org/
   - 安装后验证：`node --version`

### 可选：配置 Python 镜像源（永久）

创建文件 `%APPDATA%\pip\pip.ini`：
```ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
timeout = 120
```

## 📝 常见问题

### 1. 端口被占用
如果 5173 或 5409 端口被占用：
```cmd
netstat -ano | findstr :5173
netstat -ano | findstr :5409
```
找到进程 ID 后，结束进程或修改端口配置。

### 2. 无法访问服务
- 检查防火墙设置
- 检查服务是否正常启动
- 检查阿里云安全组是否开放端口

### 3. Python 模块安装失败
使用清华源重试：
```cmd
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 4. Playwright 浏览器安装失败
手动安装：
```cmd
python -m playwright install chromium
```

## 🔄 更新代码

如果后续需要更新代码：

1. 在 Mac 上重新运行部署脚本生成新的部署包
2. 上传新的 `social-auto-upload-window-deploy.zip` 到服务器
3. 在服务器上重新执行 `deploy_on_windows.bat`

或者使用 Git（如果服务器已安装）：
```cmd
cd C:\social-auto-upload-window
git pull
```

## 📞 技术支持

如果遇到问题，请检查：
1. 服务日志（CMD 窗口中的输出）
2. 防火墙和安全组配置
3. Python 和 Node.js 版本是否正确

