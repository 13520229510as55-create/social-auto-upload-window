#!/bin/bash
# 部署脚本：将项目部署到阿里云 Windows 服务器

SERVER_IP="39.105.227.6"
SERVER_USER="administrator"
SERVER_PASS="15831929073asAS"
SERVER_PORT="3389"
REMOTE_DIR="C:\\social-auto-upload-window"

echo "=========================================="
echo "🚀 开始部署到 Windows 服务器"
echo "服务器: ${SERVER_IP}:${SERVER_PORT}"
echo "=========================================="
echo ""

# 检查必要工具
if ! command -v zip &> /dev/null; then
    echo "❌ 错误: 需要安装 zip 工具"
    exit 1
fi

# 1. 打包项目（排除不必要的文件）
echo "📦 [1/4] 打包项目..."
cd "$(dirname "$0")"
PROJECT_DIR="social-auto-upload-window"
ZIP_FILE="social-auto-upload-window-deploy.zip"

# 创建临时目录
TEMP_DIR=$(mktemp -d)
cp -r . "$TEMP_DIR/$PROJECT_DIR" 2>/dev/null || {
    echo "❌ 复制项目文件失败"
    exit 1
}

# 排除不需要的文件
cd "$TEMP_DIR/$PROJECT_DIR"
rm -rf .git
rm -rf node_modules
rm -rf venv
rm -rf __pycache__
rm -rf .vscode
rm -rf *.log
rm -rf screenshots
rm -rf restore_working_version.tar.gz
rm -rf xvfb_changes.tar.gz
rm -rf xvfb_helper.tar.gz

# 打包
cd "$TEMP_DIR"
zip -r "$ZIP_FILE" "$PROJECT_DIR" > /dev/null
mv "$ZIP_FILE" ~/

echo "✅ 打包完成: ~/$ZIP_FILE"
echo ""

# 2. 上传到服务器
echo "📤 [2/4] 上传到服务器..."
echo "   目标路径: ${REMOTE_DIR}"

# 使用 scp 上传（需要服务器开启 SSH）
# 如果 Windows 服务器没有 SSH，可以使用其他方式
if command -v scp &> /dev/null; then
    # 尝试通过 SSH 上传
    echo "   使用 SCP 上传..."
    sshpass -p "$SERVER_PASS" scp -P 22 -o StrictHostKeyChecking=no ~/$ZIP_FILE "${SERVER_USER}@${SERVER_IP}:C:\\temp\\$ZIP_FILE" 2>&1 || {
        echo "⚠️  SCP 上传失败，请手动上传文件"
        echo ""
        echo "📋 手动上传步骤："
        echo "   1. 文件位置: ~/$ZIP_FILE"
        echo "   2. 使用远程桌面连接到服务器"
        echo "   3. 将文件复制到服务器 C:\\temp\\ 目录"
        echo "   4. 在服务器上解压到: ${REMOTE_DIR}"
        echo ""
        read -p "按 Enter 继续（假设文件已上传）..."
    }
else
    echo "⚠️  未找到 scp 工具，请手动上传文件"
    echo ""
    echo "📋 手动上传步骤："
    echo "   1. 文件位置: ~/$ZIP_FILE"
    echo "   2. 使用远程桌面连接到服务器"
    echo "   3. 将文件复制到服务器 C:\\temp\\ 目录"
    echo "   4. 在服务器上解压到: ${REMOTE_DIR}"
    echo ""
    read -p "按 Enter 继续（假设文件已上传）..."
fi

echo ""

# 3. 生成服务器端部署脚本
echo "📝 [3/4] 生成服务器端部署脚本..."
DEPLOY_SCRIPT="deploy_on_windows.ps1"

cat > "$TEMP_DIR/$DEPLOY_SCRIPT" << 'DEPLOY_EOF'
# PowerShell 部署脚本
# 在 Windows 服务器上执行此脚本

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🚀 开始部署 social-auto-upload-window" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$PROJECT_DIR = "C:\social-auto-upload-window"
$ZIP_FILE = "C:\temp\social-auto-upload-window-deploy.zip"

# 1. 检查并解压文件
Write-Host "[1/5] 检查部署文件..." -ForegroundColor Yellow
if (-not (Test-Path $ZIP_FILE)) {
    Write-Host "❌ 错误: 找不到部署文件 $ZIP_FILE" -ForegroundColor Red
    Write-Host "请确保文件已上传到服务器" -ForegroundColor Red
    exit 1
}

Write-Host "[2/5] 解压文件到 $PROJECT_DIR..." -ForegroundColor Yellow
if (Test-Path $PROJECT_DIR) {
    Write-Host "   备份现有目录..." -ForegroundColor Gray
    $BACKUP_DIR = "$PROJECT_DIR_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Move-Item -Path $PROJECT_DIR -Destination $BACKUP_DIR -Force
}

New-Item -ItemType Directory -Path $PROJECT_DIR -Force | Out-Null
Expand-Archive -Path $ZIP_FILE -DestinationPath "C:\temp\extracted" -Force
Move-Item -Path "C:\temp\extracted\social-auto-upload-window\*" -Destination $PROJECT_DIR -Force
Remove-Item -Path "C:\temp\extracted" -Recurse -Force

Write-Host "✅ 解压完成" -ForegroundColor Green
Write-Host ""

# 2. 检查 Python
Write-Host "[3/5] 检查 Python 环境..." -ForegroundColor Yellow
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "❌ 错误: 未找到 Python" -ForegroundColor Red
    Write-Host "请先安装 Python 3.10+" -ForegroundColor Red
    exit 1
}

$pythonVersion = python --version
Write-Host "   $pythonVersion" -ForegroundColor Gray

# 3. 安装 Python 依赖
Write-Host "[4/5] 安装 Python 依赖（使用清华源）..." -ForegroundColor Yellow
Set-Location $PROJECT_DIR
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 安装 Playwright 浏览器
Write-Host "   安装 Playwright 浏览器..." -ForegroundColor Gray
python -m playwright install chromium

Write-Host "✅ Python 依赖安装完成" -ForegroundColor Green
Write-Host ""

# 4. 检查 Node.js
Write-Host "[5/5] 检查 Node.js 环境..." -ForegroundColor Yellow
$nodeCmd = Get-Command node -ErrorAction SilentlyContinue
if (-not $nodeCmd) {
    Write-Host "⚠️  警告: 未找到 Node.js" -ForegroundColor Yellow
    Write-Host "前端服务将无法启动，请先安装 Node.js LTS" -ForegroundColor Yellow
} else {
    $nodeVersion = node --version
    Write-Host "   Node.js $nodeVersion" -ForegroundColor Gray
    
    # 安装前端依赖
    Write-Host "   安装前端依赖..." -ForegroundColor Gray
    Set-Location "$PROJECT_DIR\sau_frontend"
    npm install --registry https://registry.npmmirror.com
    
    Write-Host "✅ 前端依赖安装完成" -ForegroundColor Green
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ 部署完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 启动服务：" -ForegroundColor Yellow
Write-Host "   方法1: 双击 start-win.bat" -ForegroundColor Gray
Write-Host "   方法2: 在项目目录执行:" -ForegroundColor Gray
Write-Host "          python sau_backend.py" -ForegroundColor Gray
Write-Host "          (新窗口) cd sau_frontend && npm run dev -- --host 0.0.0.0" -ForegroundColor Gray
Write-Host ""
Write-Host "🌐 访问地址：" -ForegroundColor Yellow
Write-Host "   前端: http://$env:COMPUTERNAME:5173" -ForegroundColor Gray
Write-Host "   后端: http://$env:COMPUTERNAME:5409" -ForegroundColor Gray
Write-Host ""
DEPLOY_EOF

mv "$TEMP_DIR/$DEPLOY_SCRIPT" ~/
echo "✅ 部署脚本已生成: ~/$DEPLOY_SCRIPT"
echo ""

# 清理临时文件
rm -rf "$TEMP_DIR"

echo "=========================================="
echo "✅ 准备完成！"
echo "=========================================="
echo ""
echo "📋 下一步操作："
echo ""
echo "1. 如果文件已自动上传，在服务器上执行："
echo "   PowerShell -ExecutionPolicy Bypass -File C:\\temp\\deploy_on_windows.ps1"
echo ""
echo "2. 如果文件未自动上传，请："
echo "   a) 使用远程桌面连接到服务器 (${SERVER_IP}:${SERVER_PORT})"
echo "   b) 将 ~/$ZIP_FILE 复制到服务器 C:\\temp\\ 目录"
echo "   c) 将 ~/$DEPLOY_SCRIPT 复制到服务器 C:\\temp\\ 目录"
echo "   d) 在服务器 PowerShell 中执行："
echo "      PowerShell -ExecutionPolicy Bypass -File C:\\temp\\deploy_on_windows.ps1"
echo ""
echo "3. 部署完成后，在服务器上运行 start-win.bat 启动服务"
echo ""
echo "📁 文件位置："
echo "   部署包: ~/$ZIP_FILE"
echo "   部署脚本: ~/$DEPLOY_SCRIPT"
echo ""

