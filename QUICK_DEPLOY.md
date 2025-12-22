# 🚀 快速部署指南

## 📦 需要上传的文件

将以下文件上传到服务器 `C:\temp\` 目录：

1. ✅ `social-auto-upload-window-deploy.zip` (317MB)
2. ✅ `deploy_on_windows.bat`
3. ⚪ `check_server_environment.bat` (可选，用于环境检查)

**文件位置**：
- Mac: `~/social-auto-upload-window-deploy.zip`
- Mac: 项目目录中的 `deploy_on_windows.bat`

## 🔧 部署步骤

### 1. 连接服务器
```
远程桌面地址: 39.105.227.6:3389
用户名: administrator
密码: 15831929073asAS
```

### 2. 上传文件
- 使用远程桌面的驱动器映射功能
- 或使用网盘/云存储中转

### 3. 执行部署
在服务器 CMD 中执行：
```cmd
cd C:\temp
deploy_on_windows.bat
```

### 4. 启动服务
部署完成后：
```cmd
cd C:\social-auto-upload-window
start-win.bat
```

## ✅ 验证部署

访问以下地址：
- 前端: http://39.105.227.6:5173
- 后端: http://39.105.227.6:5409/getAccounts

## 🆘 常见问题

### 端口被占用
```cmd
netstat -ano | findstr ":5409"
netstat -ano | findstr ":5173"
```

### 防火墙问题
确保 Windows 防火墙和阿里云安全组都开放了 5173 和 5409 端口

### 依赖安装失败
使用镜像源重试：
```cmd
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
npm install --registry https://registry.npmmirror.com
```

