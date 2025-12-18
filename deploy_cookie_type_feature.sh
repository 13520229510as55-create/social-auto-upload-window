#!/bin/bash
# 部署Cookie类型选择功能到服务器

SERVER_IP="150.107.38.113"
SERVER_USER="ubuntu"
SERVER_PASSWORD="15831929073asAS"
DEPLOY_DIR="/home/ubuntu/social-auto-upload"

echo "=========================================="
echo "部署Cookie类型选择功能"
echo "=========================================="

# 1. 备份服务器文件
echo "📦 备份服务器上的现有文件..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
DEPLOY_DIR="/home/ubuntu/social-auto-upload"
BACKUP_DIR="${DEPLOY_DIR}/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

echo "备份后端文件..."
[ -f "${DEPLOY_DIR}/sau_backend.py" ] && cp ${DEPLOY_DIR}/sau_backend.py ${BACKUP_DIR}/sau_backend.py 2>/dev/null || true

if [ -d "${DEPLOY_DIR}/sau_frontend/dist" ]; then
    echo "备份前端文件..."
    mkdir -p ${BACKUP_DIR}/frontend
    cp -r ${DEPLOY_DIR}/sau_frontend/dist ${BACKUP_DIR}/frontend/ 2>/dev/null || true
fi

echo "✅ 备份完成: $BACKUP_DIR"
ENDSSH

# 2. 构建前端
echo ""
echo "🔨 构建前端..."
cd sau_frontend

if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install --registry=https://registry.npmmirror.com
fi

echo "🔨 开始构建..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ 前端构建失败"
    exit 1
fi

echo "✅ 前端构建完成"
cd ..

# 3. 上传后端文件
echo ""
echo "📤 上传后端文件..."
sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no sau_backend.py ${SERVER_USER}@${SERVER_IP}:${DEPLOY_DIR}/sau_backend.py
echo "✅ 后端文件上传完成"

# 4. 上传前端构建文件
echo ""
echo "📤 上传前端构建文件..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "mkdir -p ${DEPLOY_DIR}/sau_frontend/dist"
sshpass -p "$SERVER_PASSWORD" scp -r -o StrictHostKeyChecking=no sau_frontend/dist/* ${SERVER_USER}@${SERVER_IP}:${DEPLOY_DIR}/sau_frontend/dist/
echo "✅ 前端文件上传完成"

# 5. 清除服务器上的Python缓存
echo ""
echo "🧹 清除服务器上的Python缓存..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
cd /home/ubuntu/social-auto-upload
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
echo "✅ 缓存已清除"
ENDSSH

# 6. 重启后端服务
echo ""
echo "🔄 重启后端服务..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
cd /home/ubuntu/social-auto-upload

# 停止现有服务
echo "1️⃣ 停止现有服务..."
pkill -9 -f "python3.*sau_backend.py" || true
pkill -9 -f "python.*sau_backend.py" || true
sleep 3

# 确认端口已释放
if lsof -ti:5409 > /dev/null 2>&1; then
    echo "⚠️ 端口5409仍被占用，强制释放..."
    sudo fuser -k 5409/tcp 2>/dev/null || true
    sleep 2
fi

# 启动服务
echo "2️⃣ 启动服务..."
# 尝试使用conda环境
if [ -f "/home/ubuntu/miniconda3/envs/social-auto-upload/bin/python" ]; then
    nohup /home/ubuntu/miniconda3/envs/social-auto-upload/bin/python sau_backend.py > logs/backend.log 2>&1 &
else
    source venv/bin/activate 2>/dev/null || true
    nohup python3 sau_backend.py > logs/backend.log 2>&1 &
fi
BACKEND_PID=$!
echo "后端服务 PID: $BACKEND_PID"
sleep 4

# 检查服务状态
if ps -p $BACKEND_PID > /dev/null 2>&1 || pgrep -f sau_backend.py > /dev/null; then
    echo "✅ 后端服务启动成功"
    ps aux | grep sau_backend.py | grep -v grep | head -1
    echo ""
    echo "检查端口监听:"
    netstat -tlnp | grep 5409 || ss -tlnp | grep 5409 || echo "⚠️ 无法检查端口状态"
else
    echo "❌ 后端服务启动失败，查看日志:"
    tail -30 logs/backend.log
fi
ENDSSH

echo ""
echo "=========================================="
echo "✅ 部署完成！"
echo "=========================================="
echo "已部署的功能："
echo "  ✅ Cookie类型选择（本地上传/扫码登录）"
echo "  ✅ 直接创建账号功能"
echo "  ✅ 后端API: /addAccountDirect"
echo ""
echo "服务器地址: http://${SERVER_IP}:5409"
echo ""
echo "测试步骤："
echo "1. 打开账号管理页面"
echo "2. 点击'添加账号'"
echo "3. 选择'Cookie类型'为'本地上传'"
echo "4. 填写平台和名称后点击确定"
echo "5. 账号应该直接添加到列表中（状态为异常）"
echo "6. 后续可以通过'上传'按钮上传Cookie文件"

