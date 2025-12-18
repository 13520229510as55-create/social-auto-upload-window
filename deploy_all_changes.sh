#!/bin/bash
# 部署所有本地修改到服务器

SERVER_IP="150.107.38.113"
SERVER_USER="ubuntu"
SERVER_PASSWORD="15831929073asAS"
DEPLOY_DIR="/home/ubuntu/social-auto-upload"

echo "=========================================="
echo "部署所有本地修改到服务器"
echo "=========================================="

# 1. 备份服务器文件
echo "📦 备份服务器上的现有文件..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
DEPLOY_DIR="/home/ubuntu/social-auto-upload"
BACKUP_DIR="${DEPLOY_DIR}/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

echo "备份后端文件..."
[ -f "${DEPLOY_DIR}/sau_backend.py" ] && cp ${DEPLOY_DIR}/sau_backend.py ${BACKUP_DIR}/sau_backend.py 2>/dev/null || true
[ -f "${DEPLOY_DIR}/myUtils/auth.py" ] && cp ${DEPLOY_DIR}/myUtils/auth.py ${BACKUP_DIR}/auth.py 2>/dev/null || true
[ -f "${DEPLOY_DIR}/myUtils/login.py" ] && cp ${DEPLOY_DIR}/myUtils/login.py ${BACKUP_DIR}/login.py 2>/dev/null || true
[ -f "${DEPLOY_DIR}/myUtils/postVideo.py" ] && cp ${DEPLOY_DIR}/myUtils/postVideo.py ${BACKUP_DIR}/postVideo.py 2>/dev/null || true

echo "备份uploader文件..."
[ -f "${DEPLOY_DIR}/uploader/tencent_uploader/main.py" ] && mkdir -p ${BACKUP_DIR}/uploader/tencent_uploader && cp ${DEPLOY_DIR}/uploader/tencent_uploader/main.py ${BACKUP_DIR}/uploader/tencent_uploader/main.py 2>/dev/null || true
[ -f "${DEPLOY_DIR}/uploader/ks_uploader/main.py" ] && mkdir -p ${BACKUP_DIR}/uploader/ks_uploader && cp ${DEPLOY_DIR}/uploader/ks_uploader/main.py ${BACKUP_DIR}/uploader/ks_uploader/main.py 2>/dev/null || true
[ -f "${DEPLOY_DIR}/uploader/xiaohongshu_uploader/main.py" ] && mkdir -p ${BACKUP_DIR}/uploader/xiaohongshu_uploader && cp ${DEPLOY_DIR}/uploader/xiaohongshu_uploader/main.py ${BACKUP_DIR}/uploader/xiaohongshu_uploader/main.py 2>/dev/null || true

if [ -d "${DEPLOY_DIR}/sau_frontend/dist" ]; then
    echo "备份前端文件..."
    cp -r ${DEPLOY_DIR}/sau_frontend/dist ${BACKUP_DIR}/frontend/ 2>/dev/null || true
fi

echo "✅ 备份完成: $BACKUP_DIR"
ENDSSH

NEED_RESTART_BACKEND=false

# 2. 上传后端主文件
if [ -f "sau_backend.py" ]; then
    echo "📤 上传 sau_backend.py..."
    sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no sau_backend.py ${SERVER_USER}@${SERVER_IP}:${DEPLOY_DIR}/sau_backend.py
    NEED_RESTART_BACKEND=true
fi

# 3. 上传 myUtils 文件
echo "📤 上传 myUtils 文件..."
if [ -f "myUtils/auth.py" ]; then
    sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "mkdir -p ${DEPLOY_DIR}/myUtils"
    sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no myUtils/auth.py ${SERVER_USER}@${SERVER_IP}:${DEPLOY_DIR}/myUtils/auth.py
    NEED_RESTART_BACKEND=true
fi

if [ -f "myUtils/login.py" ]; then
    sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no myUtils/login.py ${SERVER_USER}@${SERVER_IP}:${DEPLOY_DIR}/myUtils/login.py
    NEED_RESTART_BACKEND=true
fi

if [ -f "myUtils/postVideo.py" ]; then
    sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no myUtils/postVideo.py ${SERVER_USER}@${SERVER_IP}:${DEPLOY_DIR}/myUtils/postVideo.py
    NEED_RESTART_BACKEND=true
fi

# 4. 上传 uploader 文件
echo "📤 上传 uploader 文件..."
if [ -f "uploader/tencent_uploader/main.py" ]; then
    sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "mkdir -p ${DEPLOY_DIR}/uploader/tencent_uploader"
    sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no uploader/tencent_uploader/main.py ${SERVER_USER}@${SERVER_IP}:${DEPLOY_DIR}/uploader/tencent_uploader/main.py
    NEED_RESTART_BACKEND=true
fi

if [ -f "uploader/ks_uploader/main.py" ]; then
    sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "mkdir -p ${DEPLOY_DIR}/uploader/ks_uploader"
    sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no uploader/ks_uploader/main.py ${SERVER_USER}@${SERVER_IP}:${DEPLOY_DIR}/uploader/ks_uploader/main.py
    NEED_RESTART_BACKEND=true
fi

if [ -f "uploader/xiaohongshu_uploader/main.py" ]; then
    sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "mkdir -p ${DEPLOY_DIR}/uploader/xiaohongshu_uploader"
    sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no uploader/xiaohongshu_uploader/main.py ${SERVER_USER}@${SERVER_IP}:${DEPLOY_DIR}/uploader/xiaohongshu_uploader/main.py
    NEED_RESTART_BACKEND=true
fi

# 5. 构建并上传前端
echo "📤 构建并上传前端..."
cd sau_frontend

if [ ! -d "dist" ]; then
    echo "🔨 构建前端..."
    npm run build
    if [ $? -ne 0 ]; then
        echo "❌ 前端构建失败"
        exit 1
    fi
fi

sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "mkdir -p ${DEPLOY_DIR}/sau_frontend/dist"
sshpass -p "$SERVER_PASSWORD" scp -r -o StrictHostKeyChecking=no dist/* ${SERVER_USER}@${SERVER_IP}:${DEPLOY_DIR}/sau_frontend/dist/

cd ..

# 6. 清除服务器上的Python缓存
echo "🧹 清除服务器上的Python缓存..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
cd /home/ubuntu/social-auto-upload
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
echo "✅ 缓存已清除"
ENDSSH

# 7. 如果需要，重启后端服务
if [ "$NEED_RESTART_BACKEND" = true ]; then
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
else
    echo "❌ 后端服务启动失败，查看日志:"
    tail -30 logs/backend.log
fi
ENDSSH
fi

echo ""
echo "=========================================="
echo "✅ 部署完成！"
echo "=========================================="
echo "已部署的文件："
echo "  - sau_backend.py"
echo "  - myUtils/auth.py, login.py, postVideo.py"
echo "  - uploader/tencent_uploader/main.py"
echo "  - uploader/ks_uploader/main.py"
echo "  - uploader/xiaohongshu_uploader/main.py"
echo "  - sau_frontend/dist/*"
echo ""
echo "服务器地址: http://${SERVER_IP}:5409"

