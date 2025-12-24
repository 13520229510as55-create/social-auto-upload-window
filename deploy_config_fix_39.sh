#!/bin/bash
# 部署配置管理页面修复到39服务器

SERVER_IP="39.105.227.6"
SERVER_USER="administrator"
SERVER_PASSWORD="15831929073asAS"
DEPLOY_DIR="/home/administrator/social-auto-upload-window"

echo "=========================================="
echo "部署配置管理页面修复到39服务器"
echo "=========================================="

# 1. 备份服务器文件
echo "📦 备份服务器上的现有文件..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << ENDSSH
DEPLOY_DIR="${DEPLOY_DIR}"
BACKUP_DIR="\${DEPLOY_DIR}/backup_config_fix_\$(date +%Y%m%d_%H%M%S)"
mkdir -p \$BACKUP_DIR

if [ -d "\${DEPLOY_DIR}/sau_frontend/dist" ]; then
    echo "备份前端文件..."
    mkdir -p \$BACKUP_DIR/frontend
    cp -r \${DEPLOY_DIR}/sau_frontend/dist \$BACKUP_DIR/frontend/ 2>/dev/null || true
fi

echo "✅ 备份完成: \$BACKUP_DIR"
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

# 3. 上传前端构建文件
echo ""
echo "📤 上传前端构建文件..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "mkdir -p ${DEPLOY_DIR}/sau_frontend/dist"
sshpass -p "$SERVER_PASSWORD" scp -r -o StrictHostKeyChecking=no sau_frontend/dist/* ${SERVER_USER}@${SERVER_IP}:${DEPLOY_DIR}/sau_frontend/dist/

echo "✅ 前端文件上传完成"

# 4. 重启前端服务（如果需要）
echo ""
echo "🔄 重启前端服务..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << ENDSSH
cd ${DEPLOY_DIR}

# 如果使用PM2，重启前端服务
if command -v pm2 &> /dev/null; then
    echo "使用PM2重启前端服务..."
    pm2 restart sau-frontend 2>/dev/null || pm2 restart frontend 2>/dev/null || echo "PM2服务重启失败或未找到服务"
else
    echo "未找到PM2，请手动重启前端服务"
fi

# 如果使用systemd
if systemctl is-active --quiet sau-frontend.service 2>/dev/null; then
    echo "使用systemd重启前端服务..."
    sudo systemctl restart sau-frontend.service 2>/dev/null || echo "systemd服务重启失败"
fi

echo "✅ 服务重启完成"
ENDSSH

echo ""
echo "=========================================="
echo "✅ 部署完成！"
echo "=========================================="
echo ""
echo "请访问配置管理页面验证修复是否生效："
echo "http://${SERVER_IP}/production/config"
echo ""

