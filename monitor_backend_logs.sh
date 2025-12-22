#!/bin/bash
# 实时监控后端日志脚本

LOG_FILE="/tmp/backend.log"
COLOR_ENABLED=true

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

echo "=========================================="
echo "📊 实时监控后端日志"
echo "=========================================="
echo "日志文件: $LOG_FILE"
echo ""

# 检查日志文件是否存在
if [ ! -f "$LOG_FILE" ]; then
    echo "⚠️  日志文件不存在: $LOG_FILE"
    echo "正在等待日志文件创建..."
    # 等待文件创建（最多等待10秒）
    for i in {1..10}; do
        sleep 1
        if [ -f "$LOG_FILE" ]; then
            echo "✅ 日志文件已创建"
            break
        fi
    done
    if [ ! -f "$LOG_FILE" ]; then
        echo "❌ 日志文件仍未创建，请检查后端服务是否正在运行"
        exit 1
    fi
fi

echo "✅ 开始监控日志..."
echo "按 Ctrl+C 停止监控"
echo "=========================================="
echo ""

# 实时监控日志，带颜色高亮
tail -f "$LOG_FILE" 2>/dev/null | while IFS= read -r line; do
    if [ "$COLOR_ENABLED" = true ]; then
        # 根据日志级别和关键词添加颜色
        if echo "$line" | grep -qE "ERROR|错误|失败|Exception|Traceback|❌|失败|error|Error"; then
            echo -e "${RED}$line${NC}"
        elif echo "$line" | grep -qE "SUCCESS|成功|✅|完成|success|Success|✓"; then
            echo -e "${GREEN}$line${NC}"
        elif echo "$line" | grep -qE "WARNING|警告|⚠️|warning|Warning"; then
            echo -e "${YELLOW}$line${NC}"
        elif echo "$line" | grep -qE "INFO|信息|📊|📋|📝|info|Info|INFO:"; then
            echo -e "${CYAN}$line${NC}"
        elif echo "$line" | grep -qE "DEBUG|调试|debug|Debug"; then
            echo -e "${BLUE}$line${NC}"
        elif echo "$line" | grep -qE "爬取|爬虫|crawler|Crawler|任务|task|Task"; then
            echo -e "${MAGENTA}$line${NC}"
        elif echo "$line" | grep -qE "Cookie|登录|login|Login|二维码|qrcode"; then
            echo -e "${CYAN}$line${NC}"
        else
            echo "$line"
        fi
    else
        echo "$line"
    fi
done

