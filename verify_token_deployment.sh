#!/bin/bash

# 验证 Google Cloud Storage Token 部署脚本

echo "=========================================="
echo "验证 GCS Token 部署状态"
echo "=========================================="
echo ""

# 新 token (应该使用的)
NEW_TOKEN="ya29.a0Aa7pCA_V4-alvb6WzH1DT_kZztIq_Fk6FToWE0C804MnQAUwFTwRkBGLzuS3d8PgPE_UfgXLm5TjkntyVrts_iXoKGIzTzVockMZUhSVc7X5EqSTjRFLH_VamWi2bSvdhQg22t-oazXAk_UTALkdog17Q9X4JhFruiDxDWkWGap8P8DTVtWSc4NPADcxJUCYkpCvIVPhoH5XWwaCgYKATsSARESFQHGX2MidZLOwXozR7IrP8OU45RkWw0213"

# 浏览器实际使用的 token (不应该使用的)
BROWSER_TOKEN="ya29.a0ATi6K2sCH1Pm5TNQYQHnFmrCKZqPe8qO7gwrETHPT2_K_SgutA6_Hkvyab2JGdSvxL6XbMMa3DJLo2yHvhRLe1mbZNtWX2BgILHDm53MU0srxMBROvAwtQbPswmBTMtx1i49bkuDI6ZhZ2fBm5guS7QC4ELPWj9CIB7YSojzNjh4a1qPv7J6l-yDKTggl0TMsarMUnYh0ZB4aCgYKAdMSARESFQHGX2Mio37MSZuC5VasgHFL_UC0Ww0211"

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

