#!/bin/bash

# 服务停止脚本

echo "🛑 正在停止服务..."

# 停止后端服务
if [ -f /tmp/social-auto-upload-backend.pid ]; then
    BACKEND_PID=$(cat /tmp/social-auto-upload-backend.pid)
    if ps -p $BACKEND_PID > /dev/null; then
        kill $BACKEND_PID
        echo "✅ 后端服务已停止 (PID: $BACKEND_PID)"
    else
        echo "⚠️  后端服务进程不存在"
    fi
    rm /tmp/social-auto-upload-backend.pid
else
    # 如果没有 PID 文件，尝试通过进程名查找
    pkill -f "python3.*sau_backend.py" && echo "✅ 后端服务已停止" || echo "⚠️  未找到运行中的后端服务"
fi

echo "✅ 所有服务已停止"

