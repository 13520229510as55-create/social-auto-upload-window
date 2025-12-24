#!/bin/bash
# 实时监控39服务器上的视频号发布日志

SERVER_IP="39.105.227.6"
SERVER_USER="administrator"
SERVER_PASSWORD="15831929073asAS"

echo "=========================================="
echo "📺 实时监控视频号发布日志 (39服务器)"
echo "=========================================="
echo "服务器: $SERVER_IP"
echo ""
echo "等待新的发布任务..."
echo "按 Ctrl+C 停止监控"
echo "=========================================="
echo ""

# 检查日志文件位置
echo "🔍 查找日志文件..."
LOG_FILES=$(sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "powershell -Command \"Get-ChildItem -Path 'C:\\social-auto-upload-window' -Recurse -Filter '*tencent*.log' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName\" 2>&1")

if [ -z "$LOG_FILES" ] || [ "$LOG_FILES" = "" ]; then
    echo "⚠️  未找到tencent日志文件，监控后端服务输出..."
    echo ""
    echo "监控后端服务控制台输出（实时）..."
    echo "=========================================="
    echo ""
    
    # 监控后端服务的输出（通过SSH实时查看）
    sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
cd C:\social-auto-upload-window
# 查找Python进程并查看其输出
# 由于无法直接查看后台进程输出，我们监控可能的日志文件
Get-ChildItem -Path . -Recurse -Filter "*.log" -ErrorAction SilentlyContinue | 
    Where-Object { $_.LastWriteTime -gt (Get-Date).AddMinutes(-10) } | 
    ForEach-Object { 
        Write-Host "`n=== $($_.Name) ===" -ForegroundColor Cyan
        Get-Content $_.FullName -Tail 20 -ErrorAction SilentlyContinue
    }
ENDSSH
    
    echo ""
    echo "💡 提示: 如果服务在后台运行，请在前台启动以查看实时日志"
    echo "   命令: cd C:\\social-auto-upload-window && python sau_backend.py"
else
    echo "✅ 找到日志文件:"
    echo "$LOG_FILES" | while read -r log_file; do
        if [ ! -z "$log_file" ]; then
            echo "   - $log_file"
        fi
    done
    echo ""
    echo "=========================================="
    echo "🔄 开始实时监控（按 Ctrl+C 停止）..."
    echo "=========================================="
    echo ""
    
    # 使用第一个找到的日志文件
    FIRST_LOG=$(echo "$LOG_FILES" | head -1 | tr -d '\r')
    
    if [ ! -z "$FIRST_LOG" ]; then
        # 实时监控日志，带颜色高亮
        sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "powershell -Command \"Get-Content '$FIRST_LOG' -Wait -Tail 0 -ErrorAction SilentlyContinue\"" 2>/dev/null | while IFS= read -r line; do
            # 根据日志级别添加颜色
            if echo "$line" | grep -q "SUCCESS\|成功\|✅\|cookie更新完毕\|视频发布成功\|视频草稿保存成功"; then
                echo -e "\033[32m$line\033[0m"  # 绿色 - 成功
            elif echo "$line" | grep -q "ERROR\|失败\|❌\|Exception\|超时"; then
                echo -e "\033[31m$line\033[0m"  # 红色 - 错误
            elif echo "$line" | grep -q "WARNING\|警告\|⚠️"; then
                echo -e "\033[33m$line\033[0m"  # 黄色 - 警告
            elif echo "$line" | grep -q "INFO\|信息\|📸\|📄\|正在\|步骤\|上传\|填写\|点击\|等待\|已等待"; then
                echo -e "\033[36m$line\033[0m"  # 青色 - 信息
            else
                echo "$line"  # 默认颜色
            fi
        done
    fi
fi

