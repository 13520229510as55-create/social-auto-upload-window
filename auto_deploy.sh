#!/bin/bash
# 自动化部署脚本 - 尝试多种方式连接到 Windows 服务器并部署

SERVER_IP="39.105.227.6"
SERVER_USER="administrator"
SERVER_PASS="15831929073asAS"
REMOTE_DIR="C:\\social-auto-upload-window"
TEMP_DIR="C:\\temp"

echo "=========================================="
echo "🚀 自动化部署到 Windows 服务器"
echo "服务器: ${SERVER_IP}"
echo "=========================================="
echo ""

# 检查必要文件
ZIP_FILE="$HOME/social-auto-upload-window-deploy.zip"
DEPLOY_BAT="deploy_on_windows.bat"

if [ ! -f "$ZIP_FILE" ]; then
    echo "❌ 错误: 找不到部署包 $ZIP_FILE"
    echo "正在重新生成..."
    ./deploy_to_windows_server.sh
    ZIP_FILE="$HOME/social-auto-upload-window-deploy.zip"
fi

if [ ! -f "$DEPLOY_BAT" ]; then
    echo "❌ 错误: 找不到部署脚本 $DEPLOY_BAT"
    exit 1
fi

echo "✅ 部署文件检查完成"
echo ""

# 方法1: 尝试 SSH 连接（如果服务器开启了 SSH）
echo "[方法1] 尝试通过 SSH 连接..."
if sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 "${SERVER_USER}@${SERVER_IP}" "echo 'SSH连接成功'" 2>/dev/null; then
    echo "✅ SSH 连接成功，开始上传文件..."
    
    # 创建临时目录
    sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no "${SERVER_USER}@${SERVER_IP}" "mkdir -p ${TEMP_DIR//\\/\/}" 2>/dev/null
    
    # 上传文件
    echo "📤 上传部署包..."
    sshpass -p "$SERVER_PASS" scp -o StrictHostKeyChecking=no "$ZIP_FILE" "${SERVER_USER}@${SERVER_IP}:${TEMP_DIR//\\/\/}/" 2>&1
    
    echo "📤 上传部署脚本..."
    sshpass -p "$SERVER_PASS" scp -o StrictHostKeyChecking=no "$DEPLOY_BAT" "${SERVER_USER}@${SERVER_IP}:${TEMP_DIR//\\/\/}/" 2>&1
    
    echo "✅ 文件上传完成"
    echo ""
    echo "📋 请在服务器上执行以下命令完成部署："
    echo "   cd ${TEMP_DIR}"
    echo "   deploy_on_windows.bat"
    exit 0
else
    echo "⚠️  SSH 连接失败（服务器可能未开启 SSH）"
fi
echo ""

# 方法2: 尝试 WinRM (PowerShell Remoting)
echo "[方法2] 尝试通过 WinRM 连接..."
if command -v pwsh &> /dev/null || command -v powershell &> /dev/null; then
    echo "检测到 PowerShell，尝试 WinRM 连接..."
    # WinRM 需要服务器预先配置，这里先跳过
    echo "⚠️  WinRM 需要服务器预先配置，跳过"
else
    echo "⚠️  未找到 PowerShell，跳过 WinRM"
fi
echo ""

# 方法3: 使用 SMB 共享（如果可用）
echo "[方法3] 尝试通过 SMB 共享上传..."
if command -v smbclient &> /dev/null; then
    echo "检测到 smbclient，尝试 SMB 连接..."
    # 尝试连接 SMB
    if smbclient "//${SERVER_IP}/C$" -U "${SERVER_USER}%${SERVER_PASS}" -c "mkdir temp 2>/dev/null; put $ZIP_FILE temp/social-auto-upload-window-deploy.zip; put $DEPLOY_BAT temp/deploy_on_windows.bat; exit" 2>/dev/null; then
        echo "✅ 通过 SMB 上传成功"
        echo ""
        echo "📋 请在服务器上执行以下命令完成部署："
        echo "   cd C:\\temp"
        echo "   deploy_on_windows.bat"
        exit 0
    else
        echo "⚠️  SMB 连接失败"
    fi
else
    echo "⚠️  未安装 smbclient，跳过 SMB"
fi
echo ""

# 如果所有自动方式都失败，提供手动步骤
echo "=========================================="
echo "⚠️  自动连接失败，请使用手动方式部署"
echo "=========================================="
echo ""
echo "📋 手动部署步骤："
echo ""
echo "1. 使用远程桌面连接到服务器："
echo "   地址: ${SERVER_IP}:3389"
echo "   用户名: ${SERVER_USER}"
echo "   密码: ${SERVER_PASS}"
echo ""
echo "2. 上传以下文件到服务器 C:\\temp\\ 目录："
echo "   - ${ZIP_FILE}"
echo "   - ${DEPLOY_BAT}"
echo ""
echo "3. 在服务器 CMD 中执行："
echo "   cd C:\\temp"
echo "   deploy_on_windows.bat"
echo ""
echo "4. 部署完成后，启动服务："
echo "   cd C:\\social-auto-upload-window"
echo "   start-win.bat"
echo ""
echo "📁 文件位置："
echo "   部署包: ${ZIP_FILE}"
echo "   部署脚本: $(pwd)/${DEPLOY_BAT}"
echo ""

