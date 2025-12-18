#!/bin/bash
# 实时监控视频号发布日志（带颜色高亮）

SERVER_IP="150.107.38.113"
SERVER_USER="ubuntu"
SERVER_PASSWORD="15831929073asAS"
LOG_FILE="/home/ubuntu/social-auto-upload/logs/tencent.log"

echo "=========================================="
echo "📺 实时监控视频号发布日志"
echo "=========================================="
echo "服务器: $SERVER_IP"
echo "日志文件: $LOG_FILE"
echo ""
echo "等待新的发布任务..."
echo "按 Ctrl+C 停止监控"
echo "=========================================="
echo ""

# 实时监控日志，带颜色高亮
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "tail -n 0 -f $LOG_FILE" 2>/dev/null | while IFS= read -r line; do
    # 根据日志级别添加颜色
    if echo "$line" | grep -q "SUCCESS\|成功\|✅\|cookie更新完毕\|视频发布成功\|视频草稿保存成功"; then
        echo -e "\033[32m$line\033[0m"  # 绿色 - 成功
    elif echo "$line" | grep -q "ERROR\|失败\|❌\|Exception"; then
        echo -e "\033[31m$line\033[0m"  # 红色 - 错误
    elif echo "$line" | grep -q "WARNING\|警告\|⚠️"; then
        echo -e "\033[33m$line\033[0m"  # 黄色 - 警告
    elif echo "$line" | grep -q "INFO\|信息\|📸\|📄\|正在\|步骤\|上传\|填写\|点击\|等待"; then
        echo -e "\033[36m$line\033[0m"  # 青色 - 信息
    else
        echo "$line"  # 默认颜色
    fi
done

