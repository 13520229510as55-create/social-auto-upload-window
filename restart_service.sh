#!/bin/bash
# 重启服务器上的服务

SERVER_IP="101.126.158.155"
SERVER_USER="root"
SERVER_PASSWORD="15831929073asAS"
DEPLOY_DIR="/opt/social-auto-upload"

echo "=========================================="
echo "重启服务器上的服务"
echo "=========================================="

sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
cd /opt/social-auto-upload

# 停止服务
echo "🛑 停止服务..."
if [ -f stop.sh ]; then
    ./stop.sh
else
    pkill -f "python3.*sau_backend.py" || true
fi

sleep 2

# 启动服务
echo "🚀 启动服务..."
if [ -f start.sh ]; then
    ./start.sh &
else
    cd /opt/social-auto-upload
    source venv/bin/activate
    nohup python3 sau_backend.py > logs/backend.log 2>&1 &
fi

sleep 3

# 检查服务状态
if pgrep -f "python3.*sau_backend.py" > /dev/null; then
    echo "✅ 服务启动成功"
else
    echo "❌ 服务启动失败，请检查日志"
fi
ENDSSH

echo ""
echo "✅ 服务重启完成！"
echo "服务器地址: http://${SERVER_IP}:5409"
