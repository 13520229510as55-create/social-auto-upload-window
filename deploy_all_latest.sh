#!/bin/bash

echo "🚀 开始部署所有最新更改..."

SERVER="ubuntu@150.107.38.113"
PASSWORD="15831929073asAS"
REMOTE_DIR="/home/ubuntu/social-auto-upload"

# 需要部署的文件列表
FILES=(
    "sau_backend.py"
    "myUtils/login.py"
    "myUtils/login_wrapper.py"
    "myUtils/login_selenium.py"
    "myUtils/auth.py"
    "utils/enhanced_stealth.py"
    "utils/fingerprint_protection.py"
    "utils/human_behavior.py"
    "sau_frontend/src/views/AccountManagement.vue"
    "sau_frontend/src/api/account.js"
)

# 检查 conf.py 是否存在
if [ -f "conf.py" ]; then
    FILES+=("conf.py")
fi

echo "📦 上传文件到服务器..."
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ 上传: $file"
        sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no "$file" "$SERVER:$REMOTE_DIR/$file"
    else
        echo "  ⚠️  文件不存在: $file"
    fi
done

echo ""
echo "🔄 重启后端服务..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER" << 'REMOTE_SCRIPT'
cd /home/ubuntu/social-auto-upload
~/.local/lib/node_modules/pm2/bin/pm2 restart sau-backend
sleep 3
~/.local/lib/node_modules/pm2/bin/pm2 status sau-backend
~/.local/lib/node_modules/pm2/bin/pm2 logs sau-backend --lines 5 --nostream | tail -10
REMOTE_SCRIPT

echo ""
echo "✅ 部署完成！"
