#!/bin/bash

# MoneyPrinterTurbo 自动部署脚本
# 使用方法: 在本地运行此脚本，它会自动在服务器上部署 MoneyPrinterTurbo

set -e

# 服务器配置
SERVER_IP="150.107.38.113"
SERVER_USER="ubuntu"
SERVER_PASSWORD="15831929073asAS"
DEPLOY_DIR="/opt/MoneyPrinterTurbo"
GIT_REPO="https://github.com/harry0703/MoneyPrinterTurbo.git"

echo "=========================================="
echo "🚀 MoneyPrinterTurbo 自动部署脚本"
echo "服务器: $SERVER_IP"
echo "=========================================="
echo ""

# 测试 SSH 连接
echo "[1/7] 测试 SSH 连接..."
if sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 "${SERVER_USER}@${SERVER_IP}" "echo 'SSH连接成功'" 2>/dev/null; then
    echo "✅ SSH 连接成功！"
else
    echo "❌ SSH 连接失败"
    echo ""
    echo "请确保："
    echo "1. 服务器已开启 SSH 服务"
    echo "2. 安全组已开放 22 端口"
    echo "3. 用户名和密码正确"
    exit 1
fi
echo ""

# 在服务器上执行部署
echo "[2/7] 开始服务器部署..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << ENDSSH
set -e

DEPLOY_DIR="$DEPLOY_DIR"
GIT_REPO="$GIT_REPO"

echo "=========================================="
echo "📦 开始部署 MoneyPrinterTurbo"
echo "=========================================="

# 更新系统包
echo "[1/6] 更新系统包..."
sudo apt-get update -qq

# 安装基础依赖
echo "[2/6] 安装基础依赖..."
sudo apt-get install -y -qq \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common \
    git \
    wget

# 检查并安装 Docker
echo "[3/6] 检查 Docker 安装状态..."
if ! command -v docker &> /dev/null; then
    echo "   正在安装 Docker..."
    # 添加 Docker 官方 GPG 密钥
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - 2>/dev/null || true
    
    # 添加 Docker APT 源
    sudo add-apt-repository "deb [arch=\$(dpkg --print-architecture)] https://download.docker.com/linux/ubuntu \$(lsb_release -cs) stable" -y
    
    # 安装 Docker
    sudo apt-get update -qq
    sudo apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # 将当前用户添加到 docker 组（避免每次都需要 sudo）
    sudo usermod -aG docker \$USER || true
    
    echo "   ✅ Docker 安装完成"
else
    echo "   ✅ Docker 已安装"
fi

# 检查并安装 Docker Compose（如果使用独立版本）
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "   正在安装 Docker Compose..."
    DOCKER_COMPOSE_VERSION="2.23.0"
    sudo curl -L "https://github.com/docker/compose/releases/download/v\${DOCKER_COMPOSE_VERSION}/docker-compose-\$(uname -s)-\$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "   ✅ Docker Compose 安装完成"
else
    echo "   ✅ Docker Compose 已安装"
fi

# 创建部署目录
echo "[4/6] 准备项目目录..."
sudo mkdir -p \$DEPLOY_DIR
sudo chown -R \$USER:\$USER \$DEPLOY_DIR
cd \$DEPLOY_DIR

# 克隆或更新项目
if [ -d ".git" ]; then
    echo "   项目已存在，正在更新..."
    git fetch origin
    git reset --hard origin/main || git reset --hard origin/master
    git pull origin main || git pull origin master
else
    echo "   正在克隆项目..."
    if [ -d "MoneyPrinterTurbo" ]; then
        rm -rf MoneyPrinterTurbo
    fi
    git clone \$GIT_REPO .
fi

# 检查配置文件
echo "[5/6] 检查配置文件..."
if [ ! -f "config.toml" ]; then
    if [ -f "config.example.toml" ]; then
        echo "   创建配置文件..."
        cp config.example.toml config.toml
        echo "   ⚠️  请记得配置 config.toml 文件中的 API 密钥"
    else
        echo "   ⚠️  未找到配置文件模板，请手动创建 config.toml"
    fi
else
    echo "   ✅ 配置文件已存在"
fi

# 启动服务
echo "[6/6] 启动服务..."
# 确保在项目目录下
cd \$DEPLOY_DIR

# 检查 docker-compose.yml 是否存在
if [ ! -f "docker-compose.yml" ]; then
    echo "   ❌ 未找到 docker-compose.yml 文件"
    exit 1
fi

# 使用 docker-compose（检查可用性）
if command -v docker-compose &> /dev/null; then
    echo "   使用 docker-compose..."
    docker-compose down 2>/dev/null || true
    docker-compose up -d --build
elif docker compose version &> /dev/null 2>&1; then
    echo "   使用 docker compose (plugin)..."
    docker compose down 2>/dev/null || true
    docker compose up -d --build
else
    echo "   ❌ 未找到 Docker Compose"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ 部署完成！"
echo "=========================================="
echo ""
echo "📋 服务信息："
echo "   项目目录: \$DEPLOY_DIR"
echo "   Web 界面: http://\$(hostname -I 2>/dev/null | awk '{print \$1}' || echo 'SERVER_IP'):8501"
echo ""
echo "📝 常用命令："
echo "   查看日志: docker compose logs -f"
echo "   停止服务: docker compose down"
echo "   重启服务: docker compose restart"
echo "   查看状态: docker compose ps"
echo ""
ENDSSH

# 检查防火墙端口
echo "[3/7] 检查防火墙配置..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'FIREWALL'
if command -v ufw &> /dev/null; then
    echo "   配置 UFW 防火墙..."
    sudo ufw allow 8501/tcp comment "MoneyPrinterTurbo Web UI" || true
    echo "   ✅ 防火墙规则已添加"
elif command -v firewall-cmd &> /dev/null; then
    echo "   配置 firewalld..."
    sudo firewall-cmd --permanent --add-port=8501/tcp || true
    sudo firewall-cmd --reload || true
    echo "   ✅ 防火墙规则已添加"
else
    echo "   ⚠️  未检测到防火墙，请手动开放 8501 端口"
fi
FIREWALL
echo ""

# 等待服务启动
echo "[4/7] 等待服务启动（30秒）..."
sleep 30

# 检查服务状态
echo "[5/7] 检查服务状态..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << STATUS
cd ${DEPLOY_DIR}
if command -v docker-compose &> /dev/null; then
    docker-compose ps
elif docker compose version &> /dev/null 2>&1; then
    docker compose ps
fi
STATUS
echo ""

# 测试 Web 界面
echo "[6/7] 测试 Web 界面连接..."
if curl -s --connect-timeout 5 "http://${SERVER_IP}:8501" > /dev/null; then
    echo "✅ Web 界面可访问"
else
    echo "⚠️  Web 界面暂时无法访问（服务可能还在启动中）"
fi
echo ""

# 显示访问信息
echo "[7/7] 部署完成！"
echo ""
echo "=========================================="
echo "✅ MoneyPrinterTurbo 部署完成！"
echo "=========================================="
echo ""
echo "🌐 访问地址："
echo "   Web 界面: http://${SERVER_IP}:8501"
echo ""
echo "📋 后续操作："
echo "1. 配置 API 密钥（如需要）："
echo "   ssh ${SERVER_USER}@${SERVER_IP}"
echo "   cd ${DEPLOY_DIR}"
echo "   nano config.toml"
echo ""
echo "2. 查看服务日志："
echo "   ssh ${SERVER_USER}@${SERVER_IP}"
echo "   cd ${DEPLOY_DIR}"
echo "   docker compose logs -f"
echo ""
echo "3. 重启服务（修改配置后）："
echo "   cd ${DEPLOY_DIR}"
echo "   docker compose restart"
echo ""
echo "4. 停止服务："
echo "   cd ${DEPLOY_DIR}"
echo "   docker compose down"
echo ""

