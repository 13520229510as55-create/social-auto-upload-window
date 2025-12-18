#!/bin/bash
# 快速部署Cookie日志功能到 yutt.xyz

SERVER_IP="150.107.38.113"
SERVER_USER="ubuntu"
SERVER_PASSWORD="15831929073asAS"
DEPLOY_DIR="/home/ubuntu/social-auto-upload"

echo "=========================================="
echo "快速部署Cookie日志功能到 yutt.xyz"
echo "=========================================="

# 1. 备份服务器文件
echo "📦 备份服务器上的现有文件..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
DEPLOY_DIR="/home/ubuntu/social-auto-upload"
BACKUP_DIR="${DEPLOY_DIR}/backup_cookie_logs_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

echo "备份后端文件..."
[ -f "${DEPLOY_DIR}/sau_backend.py" ] && cp ${DEPLOY_DIR}/sau_backend.py ${BACKUP_DIR}/sau_backend.py 2>/dev/null || true
[ -f "${DEPLOY_DIR}/myUtils/login.py" ] && cp ${DEPLOY_DIR}/myUtils/login.py ${BACKUP_DIR}/login.py 2>/dev/null || true

echo "✅ 备份完成: $BACKUP_DIR"
ENDSSH

# 2. 上传后端文件
echo ""
echo "📤 上传后端文件..."
sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no sau_backend.py ${SERVER_USER}@${SERVER_IP}:${DEPLOY_DIR}/sau_backend.py
echo "✅ sau_backend.py 上传完成"

# 3. 上传登录模块文件
echo ""
echo "📤 上传登录模块文件..."
sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no myUtils/login.py ${SERVER_USER}@${SERVER_IP}:${DEPLOY_DIR}/myUtils/login.py
echo "✅ myUtils/login.py 上传完成"

# 4. 清除服务器上的Python缓存
echo ""
echo "🧹 清除服务器上的Python缓存..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
cd /home/ubuntu/social-auto-upload
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
echo "✅ 缓存已清除"
ENDSSH

# 5. 重启PM2服务
echo ""
echo "🔄 重启PM2服务..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
cd /home/ubuntu/social-auto-upload

echo "1️⃣ 重启后端服务 (sau-backend)..."
pm2 restart sau-backend

echo "2️⃣ 等待服务启动..."
sleep 3

echo "3️⃣ 检查服务状态..."
pm2 list
pm2 logs sau-backend --lines 20 --nostream

ENDSSH

echo ""
echo "=========================================="
echo "✅ 部署完成！"
echo "=========================================="
echo "已部署的功能："
echo "  ✅ Cookie返回日志追踪"
echo "  ✅ SSE流Cookie发送日志"
echo "  ✅ 手动确认登录Cookie返回日志"
echo ""
echo "访问地址: https://yutt.xyz"
echo ""
echo "查看日志命令:"
echo "  pm2 logs sau-backend | grep -E 'Cookie|SSE流|手动确认登录'"
