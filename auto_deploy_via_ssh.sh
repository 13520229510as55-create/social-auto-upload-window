#!/bin/bash
# 通过 SSH 自动部署脚本
# 前提：Windows 服务器已安装并启动 OpenSSH 服务器

SERVER_IP="39.105.227.6"
SERVER_USER="administrator"
SERVER_PASS="15831929073asAS"
REMOTE_DIR="C:\\social-auto-upload-window"
TEMP_DIR="C:\\temp"

echo "=========================================="
echo "🚀 通过 SSH 自动部署到 Windows 服务器"
echo "=========================================="
echo ""

# 检查必要文件
ZIP_FILE="$HOME/social-auto-upload-window-deploy.zip"
DEPLOY_BAT="deploy_on_windows.bat"

if [ ! -f "$ZIP_FILE" ]; then
    echo "❌ 错误: 找不到部署包，正在重新生成..."
    ./deploy_to_windows_server.sh
    ZIP_FILE="$HOME/social-auto-upload-window-deploy.zip"
fi

if [ ! -f "$DEPLOY_BAT" ]; then
    echo "❌ 错误: 找不到部署脚本 $DEPLOY_BAT"
    exit 1
fi

echo "✅ 部署文件检查完成"
echo ""

# 测试 SSH 连接
echo "[1/6] 测试 SSH 连接..."
if sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 "${SERVER_USER}@${SERVER_IP}" "echo 'SSH连接成功'" 2>/dev/null; then
    echo "✅ SSH 连接成功！"
else
    echo "❌ SSH 连接失败"
    echo ""
    echo "请确保："
    echo "1. OpenSSH 服务器已安装并运行"
    echo "2. 阿里云安全组已开放 22 端口"
    echo "3. Windows 防火墙已允许 SSH 连接"
    echo ""
    echo "测试连接命令："
    echo "  ssh ${SERVER_USER}@${SERVER_IP}"
    exit 1
fi
echo ""

# 创建临时目录
echo "[2/6] 创建服务器临时目录..."
sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no "${SERVER_USER}@${SERVER_IP}" "if not exist ${TEMP_DIR} mkdir ${TEMP_DIR}" 2>/dev/null
echo "✅ 临时目录已创建"
echo ""

# 上传部署包
echo "[3/6] 上传部署包 (这可能需要几分钟)..."
sshpass -p "$SERVER_PASS" scp -o StrictHostKeyChecking=no -o ConnectTimeout=300 "$ZIP_FILE" "${SERVER_USER}@${SERVER_IP}:${TEMP_DIR//\\//}/social-auto-upload-window-deploy.zip" 2>&1 | grep -v "Warning: Permanently added"
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "✅ 部署包上传成功"
else
    echo "❌ 部署包上传失败"
    exit 1
fi
echo ""

# 上传部署脚本
echo "[4/6] 上传部署脚本..."
sshpass -p "$SERVER_PASS" scp -o StrictHostKeyChecking=no "$DEPLOY_BAT" "${SERVER_USER}@${SERVER_IP}:${TEMP_DIR//\\//}/deploy_on_windows.bat" 2>&1 | grep -v "Warning: Permanently added"
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "✅ 部署脚本上传成功"
else
    echo "❌ 部署脚本上传失败"
    exit 1
fi
echo ""

# 执行部署
echo "[5/6] 在服务器上执行部署（这可能需要 10-20 分钟）..."
echo "    正在安装依赖，请耐心等待..."
sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no "${SERVER_USER}@${SERVER_IP}" "cd ${TEMP_DIR} && cmd.exe /c deploy_on_windows.bat" 2>&1 | while IFS= read -r line; do
    echo "    $line"
done

if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "✅ 部署执行完成"
else
    echo "⚠️  部署过程中可能有警告，但可能已成功完成"
fi
echo ""

# 验证部署
echo "[6/6] 验证部署..."
if sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no "${SERVER_USER}@${SERVER_IP}" "if exist ${REMOTE_DIR}\\sau_backend.py (exit 0) else (exit 1)" 2>/dev/null; then
    echo "✅ 后端文件已部署"
else
    echo "⚠️  后端文件未找到，可能需要手动检查"
fi

if sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no "${SERVER_USER}@${SERVER_IP}" "if exist ${REMOTE_DIR}\\sau_frontend (exit 0) else (exit 1)" 2>/dev/null; then
    echo "✅ 前端目录已部署"
else
    echo "⚠️  前端目录未找到，可能需要手动检查"
fi
echo ""

echo "=========================================="
echo "✅ 自动部署完成！"
echo "=========================================="
echo ""
echo "📋 下一步：在服务器上启动服务"
echo ""
echo "方法1: 使用启动脚本"
echo "  cd C:\\social-auto-upload-window"
echo "  start-win.bat"
echo ""
echo "方法2: 手动启动"
echo "  后端: python sau_backend.py"
echo "  前端: cd sau_frontend && npm run dev -- --host 0.0.0.0"
echo ""
echo "🌐 访问地址："
echo "  前端: http://${SERVER_IP}:5173"
echo "  后端: http://${SERVER_IP}:5409"
echo ""

