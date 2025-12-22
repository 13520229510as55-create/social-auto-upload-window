#!/bin/bash

# 启动脚本

echo "启动 MediaCrawler 管理后台..."

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python3，请先安装 Python"
    exit 1
fi

# 检查依赖
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

echo "激活虚拟环境..."
source venv/bin/activate

echo "安装后端依赖..."
pip install -r requirements.txt

echo "启动后端服务..."
python main.py &

BACKEND_PID=$!

# 等待后端启动
sleep 3

# 检查前端依赖
if [ ! -d "frontend/node_modules" ]; then
    echo "安装前端依赖..."
    cd frontend
    npm install
    cd ..
fi

echo "启动前端服务..."
cd frontend
npm run dev &

FRONTEND_PID=$!

echo "=========================================="
echo "后端服务: http://localhost:8000"
echo "前端服务: http://localhost:3000"
echo "=========================================="
echo "按 Ctrl+C 停止服务"

# 等待中断信号
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT TERM

wait

