#!/bin/bash
# 检查服务器后端服务和Nginx配置

SERVER_IP="101.126.158.155"
SERVER_USER="root"
SERVER_PASSWORD="15831929073asAS"
DEPLOY_DIR="/opt/social-auto-upload"

echo "=========================================="
echo "检查服务器后端服务和Nginx配置"
echo "=========================================="

sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
echo ""
echo "1️⃣ 检查后端服务进程..."
echo "----------------------------------------"
ps aux | grep -E "python.*sau_backend|python3.*sau_backend" | grep -v grep || echo "❌ 未找到后端服务进程"

echo ""
echo "2️⃣ 检查端口占用情况..."
echo "----------------------------------------"
echo "检查端口 5409 (后端服务端口):"
netstat -tlnp | grep 5409 || ss -tlnp | grep 5409 || echo "❌ 端口 5409 未被占用"

echo ""
echo "检查端口 80 (HTTP):"
netstat -tlnp | grep ":80 " || ss -tlnp | grep ":80 " || echo "端口 80 未被占用"

echo ""
echo "检查端口 443 (HTTPS):"
netstat -tlnp | grep ":443 " || ss -tlnp | grep ":443 " || echo "端口 443 未被占用"

echo ""
echo "3️⃣ 检查Nginx服务状态..."
echo "----------------------------------------"
systemctl status nginx --no-pager -l || service nginx status || echo "❌ 无法获取Nginx状态"

echo ""
echo "4️⃣ 检查Nginx配置..."
echo "----------------------------------------"
if [ -f /etc/nginx/nginx.conf ]; then
    echo "✅ Nginx配置文件存在"
    echo "检查相关配置文件:"
    ls -la /etc/nginx/sites-enabled/ 2>/dev/null || ls -la /etc/nginx/conf.d/ 2>/dev/null || echo "未找到站点配置目录"
else
    echo "❌ Nginx配置文件不存在"
fi

echo ""
echo "5️⃣ 检查后端日志（最近20行）..."
echo "----------------------------------------"
cd /opt/social-auto-upload
if [ -f logs/backend.log ]; then
    echo "📋 后端日志（最后20行）:"
    tail -20 logs/backend.log
else
    echo "❌ 后端日志文件不存在"
fi

echo ""
echo "6️⃣ 检查后端服务启动脚本..."
echo "----------------------------------------"
cd /opt/social-auto-upload
if [ -f start.sh ]; then
    echo "✅ start.sh 存在"
    cat start.sh
else
    echo "❌ start.sh 不存在"
fi

echo ""
echo "7️⃣ 检查Python环境..."
echo "----------------------------------------"
cd /opt/social-auto-upload
if [ -d venv ]; then
    echo "✅ 虚拟环境存在"
    source venv/bin/activate
    python3 --version
    which python3
else
    echo "❌ 虚拟环境不存在"
fi

echo ""
echo "8️⃣ 尝试手动启动后端服务（测试）..."
echo "----------------------------------------"
cd /opt/social-auto-upload
if [ -f sau_backend.py ]; then
    echo "✅ sau_backend.py 存在"
    echo "检查文件权限:"
    ls -la sau_backend.py
else
    echo "❌ sau_backend.py 不存在"
fi

ENDSSH

echo ""
echo "=========================================="
echo "检查完成"
echo "=========================================="


