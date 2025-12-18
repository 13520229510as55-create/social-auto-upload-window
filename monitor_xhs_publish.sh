#!/bin/bash
# 实时监控小红书图文发布过程

SERVER_IP="150.107.38.113"
SERVER_USER="ubuntu"
SERVER_PASSWORD="15831929073asAS"
LOG_FILE="/home/ubuntu/social-auto-upload/logs/backend.log"

echo "=========================================="
echo "🔍 实时监控小红书图文发布过程"
echo "=========================================="
echo ""
echo "📋 监控说明:"
echo "1. 请在浏览器中执行小红书图文发布操作"
echo "2. 我将实时显示发布过程的日志"
echo "3. 按 Ctrl+C 停止监控"
echo ""
echo "⏳ 等待发布请求..."
echo ""

# 记录开始时间
START_TIME=$(date +%s)
LAST_LINE_COUNT=$(sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "wc -l $LOG_FILE 2>/dev/null | awk '{print \$1}'" || echo "0")

echo "开始监控时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "当前日志行数: $LAST_LINE_COUNT"
echo ""
echo "----------------------------------------"
echo "实时日志输出:"
echo "----------------------------------------"
echo ""

# 实时监控日志
while true; do
    CURRENT_LINE_COUNT=$(sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "wc -l $LOG_FILE 2>/dev/null | awk '{print \$1}'" || echo "0")
    
    if [ "$CURRENT_LINE_COUNT" -gt "$LAST_LINE_COUNT" ]; then
        # 有新日志，显示新增部分
        NEW_LINES=$((CURRENT_LINE_COUNT - LAST_LINE_COUNT))
        sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "tail -n $NEW_LINES $LOG_FILE" | grep -E "xiaohongshu|postImageText|upload|Browser|Chromium|找到|成功|失败|ERROR|Exception|发布|正在|完成|图片|标题|上传|Execution context|count|is_visible" || sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "tail -n $NEW_LINES $LOG_FILE"
        LAST_LINE_COUNT=$CURRENT_LINE_COUNT
    fi
    
    # 检查是否超过5分钟
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))
    if [ $ELAPSED -gt 300 ]; then
        echo ""
        echo "⏰ 监控已运行5分钟，自动停止"
        break
    fi
    
    sleep 1
done

echo ""
echo "----------------------------------------"
echo "📊 发布过程分析"
echo "----------------------------------------"
echo ""

# 分析最近的日志
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
cd /home/ubuntu/social-auto-upload
echo "最近的小红书发布相关日志:"
tail -500 logs/backend.log | grep -E "xiaohongshu|postImageText" | tail -50
echo ""
echo "错误信息:"
tail -500 logs/backend.log | grep -E "ERROR|Exception|失败|Traceback" | tail -20
echo ""
echo "成功信息:"
tail -500 logs/backend.log | grep -E "成功|完成|✅" | tail -20
ENDSSH

echo ""
echo "✅ 监控完成"

