#!/bin/bash

# 服务启动脚本（在服务器上运行）

set -e

DEPLOY_DIR="/opt/social-auto-upload"
cd $DEPLOY_DIR

# 激活虚拟环境
source venv/bin/activate

# 确保目录存在
mkdir -p videoFile cookiesFile logs db

# 启动后端服务（后台运行）
echo "🚀 启动后端服务..."
PYTHONUNBUFFERED=1 nohup python3 sau_backend.py > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "后端服务 PID: $BACKEND_PID"
echo $BACKEND_PID > /tmp/social-auto-upload-backend.pid

# 等待服务启动
sleep 3

# 检查服务是否运行
if ps -p $BACKEND_PID > /dev/null; then
    echo "✅ 后端服务启动成功"
    echo "访问地址: http://$(hostname -I | awk '{print $1}'):5409"
else
    echo "❌ 后端服务启动失败，请查看日志: logs/backend.log"
    exit 1
fi

echo ""
echo "服务已启动，按 Ctrl+C 退出（服务将继续在后台运行）"
echo "停止服务: ./stop.sh"

