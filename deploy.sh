#!/bin/bash

# 服务器部署脚本
# 使用方法: 在本地运行此脚本，它会自动上传项目到服务器并部署

set -e

# 服务器配置
SERVER_IP="101.126.158.155"
SERVER_USER="root"
SERVER_PASSWORD="15831929073asAS"
DEPLOY_DIR="/opt/social-auto-upload"
PROJECT_NAME="social-auto-upload"

echo "=========================================="
echo "开始部署到服务器: $SERVER_IP"
echo "=========================================="

# 1. 打包项目（排除不需要的文件）
echo "📦 正在打包项目..."
tar --exclude='node_modules' \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.env' \
    --exclude='videoFile/*' \
    --exclude='cookiesFile/*' \
    --exclude='logs/*' \
    -czf /tmp/${PROJECT_NAME}.tar.gz .

# 2. 上传到服务器
echo "📤 正在上传项目到服务器..."
sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no /tmp/${PROJECT_NAME}.tar.gz ${SERVER_USER}@${SERVER_IP}:/tmp/

# 3. 在服务器上执行部署
echo "🚀 正在服务器上部署..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
set -e

DEPLOY_DIR="/opt/social-auto-upload"
PROJECT_NAME="social-auto-upload"

# 创建部署目录
mkdir -p $DEPLOY_DIR
cd $DEPLOY_DIR

# 解压项目
echo "📂 解压项目文件..."
tar -xzf /tmp/${PROJECT_NAME}.tar.gz -C $DEPLOY_DIR
rm /tmp/${PROJECT_NAME}.tar.gz

# 创建必要的目录
mkdir -p videoFile cookiesFile logs db

# 安装系统依赖
echo "📥 安装系统依赖..."
PYTHON_CMD=python3
if command -v apt-get &> /dev/null; then
    apt-get update
    apt-get install -y python3.10 python3.10-venv python3.10-dev python3-pip nodejs npm curl
    PYTHON_CMD=python3.10
elif command -v yum &> /dev/null; then
    # CentOS/RHEL: 尝试安装 Python 3.10
    yum install -y gcc openssl-devel bzip2-devel libffi-devel zlib-devel readline-devel sqlite-devel wget make
    # 检查是否已有 python3.10
    if ! command -v python3.10 &> /dev/null; then
        echo "⚠️  需要安装 Python 3.10，这可能需要一些时间..."
        cd /tmp
        if [ ! -d "Python-3.10.13" ]; then
            wget -q https://www.python.org/ftp/python/3.10.13/Python-3.10.13.tgz
            tar xzf Python-3.10.13.tgz
        fi
        cd Python-3.10.13
        ./configure --prefix=/usr/local --enable-optimizations --with-ensurepip=install
        make -j$(nproc)
        make altinstall
        cd /
    fi
    yum install -y nodejs npm curl git
    PYTHON_CMD=python3.10
fi

# 创建 Python 虚拟环境
echo "🐍 创建 Python 虚拟环境 (使用 $PYTHON_CMD)..."
if [ ! -d "venv" ]; then
    $PYTHON_CMD -m venv venv
fi
source venv/bin/activate

# 安装 Python 依赖
echo "📦 安装 Python 依赖..."
pip install --upgrade pip
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 安装 Playwright 浏览器驱动
echo "🌐 安装 Playwright 浏览器驱动..."
playwright install chromium firefox

# 初始化数据库
echo "💾 初始化数据库..."
cd db
python3 createTable.py
cd ..

# 配置 conf.py（如果不存在）
if [ ! -f "conf.py" ]; then
    cp conf.example.py conf.py
    # 设置 Chrome 路径（Linux）
    sed -i 's|LOCAL_CHROME_PATH = ""|LOCAL_CHROME_PATH = "/usr/bin/google-chrome"|g' conf.py
    sed -i 's|LOCAL_CHROME_HEADLESS = True|LOCAL_CHROME_HEADLESS = True|g' conf.py
fi

# 安装前端依赖并构建
echo "🎨 构建前端..."
cd sau_frontend
npm install --registry=https://registry.npmmirror.com
npm run build
cd ..

echo "✅ 部署完成！"
echo "项目目录: $DEPLOY_DIR"
ENDSSH

echo ""
echo "=========================================="
echo "✅ 部署完成！"
echo "=========================================="
echo "服务器地址: http://$SERVER_IP:5409"
echo ""
echo "下一步："
echo "1. 在服务器上启动服务:"
echo "   ssh $SERVER_USER@$SERVER_IP"
echo "   cd $DEPLOY_DIR"
echo "   ./start.sh"
echo ""
echo "2. 或使用 systemd 服务:"
echo "   sudo systemctl start social-auto-upload"
echo "   sudo systemctl enable social-auto-upload"

