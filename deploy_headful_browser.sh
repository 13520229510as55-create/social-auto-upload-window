#!/bin/bash
# 部署有头浏览器模式配置

echo "=========================================="
echo "🚀 部署有头浏览器模式"
echo "=========================================="

# 服务器配置
SERVER_USER="ubuntu"
SERVER_HOST="150.107.38.113"
SERVER_PASSWORD="15831929073asAS"
SERVER_PATH="/home/ubuntu/social-auto-upload"

echo ""
echo "📋 步骤 1/4: 检查并安装 Xvfb"
echo "=========================================="

sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_HOST} << 'ENDSSH'
# 检查 Xvfb 是否已安装
if command -v Xvfb >/dev/null 2>&1; then
    echo "✅ Xvfb 已安装"
    Xvfb -help 2>&1 | head -3
else
    echo "📦 正在安装 Xvfb..."
    sudo apt-get update -qq
    sudo apt-get install -y xvfb
    
    if command -v Xvfb >/dev/null 2>&1; then
        echo "✅ Xvfb 安装成功"
    else
        echo "❌ Xvfb 安装失败，请手动安装: sudo apt-get install -y xvfb"
        exit 1
    fi
fi

# 清理旧的 Xvfb 进程和锁文件
echo "🧹 清理旧的 Xvfb 进程和锁文件..."
pkill -9 Xvfb 2>/dev/null || true
rm -f /tmp/.X*-lock 2>/dev/null || true
echo "✅ 清理完成"
ENDSSH

echo ""
echo "📋 步骤 2/4: 上传配置文件"
echo "=========================================="

# 上传 conf.py
echo "📤 上传 conf.py..."
sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no \
    conf.py ${SERVER_USER}@${SERVER_HOST}:${SERVER_PATH}/conf.py

# 上传 login.py（包含增强的伪装参数）
echo "📤 上传 myUtils/login.py..."
sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no \
    myUtils/login.py ${SERVER_USER}@${SERVER_HOST}:${SERVER_PATH}/myUtils/login.py

echo "✅ 文件上传完成"

echo ""
echo "📋 步骤 3/4: 重启服务"
echo "=========================================="

sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_HOST} << 'ENDSSH'
source ~/.bashrc 2>/dev/null || true
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" 2>/dev/null || true

cd /home/ubuntu/social-auto-upload

echo "🔄 重启 PM2 服务..."
pm2 restart sau-backend

sleep 3
echo ""
echo "✅ 服务已重启"
pm2 status sau-backend | grep sau-backend
ENDSSH

echo ""
echo "📋 步骤 4/4: 验证配置"
echo "=========================================="

sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_HOST} << 'ENDSSH'
cd /home/ubuntu/social-auto-upload

echo "📝 当前配置："
echo "-------------"
python3 -c "
from conf import LOCAL_CHROME_HEADLESS
print(f'LOCAL_CHROME_HEADLESS = {LOCAL_CHROME_HEADLESS}')
print(f'模式: {'无头模式 (Headless)' if LOCAL_CHROME_HEADLESS else '有头模式 (Headful，需要 Xvfb)'}')"

echo ""
echo "🔍 Xvfb 状态："
echo "-------------"
if ps aux | grep -v grep | grep Xvfb >/dev/null; then
    echo "✅ Xvfb 进程运行中"
    ps aux | grep -v grep | grep Xvfb | head -3
else
    echo "⏸️  Xvfb 进程未运行（会在需要时自动启动）"
fi
ENDSSH

echo ""
echo "=========================================="
echo "✅ 部署完成！"
echo "=========================================="
echo ""
echo "📝 配置说明："
echo "   - 浏览器模式: 有头模式 (Headful)"
echo "   - 虚拟显示: Xvfb（自动启动）"
echo "   - 反检测: 已启用增强伪装"
echo ""
echo "⚠️  重要提示："
echo "   1. 有头模式会自动使用 Xvfb 虚拟显示器"
echo "   2. 首次登录时会自动启动 Xvfb"
echo "   3. 性能会比无头模式略低，但更像真实浏览器"
echo "   4. 微信可能仍然会检测自动化特征"
echo ""
echo "🧪 建议测试："
echo "   现在可以重新测试视频号登录功能"
echo ""
