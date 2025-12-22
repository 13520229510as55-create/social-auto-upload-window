#!/bin/bash
# 搭建简单的 HTTP 代理服务器（使用 Squid 或 3proxy）

set -e

echo "=========================================="
echo "🚀 搭建简单的 HTTP 代理服务器"
echo "=========================================="

# 检查是否为 root
if [ "$EUID" -ne 0 ]; then 
    sudo bash "$0"
    exit $?
fi

# 安装 3proxy（轻量级代理）
echo "[1/3] 安装 3proxy..."
if ! command -v 3proxy &> /dev/null; then
    apt-get update -qq
    apt-get install -y 3proxy > /dev/null 2>&1
fi

# 配置 3proxy
echo "[2/3] 配置 3proxy..."
PROXY_PORT=10810
cat > /etc/3proxy/3proxy.cfg <<EOF
daemon
maxconn 200
nserver 8.8.8.8
nserver 8.8.4.4
nscache 65536
timeouts 1 5 30 60 180 1800 15 60
log /var/log/3proxy.log D
logformat "- %U %C:%c %R:%r %O %I %h %T"
rotate 30
auth none
allow * * * 80-88,8080-8088 HTTP
allow * * * 443,8443 HTTPS
proxy -p${PROXY_PORT}
EOF

# 启动服务
echo "[3/3] 启动 3proxy..."
systemctl enable 3proxy
systemctl restart 3proxy

sleep 2
if systemctl is-active --quiet 3proxy; then
    echo "✅ 3proxy 服务运行中"
else
    echo "❌ 3proxy 启动失败，尝试使用 Python 简单代理..."
    # 备用方案：使用 Python 简单 HTTP 代理
    cat > /tmp/simple_proxy.py <<'PYEOF'
#!/usr/bin/env python3
import socketserver
import urllib.request
import urllib.parse

class ProxyHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(4096).decode('utf-8', errors='ignore')
        if not data:
            return
        
        lines = data.split('\n')
        if not lines:
            return
        
        request_line = lines[0]
        parts = request_line.split()
        if len(parts) < 2:
            return
        
        method = parts[0]
        url = parts[1]
        
        if method == 'CONNECT':
            # HTTPS 代理
            self.request.sendall(b'HTTP/1.1 200 Connection Established\r\n\r\n')
            return
        
        # HTTP 代理
        try:
            if url.startswith('http://') or url.startswith('https://'):
                target_url = url
            else:
                target_url = 'http://' + url
            
            req = urllib.request.Request(target_url)
            for line in lines[1:]:
                if ':' in line:
                    key, value = line.split(':', 1)
                    if key.lower() not in ['host', 'connection', 'proxy-connection']:
                        req.add_header(key.strip(), value.strip())
            
            with urllib.request.urlopen(req, timeout=30) as response:
                self.request.sendall(f'HTTP/1.1 {response.status} {response.reason}\r\n'.encode())
                for header, value in response.headers.items():
                    self.request.sendall(f'{header}: {value}\r\n'.encode())
                self.request.sendall(b'\r\n')
                self.request.sendall(response.read())
        except Exception as e:
            error_msg = f'HTTP/1.1 500 Error\r\n\r\nError: {str(e)}'
            self.request.sendall(error_msg.encode())

if __name__ == '__main__':
    PORT = 10810
    with socketserver.TCPServer(("0.0.0.0", PORT), ProxyHandler) as server:
        print(f"HTTP 代理服务器运行在端口 {PORT}")
        server.serve_forever()
PYEOF
    chmod +x /tmp/simple_proxy.py
    nohup python3 /tmp/simple_proxy.py > /tmp/proxy.log 2>&1 &
    echo "✅ Python 代理服务器已启动（后台运行）"
fi

# 配置防火墙
echo ""
echo "🔧 配置防火墙..."
if command -v ufw &> /dev/null; then
    ufw allow ${PROXY_PORT}/tcp
    echo "✅ 防火墙规则已添加"
fi

echo ""
echo "=========================================="
echo "✅ HTTP 代理服务器搭建完成！"
echo "=========================================="
echo "代理地址: http://$(curl -s ifconfig.me):${PROXY_PORT}"
echo "=========================================="

