#!/bin/bash

echo "🚀 开始部署最新修复..."

SERVER="ubuntu@150.107.38.113"
PASSWORD="15831929073asAS"
REMOTE_DIR="/home/ubuntu/social-auto-upload"

# 需要上传的文件列表
FILES=(
    "myUtils/login_wrapper.py"
    "myUtils/login_selenium.py"
    "myUtils/login.py"
    "sau_backend.py"
    "conf.py"
    "utils/enhanced_stealth.py"
    "utils/fingerprint_protection.py"
    "sau_frontend/src/views/AccountManagement.vue"
)

# 上传文件
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "📤 上传 $file..."
        sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no "$file" "$SERVER:$REMOTE_DIR/$file"
    else
        echo "⚠️  文件不存在: $file"
    fi
done

echo ""
echo "✅ 文件上传完成！"
echo ""
echo "🔨 构建前端..."

sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER" << 'REMOTE_SCRIPT'
cd /home/ubuntu/social-auto-upload/sau_frontend
source ~/.bashrc 2>/dev/null || true
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" 2>/dev/null || true
npm run build
REMOTE_SCRIPT

echo ""
echo "🔄 重启服务..."

sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER" << 'REMOTE_SCRIPT'
cd /home/ubuntu/social-auto-upload
~/.local/lib/node_modules/pm2/bin/pm2 restart sau-backend sau-frontend
sleep 3
~/.local/lib/node_modules/pm2/bin/pm2 status
REMOTE_SCRIPT

echo ""
echo "✅ 部署完成！"
