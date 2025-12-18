#!/bin/bash

# 视频号Set-Cookie验证机制实时监控脚本

SERVER_IP="150.107.38.113"
SERVER_USER="ubuntu"
SERVER_PASSWORD="15831929073asAS"

echo "=========================================="
echo "🔍 视频号登录Set-Cookie验证监控"
echo "=========================================="
echo ""
echo "监控内容："
echo "  ✅ Set-Cookie响应头检测"
echo "  ✅ Cookie验证状态"
echo "  ✅ 登录流程关键节点"
echo "  ✅ 最终验证报告"
echo ""
echo "按 Ctrl+C 停止监控"
echo "=========================================="
echo ""

sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
cd /home/ubuntu/social-auto-upload
source ~/.bashrc 2>/dev/null || true
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" 2>/dev/null || true

# 先显示最近50条相关日志
echo "📋 最近的相关日志："
echo "----------------------------------------"
pm2 logs sau-backend --lines 100 --nostream 2>/dev/null | grep -E "(视频号登录|Set-Cookie|Cookie验证|🍪|🔍|📊|🎯|✅|❌|⚠️)" | tail -30
echo ""
echo "=========================================="
echo "🔄 开始实时监控（等待新日志...）"
echo "=========================================="
echo ""

# 实时监控
pm2 logs sau-backend --lines 0 2>/dev/null | grep --line-buffered -E "(视频号登录|Set-Cookie|Cookie验证|🍪|🔍|📊|🎯|✅|❌|⚠️|📤|💾|🎉|⏰)" --color=always
ENDSSH
