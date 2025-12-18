#!/bin/bash
# n8n性能优化脚本

SERVER_IP="150.107.38.113"
SERVER_USER="ubuntu"
SERVER_PASSWORD="15831929073asAS"

echo "=========================================="
echo "n8n 性能优化"
echo "=========================================="
echo ""

sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
echo "【步骤1: 检查当前n8n进程】"
ps aux | grep -E 'n8n|node.*n8n' | grep -v grep
echo ""

echo "【步骤2: 重启n8n服务（释放内存）】"
# 尝试使用systemctl重启
if systemctl list-units | grep -q n8n; then
    echo "使用systemctl重启n8n..."
    sudo systemctl restart n8n
    sleep 3
elif pgrep -f "n8n" > /dev/null; then
    echo "找到n8n进程，准备重启..."
    # 优雅地停止n8n
    pkill -TERM -f "node /usr/local/bin/n8n"
    sleep 5
    # 如果还在运行，强制停止
    if pgrep -f "n8n" > /dev/null; then
        pkill -9 -f "n8n"
        sleep 2
    fi
    echo "n8n已停止，请手动启动: n8n start"
else
    echo "未找到运行中的n8n进程"
fi
echo ""

echo "【步骤3: 配置Swap空间（2GB）】"
if [ ! -f /swapfile ]; then
    echo "创建Swap文件..."
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo "/swapfile none swap sw 0 0" | sudo tee -a /etc/fstab
    echo "✅ Swap空间已创建并启用"
else
    echo "Swap文件已存在，检查状态..."
    swapon --show
fi
echo ""

echo "【步骤4: 优化n8n启动配置】"
N8N_SERVICE_FILE="/etc/systemd/system/n8n.service"
if [ -f "$N8N_SERVICE_FILE" ]; then
    echo "找到systemd服务文件，检查配置..."
    cat "$N8N_SERVICE_FILE" | grep -E "MemoryMax|MemoryLimit|NODE_OPTIONS"
    echo ""
    echo "建议在服务文件中添加内存限制："
    echo "  [Service]"
    echo "  MemoryMax=1G"
    echo "  Environment=\"NODE_OPTIONS=--max-old-space-size=512\""
else
    echo "未找到systemd服务文件"
    echo "建议创建 ~/.n8n/config 文件，添加："
    echo "  NODE_OPTIONS=--max-old-space-size=512"
fi
echo ""

echo "【步骤5: 清理僵尸进程】"
ZOMBIE_COUNT=$(ps aux | grep -E '<defunct>|<zombie>' | wc -l)
if [ $ZOMBIE_COUNT -gt 0 ]; then
    echo "发现 $ZOMBIE_COUNT 个僵尸进程"
    echo "查找僵尸进程的父进程..."
    ps aux | grep -E '<defunct>|<zombie>' | head -5
    echo "注意: 需要找到并重启僵尸进程的父进程才能清理"
else
    echo "✅ 没有僵尸进程"
fi
echo ""

echo "【步骤6: 检查优化后的状态】"
sleep 2
echo "系统内存:"
free -h
echo ""
echo "Swap状态:"
swapon --show
echo ""
echo "n8n进程:"
ps aux | grep -E 'n8n|node.*n8n' | grep -v grep || echo "n8n未运行"
echo ""

echo "【优化完成】"
echo "建议："
echo "1. 如果n8n已重启，等待30秒后测试性能"
echo "2. 监控内存使用情况: watch -n 1 free -h"
echo "3. 如果问题持续，考虑升级服务器内存或优化n8n工作流"
ENDSSH

echo ""
echo "=========================================="
echo "优化完成"
echo "=========================================="

