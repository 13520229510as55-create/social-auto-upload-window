#!/bin/bash
# 安全重启n8n服务

SERVER_IP="150.107.38.113"
SERVER_USER="ubuntu"
SERVER_PASSWORD="15831929073asAS"

echo "=========================================="
echo "重启 n8n 服务"
echo "=========================================="
echo ""

sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
echo "【步骤1: 检查当前n8n状态】"
ps aux | grep -E 'n8n|node.*n8n' | grep -v grep
echo ""

echo "【步骤2: 停止n8n】"
# 尝试优雅停止
if pgrep -f "node /usr/local/bin/n8n" > /dev/null; then
    echo "  发送TERM信号..."
    pkill -TERM -f "node /usr/local/bin/n8n"
    sleep 5
    
    # 检查是否还在运行
    if pgrep -f "node /usr/local/bin/n8n" > /dev/null; then
        echo "  进程仍在运行，发送KILL信号..."
        pkill -9 -f "node /usr/local/bin/n8n"
        sleep 2
    fi
    echo "✅ n8n已停止"
else
    echo "  n8n未运行"
fi
echo ""

echo "【步骤3: 等待进程完全退出】"
sleep 3
if pgrep -f "n8n" > /dev/null; then
    echo "  ⚠️  仍有n8n相关进程在运行"
    ps aux | grep n8n | grep -v grep
else
    echo "✅ 所有n8n进程已停止"
fi
echo ""

echo "【步骤4: 检查内存配置】"
if [ -f ~/.n8n/config ]; then
    echo "  配置文件内容:"
    cat ~/.n8n/config | grep NODE_OPTIONS | sed 's/^/    /'
    echo ""
    echo "  环境变量将自动加载"
else
    echo "  ⚠️  未找到配置文件，将使用默认配置"
fi
echo ""

echo "【步骤5: 启动n8n】"
echo "  启动命令: n8n start"
echo "  注意: 如果使用systemd，请使用: sudo systemctl start n8n"
echo ""
echo "  手动启动请执行:"
echo "    cd ~ && n8n start"
echo ""
echo "  或后台启动:"
echo "    nohup n8n start > ~/n8n.log 2>&1 &"
echo ""

echo "【步骤6: 验证启动】"
echo "  等待5秒后检查进程..."
sleep 5
if pgrep -f "node /usr/local/bin/n8n" > /dev/null; then
    echo "✅ n8n已启动"
    ps aux | grep 'node /usr/local/bin/n8n' | grep -v grep | awk '{print "  PID: " $2 ", 内存: " $6/1024 "MB"}'
    echo ""
    echo "  测试健康检查:"
    sleep 2
    curl -s http://localhost:5678/healthz && echo " ✅ 健康检查通过" || echo " ⚠️  健康检查失败，请稍等片刻"
else
    echo "  ⚠️  n8n未启动，请手动启动"
fi
ENDSSH

echo ""
echo "=========================================="
echo "重启完成"
echo "=========================================="

