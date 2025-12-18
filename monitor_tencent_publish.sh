#!/bin/bash
# 实时监控视频号发布日志

SERVER_IP="150.107.38.113"
SERVER_USER="ubuntu"
SERVER_PASSWORD="15831929073asAS"
LOG_FILE="/home/ubuntu/social-auto-upload/logs/tencent.log"

echo "=========================================="
echo "📺 开始实时监控视频号发布日志"
echo "=========================================="
echo "服务器: $SERVER_IP"
echo "日志文件: $LOG_FILE"
echo ""
echo "按 Ctrl+C 停止监控"
echo "=========================================="
echo ""

# 实时监控日志，带颜色高亮
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
LOG_FILE="/home/ubuntu/social-auto-upload/logs/tencent.log"

# 如果日志文件不存在，先创建
if [ ! -f "$LOG_FILE" ]; then
    echo "⚠️  日志文件不存在，等待创建..."
    touch "$LOG_FILE"
fi

# 显示最后20行，然后实时监控
echo "📋 最近日志："
echo "----------------------------------------"
tail -20 "$LOG_FILE" 2>/dev/null || echo "日志文件为空或无法读取"
echo ""
echo "=========================================="
echo "🔄 开始实时监控（按 Ctrl+C 停止）..."
echo "=========================================="
echo ""

# 实时监控，带颜色高亮
tail -f "$LOG_FILE" 2>/dev/null | while IFS= read -r line; do
    # 根据日志级别添加颜色
    if echo "$line" | grep -q "SUCCESS\|成功\|✅"; then
        echo -e "\033[32m$line\033[0m"  # 绿色
    elif echo "$line" | grep -q "ERROR\|失败\|❌"; then
        echo -e "\033[31m$line\033[0m"  # 红色
    elif echo "$line" | grep -q "WARNING\|警告\|⚠️"; then
        echo -e "\033[33m$line\033[0m"  # 黄色
    elif echo "$line" | grep -q "INFO\|信息\|📸\|📄"; then
        echo -e "\033[36m$line\033[0m"  # 青色
    else
        echo "$line"  # 默认颜色
    fi
done
ENDSSH

