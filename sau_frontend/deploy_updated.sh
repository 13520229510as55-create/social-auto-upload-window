#!/bin/bash
# 部署更新后的前端和后端代码

SERVER_IP="101.126.158.155"
SERVER_USER="root"
SERVER_PASSWORD="15831929073asAS"
DEPLOY_DIR="/opt/social-auto-upload"

echo "=========================================="
echo "开始部署更新后的代码"
echo "=========================================="

# 1. 部署前端dist目录
echo "📤 上传前端构建文件..."
cd sau_frontend
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "mkdir -p ${DEPLOY_DIR}/sau_frontend/dist"
sshpass -p "$SERVER_PASSWORD" scp -r -o StrictHostKeyChecking=no dist/* ${SERVER_USER}@${SERVER_IP}:${DEPLOY_DIR}/sau_frontend/dist/

# 2. 部署后端代码
echo "📤 上传后端代码..."
cd ..
sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no sau_backend.py ${SERVER_USER}@${SERVER_IP}:${DEPLOY_DIR}/
sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no uploader/tencent_uploader/main.py ${SERVER_USER}@${SERVER_IP}:${DEPLOY_DIR}/uploader/tencent_uploader/

echo ""
echo "✅ 文件上传完成！"
echo ""
echo "正在重启服务..."
