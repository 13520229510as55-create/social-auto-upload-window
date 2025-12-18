#!/bin/bash
# 实时监测小红书图文发布日志

SERVER_IP="150.107.38.113"
SERVER_USER="ubuntu"
SERVER_PASSWORD="15831929073asAS"
LOG_FILE="/home/ubuntu/social-auto-upload/logs/xiaohongshu.log"
BACKEND_LOG="/home/ubuntu/social-auto-upload/logs/backend.log"

echo "=========================================="
echo "小红书图文发布实时监测"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="
echo ""
echo "正在监测日志，按 Ctrl+C 退出..."
echo ""

# 获取当前日志行数作为起始点
INITIAL_LINES=$(sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "wc -l < ${LOG_FILE} 2>/dev/null || echo 0")
INITIAL_BACKEND_LINES=$(sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "wc -l < ${BACKEND_LOG} 2>/dev/null || echo 0")

echo "起始日志行数: xiaohongshu.log=$INITIAL_LINES, backend.log=$INITIAL_BACKEND_LINES"
echo ""

# 实时监测
while true; do
    # 获取当前日志行数
    CURRENT_LINES=$(sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "wc -l < ${LOG_FILE} 2>/dev/null || echo 0")
    CURRENT_BACKEND_LINES=$(sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "wc -l < ${BACKEND_LOG} 2>/dev/null || echo 0")
    
    # 计算新增行数
    NEW_LINES=$((CURRENT_LINES - INITIAL_LINES))
    NEW_BACKEND_LINES=$((CURRENT_BACKEND_LINES - INITIAL_BACKEND_LINES))
    
    if [ $NEW_LINES -gt 0 ] || [ $NEW_BACKEND_LINES -gt 0 ]; then
        # 显示新增的后端日志（postImageText相关）
        if [ $NEW_BACKEND_LINES -gt 0 ]; then
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "📋 后端日志 (postImageText):"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "tail -n $NEW_BACKEND_LINES ${BACKEND_LOG}" | grep -E "postImageText|URL|下载|图片|image|post_image_text_xhs|发布任务|ERROR|Exception" | tail -20
            INITIAL_BACKEND_LINES=$CURRENT_BACKEND_LINES
        fi
        
        # 显示新增的小红书日志
        if [ $NEW_LINES -gt 0 ]; then
            echo ""
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "📱 小红书发布日志:"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "tail -n $NEW_LINES ${LOG_FILE}" | grep -E "正在上传图文|Browser launched|Cookie|访问主页|打开.*发布页面|检查当前标签页|切换到.*上传图文|找到.*上传输入框|准备上传文件|文件已设置|等待.*上传完成|检测到.*上传成功|填充标题|填充话题|步骤9|步骤10|步骤11|步骤12|点击.*发布|发布成功|ERROR|❌|✅|SUCCESS" | tail -30
            INITIAL_LINES=$CURRENT_LINES
        fi
    fi
    
    sleep 2
done

