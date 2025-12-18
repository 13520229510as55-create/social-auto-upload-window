#!/bin/bash
# 监控话题功能测试的日志

SERVER_IP="150.107.38.113"
SERVER_USER="ubuntu"
SERVER_PASSWORD="15831929073asAS"
LOG_FILE="/home/ubuntu/social-auto-upload/logs/xiaohongshu.log"

echo "=========================================="
echo "🔍 监控小红书图文发布 - 话题功能测试"
echo "=========================================="
echo ""
echo "📋 监控说明:"
echo "1. 我将实时显示发布过程的日志"
echo "2. 重点关注话题相关的日志"
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
echo "实时日志输出（重点关注话题相关）:"
echo "----------------------------------------"
echo ""

# 实时监控日志
while true; do
    CURRENT_LINE_COUNT=$(sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "wc -l $LOG_FILE 2>/dev/null | awk '{print \$1}'" || echo "0")
    
    if [ "$CURRENT_LINE_COUNT" -gt "$LAST_LINE_COUNT" ]; then
        # 有新日志，显示新增部分
        NEW_LINES=$((CURRENT_LINE_COUNT - LAST_LINE_COUNT))
        sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "tail -n $NEW_LINES $LOG_FILE" | grep -E "话题|标签|tag|步骤10|方法1|方法2|方法3|找到话题|添加话题|话题.*添加成功|话题输入框|JavaScript|ql-editor|contenteditable" || sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "tail -n $NEW_LINES $LOG_FILE"
        LAST_LINE_COUNT=$CURRENT_LINE_COUNT
    fi
    
    # 检查是否超过10分钟
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))
    if [ $ELAPSED -gt 600 ]; then
        echo ""
        echo "⏰ 监控已运行10分钟，自动停止"
        break
    fi
    
    sleep 1
done

echo ""
echo "----------------------------------------"
echo "📊 话题功能测试分析"
echo "----------------------------------------"
echo ""

# 分析最近的日志
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
cd /home/ubuntu/social-auto-upload
echo "最近的话题相关日志:"
tail -500 logs/xiaohongshu.log | grep -E "话题|标签|tag|步骤10" | tail -30
echo ""
echo "话题添加成功记录:"
tail -500 logs/xiaohongshu.log | grep -E "话题.*添加成功|总共添加.*话题" | tail -10
echo ""
echo "话题输入框定位记录:"
tail -500 logs/xiaohongshu.log | grep -E "找到话题输入框|话题选择器|方法1|方法2|方法3" | tail -15
echo ""
echo "错误信息:"
tail -500 logs/xiaohongshu.log | grep -E "ERROR|Exception|失败|话题.*失败" | tail -10
ENDSSH

echo ""
echo "✅ 监控完成"
echo ""
echo "📋 验证清单:"
echo "   1. 检查日志中是否显示'找到话题输入框'"
echo "   2. 检查日志中是否显示所有话题都'添加成功'"
echo "   3. 在小红书APP或网页版查看发布的内容"
echo "   4. 验证话题是否出现在发布的内容中"





