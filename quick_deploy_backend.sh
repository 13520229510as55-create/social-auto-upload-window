#!/bin/bash
# 快速部署后端修复

SERVER_IP="101.126.158.155"
SERVER_USER="root"
SERVER_PASSWORD="15831929073asAS"
DEPLOY_DIR="/opt/social-auto-upload"

echo "=========================================="
echo "快速部署后端修复"
echo "=========================================="

# 1. 上传修复后的后端代码
echo "📤 上传修复后的后端代码..."
sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no sau_backend.py ${SERVER_USER}@${SERVER_IP}:${DEPLOY_DIR}/

# 2. 重启服务
echo "🔄 重启后端服务..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
cd /opt/social-auto-upload

# 停止现有服务
echo "🛑 停止现有服务..."
pkill -f "python3.*sau_backend.py" || true
sleep 2

# 启动服务
echo "🚀 启动服务..."
source venv/bin/activate
mkdir -p logs
nohup python3 sau_backend.py > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "后端服务 PID: $BACKEND_PID"

# 等待服务启动
sleep 5

# 检查服务状态
if ps -p $BACKEND_PID > /dev/null 2>&1; then
    echo "✅ 服务启动成功"
    echo "检查端口监听:"
    netstat -tlnp | grep 5409 || ss -tlnp | grep 5409
else
    echo "❌ 服务启动失败，查看日志:"
    tail -20 logs/backend.log
fi
ENDSSH

echo ""
echo "=========================================="
echo "✅ 部署完成！"
echo "=========================================="


