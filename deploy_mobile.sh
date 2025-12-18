#!/bin/bash
# 部署移动端应用到 yutt.xyz 服务器

SERVER_IP="150.107.38.113"
SERVER_USER="ubuntu"
SERVER_PASSWORD="15831929073asAS"
DEPLOY_DIR="/home/ubuntu/social-auto-upload"
MOBILE_SOURCE_DIR="/Users/a58/Desktop/sau-mobile/dist/mobile"
MOBILE_TARGET_DIR="${DEPLOY_DIR}/sau-mobile/dist/mobile"

echo "=========================================="
echo "部署移动端应用到 yutt.xyz"
echo "=========================================="

# 1. 检查移动端构建文件是否存在
if [ ! -d "$MOBILE_SOURCE_DIR" ]; then
    echo "❌ 错误: 移动端构建文件不存在: $MOBILE_SOURCE_DIR"
    echo "请先执行构建: cd /Users/a58/Desktop/sau-mobile && npm run build"
    exit 1
fi

echo "✅ 找到移动端构建文件"

# 2. 备份服务器上的现有移动端文件
echo ""
echo "📦 备份服务器上的现有移动端文件..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << ENDSSH
DEPLOY_DIR="${DEPLOY_DIR}"
MOBILE_TARGET_DIR="${MOBILE_TARGET_DIR}"

if [ -d "\${MOBILE_TARGET_DIR}" ]; then
    BACKUP_DIR="\${DEPLOY_DIR}/backup_mobile_\$(date +%Y%m%d_%H%M%S)"
    mkdir -p \${BACKUP_DIR}
    echo "备份移动端文件到: \${BACKUP_DIR}"
    cp -r \${MOBILE_TARGET_DIR} \${BACKUP_DIR}/mobile 2>/dev/null || true
    echo "✅ 备份完成"
else
    echo "ℹ️  服务器上没有现有移动端文件，跳过备份"
fi
ENDSSH

# 3. 创建服务器目录
echo ""
echo "📂 在服务器上创建目录..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "mkdir -p ${MOBILE_TARGET_DIR}"

# 4. 上传移动端构建文件
echo ""
echo "📤 上传移动端构建文件..."
sshpass -p "$SERVER_PASSWORD" scp -r -o StrictHostKeyChecking=no ${MOBILE_SOURCE_DIR}/* ${SERVER_USER}@${SERVER_IP}:${MOBILE_TARGET_DIR}/

echo "✅ 移动端文件上传完成"

# 5. 检查服务器上的文件
echo ""
echo "🔍 检查服务器上的文件..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << ENDSSH
MOBILE_TARGET_DIR="${MOBILE_TARGET_DIR}"

echo "移动端文件列表:"
ls -lh \${MOBILE_TARGET_DIR}/ | head -20

echo ""
echo "检查 index.html:"
if [ -f "\${MOBILE_TARGET_DIR}/index.html" ]; then
    echo "✅ index.html 存在"
    head -5 \${MOBILE_TARGET_DIR}/index.html
else
    echo "❌ index.html 不存在"
fi

echo ""
echo "检查 assets 目录:"
if [ -d "\${MOBILE_TARGET_DIR}/assets" ]; then
    echo "✅ assets 目录存在"
    echo "文件数量: \$(ls -1 \${MOBILE_TARGET_DIR}/assets/ | wc -l)"
    ls -lh \${MOBILE_TARGET_DIR}/assets/ | grep HotspotCenter
else
    echo "❌ assets 目录不存在"
fi
ENDSSH

# 6. 检查Nginx配置（提示）
echo ""
echo "=========================================="
echo "✅ 移动端文件部署完成！"
echo "=========================================="
echo ""
echo "部署详情："
echo "  服务器: ${SERVER_IP}"
echo "  目标目录: ${MOBILE_TARGET_DIR}"
echo "  访问路径: /mobile/ (需要在Nginx中配置)"
echo ""
echo "下一步操作："
echo "1. 检查Nginx配置，确保 /mobile/ 路径指向移动端文件"
echo "2. 确保Nginx配置中有以下配置:"
echo "   location /mobile/ {"
echo "       alias /home/ubuntu/social-auto-upload/sau-mobile/dist/mobile/;"
echo "       try_files \$uri \$uri/ /mobile/index.html;"
echo "   }"
echo ""
echo "3. 重启Nginx服务:"
echo "   sudo nginx -t && sudo systemctl reload nginx"
echo ""
echo "4. 访问移动端应用:"
echo "   https://yutt.xyz/mobile/"
echo ""

