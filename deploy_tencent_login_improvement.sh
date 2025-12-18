#!/bin/bash
# 部署视频号登录改进功能到 yutt.xyz 域名下的服务

SERVER_IP="150.107.38.113"
SERVER_USER="ubuntu"
SERVER_PASSWORD="15831929073asAS"
DEPLOY_DIR="/home/ubuntu/social-auto-upload"

echo "=========================================="
echo "部署视频号登录改进功能到 yutt.xyz"
echo "=========================================="

# 1. 备份服务器文件
echo "📦 备份服务器上的现有文件..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
DEPLOY_DIR="/home/ubuntu/social-auto-upload"
BACKUP_DIR="${DEPLOY_DIR}/backup_tencent_login_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

echo "备份后端文件..."
[ -f "${DEPLOY_DIR}/sau_backend.py" ] && cp ${DEPLOY_DIR}/sau_backend.py ${BACKUP_DIR}/sau_backend.py 2>/dev/null || true
[ -f "${DEPLOY_DIR}/myUtils/login.py" ] && cp ${DEPLOY_DIR}/myUtils/login.py ${BACKUP_DIR}/login.py 2>/dev/null || true

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
echo "✅ sau_backend.py 上传完成"

# 4. 上传登录相关文件
echo ""
echo "📤 上传登录相关文件..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "mkdir -p ${DEPLOY_DIR}/myUtils"
sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no myUtils/login.py ${SERVER_USER}@${SERVER_IP}:${DEPLOY_DIR}/myUtils/login.py
echo "✅ myUtils/login.py 上传完成"

# 5. 上传前端构建文件
echo ""
echo "📤 上传前端构建文件..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "mkdir -p ${DEPLOY_DIR}/sau_frontend/dist"
sshpass -p "$SERVER_PASSWORD" scp -r -o StrictHostKeyChecking=no sau_frontend/dist/* ${SERVER_USER}@${SERVER_IP}:${DEPLOY_DIR}/sau_frontend/dist/
echo "✅ 前端文件上传完成"

# 6. 复制前端文件到Nginx目录
echo ""
echo "📋 复制前端文件到Nginx目录..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
sudo rm -rf /var/www/html/*
sudo cp -r /home/ubuntu/social-auto-upload/sau_frontend/dist/* /var/www/html/
sudo chown -R www-data:www-data /var/www/html
echo "✅ 前端文件已复制到 /var/www/html"
ENDSSH

# 7. 清除服务器上的Python缓存
echo ""
echo "🧹 清除服务器上的Python缓存..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
cd /home/ubuntu/social-auto-upload
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
echo "✅ 缓存已清除"
ENDSSH

# 8. 重启PM2服务
echo ""
echo "🔄 重启PM2服务..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
cd /home/ubuntu/social-auto-upload

echo "1️⃣ 检查PM2服务状态..."
pm2 list

echo "2️⃣ 重启后端服务 (sau-backend)..."
pm2 restart sau-backend || pm2 start sau-backend --name sau-backend --interpreter python3 -- sau_backend.py

echo "3️⃣ 等待服务启动..."
sleep 5

echo "4️⃣ 检查服务状态..."
pm2 list
pm2 logs sau-backend --lines 20 --nostream

echo ""
echo "5️⃣ 检查端口监听..."
netstat -tlnp | grep 5409 || ss -tlnp | grep 5409 || echo "⚠️ 无法检查端口状态"

echo ""
echo "6️⃣ 检查Nginx配置..."
sudo nginx -t && echo "✅ Nginx配置正确" || echo "⚠️ Nginx配置可能有问题"

echo ""
echo "7️⃣ 重新加载Nginx..."
sudo systemctl reload nginx && echo "✅ Nginx已重新加载" || echo "⚠️ Nginx重新加载失败"

ENDSSH

echo ""
echo "=========================================="
echo "✅ 部署完成！"
echo "=========================================="
echo "已部署的功能："
echo "  ✅ 视频号登录多重检测机制"
echo "  ✅ Cookie轮询检测（每10秒）"
echo "  ✅ URL变化检测"
echo "  ✅ 页面元素检测"
echo "  ✅ 手动确认登录功能"
echo "  ✅ 后端API: /manualConfirmLogin"
echo "  ✅ 浏览器上下文保存机制"
echo ""
echo "访问地址: https://yutt.xyz"
echo ""
echo "测试步骤："
echo "1. 访问 https://yutt.xyz"
echo "2. 打开账号管理页面"
echo "3. 点击'添加账号'，选择'视频号'"
echo "4. 选择'扫码登录'"
echo "5. 扫码后系统会自动检测登录状态"
echo "6. 如果超时，可以点击'我已扫码并确认'按钮手动完成登录"
echo ""
echo "改进点："
echo "  • 多重检测机制，提高登录成功率"
echo "  • 定期Cookie保存，防止丢失"
echo "  • 手动确认备选方案，解决无响应问题"
echo "  • 状态反馈，用户可了解检测进度"

