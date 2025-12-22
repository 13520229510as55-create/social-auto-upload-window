#!/bin/bash
# 在海外服务器上搭建 V2Ray 代理服务器

set -e

echo "=========================================="
echo "🚀 开始搭建 V2Ray 代理服务器"
echo "=========================================="
echo ""

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  需要 root 权限，使用 sudo 运行"
    sudo bash "$0"
    exit $?
fi

# 更新系统
echo "[1/5] 更新系统包..."
apt-get update -qq
apt-get install -y curl wget unzip > /dev/null 2>&1

# 安装 V2Ray
echo "[2/5] 安装 V2Ray..."
if command -v v2ray &> /dev/null; then
    echo "✅ V2Ray 已安装"
    V2RAY_VERSION=$(v2ray version | head -1 | awk '{print $2}')
    echo "   版本: $V2RAY_VERSION"
else
    echo "📥 下载并安装 V2Ray..."
    bash <(curl -L https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh)
fi

# 生成 UUID
echo "[3/5] 生成配置..."
UUID=$(cat /proc/sys/kernel/random/uuid)
PORT=10808  # 代理端口

# 创建 V2Ray 配置
echo "[4/5] 配置 V2Ray..."
cat > /usr/local/etc/v2ray/config.json <<EOF
{
  "log": {
    "loglevel": "warning"
  },
  "inbounds": [
    {
      "port": ${PORT},
      "protocol": "vmess",
      "settings": {
        "clients": [
          {
            "id": "${UUID}",
            "alterId": 0
          }
        ]
      },
      "streamSettings": {
        "network": "ws",
        "wsSettings": {
          "path": "/v2ray"
        }
      }
    },
    {
      "port": 10809,
      "protocol": "socks",
      "settings": {
        "auth": "noauth",
        "udp": true
      }
    },
    {
      "port": 10810,
      "protocol": "http",
      "settings": {
        "allowTransparent": false
      }
    }
  ],
  "outbounds": [
    {
      "protocol": "freedom",
      "settings": {}
    }
  ]
}
EOF

# 启动 V2Ray 服务
echo "[5/5] 启动 V2Ray 服务..."
systemctl enable v2ray
systemctl restart v2ray

# 检查服务状态
sleep 2
if systemctl is-active --quiet v2ray; then
    echo "✅ V2Ray 服务运行中"
else
    echo "❌ V2Ray 服务启动失败"
    systemctl status v2ray
    exit 1
fi

# 配置防火墙
echo ""
echo "🔧 配置防火墙..."
if command -v ufw &> /dev/null; then
    ufw allow ${PORT}/tcp
    ufw allow 10809/tcp
    ufw allow 10810/tcp
    echo "✅ 防火墙规则已添加"
elif command -v firewall-cmd &> /dev/null; then
    firewall-cmd --permanent --add-port=${PORT}/tcp
    firewall-cmd --permanent --add-port=10809/tcp
    firewall-cmd --permanent --add-port=10810/tcp
    firewall-cmd --reload
    echo "✅ 防火墙规则已添加"
else
    echo "⚠️  未检测到防火墙，请手动开放端口: ${PORT}, 10809, 10810"
fi

# 输出配置信息
echo ""
echo "=========================================="
echo "✅ V2Ray 代理服务器搭建完成！"
echo "=========================================="
echo ""
echo "📋 服务器信息:"
echo "   服务器 IP: $(curl -s ifconfig.me || hostname -I | awk '{print $1}')"
echo "   VMess 端口: ${PORT}"
echo "   SOCKS5 端口: 10809"
echo "   HTTP 代理端口: 10810"
echo "   UUID: ${UUID}"
echo ""
echo "📝 阿里云服务器配置 (conf.py):"
echo "   HTTP_PROXY = \"http://$(curl -s ifconfig.me || hostname -I | awk '{print $1}'):10810\""
echo "   HTTPS_PROXY = \"http://$(curl -s ifconfig.me || hostname -I | awk '{print $1}'):10810\""
echo ""
echo "💡 或者使用 SOCKS5 代理（需要安装 proxychains 或类似工具）"
echo "=========================================="

