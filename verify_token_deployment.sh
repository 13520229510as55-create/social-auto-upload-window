#!/bin/bash

# 验证 Google Cloud Storage Token 部署脚本

echo "=========================================="
echo "验证 GCS Token 部署状态"
echo "=========================================="
echo ""

# 新 token (应该使用的) - 从环境变量读取
NEW_TOKEN="${GOOGLE_OAUTH_TOKEN:-}"

# 浏览器实际使用的 token (不应该使用的) - 从环境变量读取
BROWSER_TOKEN="${GOOGLE_OAUTH_TOKEN_BROWSER:-}"

echo "1. 检查本地文件..."
LOCAL_TOKEN=$(grep -o "ya29\.[^']*" sau_frontend/src/api/material.js | head -1)
if [ "$LOCAL_TOKEN" = "$NEW_TOKEN" ]; then
    echo "   ✅ 本地文件使用新 token"
else
    echo "   ❌ 本地文件 token 不匹配"
    echo "   本地: ${LOCAL_TOKEN:0:50}..."
    echo "   期望: ${NEW_TOKEN:0:50}..."
fi
echo ""

echo "2. 检查服务器文件..."
SERVER_TOKEN=$(sshpass -p "15831929073asAS" ssh -o StrictHostKeyChecking=no ubuntu@150.107.38.113 'grep -o "ya29\.[^'\'']*" /home/ubuntu/social-auto-upload/sau_frontend/src/api/material.js | head -1')
if [ "$SERVER_TOKEN" = "$NEW_TOKEN" ]; then
    echo "   ✅ 服务器文件使用新 token"
else
    echo "   ❌ 服务器文件 token 不匹配"
    echo "   服务器: ${SERVER_TOKEN:0:50}..."
    echo "   期望: ${NEW_TOKEN:0:50}..."
fi
echo ""

echo "3. 浏览器实际使用的 token..."
echo "   ⚠️  浏览器使用: ${BROWSER_TOKEN:0:50}..."
if [ "$BROWSER_TOKEN" = "$NEW_TOKEN" ]; then
    echo "   ✅ 浏览器使用正确的 token"
else
    echo "   ❌ 浏览器仍在使用旧的/错误的 token"
    echo ""
    echo "   解决方案："
    echo "   1. 清除浏览器缓存 (Ctrl+Shift+Delete)"
    echo "   2. 硬刷新页面 (Ctrl+Shift+R 或 Cmd+Shift+R)"
    echo "   3. 禁用浏览器缓存 (开发者工具 > Network > Disable cache)"
    echo "   4. 清除 Service Worker (如果有)"
fi
echo ""

echo "=========================================="
echo "验证完成"
echo "=========================================="

