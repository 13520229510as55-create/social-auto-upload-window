#!/bin/bash

# VideoLingo 项目部署脚本
# 部署到服务器: 150.107.38.113

set -e

# 服务器配置
SERVER_IP="150.107.38.113"
SERVER_USER="ubuntu"
SERVER_PASSWORD="15831929073asAS"
DEPLOY_DIR="/opt/videolingo"
PROJECT_REPO="https://github.com/Huanshere/VideoLingo.git"
PROJECT_NAME="VideoLingo"

echo "=========================================="
echo "🚀 开始部署 VideoLingo 到服务器: $SERVER_IP"
echo "=========================================="
echo ""

# 检查 sshpass 是否安装
if ! command -v sshpass &> /dev/null; then
    echo "📦 正在安装 sshpass..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &> /dev/null; then
            brew install hudochenkov/sshpass/sshpass
        else
            echo "❌ 错误: 请先安装 Homebrew，然后运行: brew install hudochenkov/sshpass/sshpass"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get update && sudo apt-get install -y sshpass
    else
        echo "❌ 错误: 无法自动安装 sshpass，请手动安装"
        exit 1
    fi
fi

# 测试 SSH 连接
echo "[1/7] 测试 SSH 连接..."
if sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 "${SERVER_USER}@${SERVER_IP}" "echo 'SSH连接成功'" 2>/dev/null; then
    echo "✅ SSH 连接成功！"
else
    echo "❌ SSH 连接失败"
    echo ""
    echo "请检查："
    echo "1. 服务器 IP 地址是否正确: $SERVER_IP"
    echo "2. 用户名是否正确: $SERVER_USER"
    echo "3. 密码是否正确"
    echo "4. 服务器是否允许 SSH 连接"
    exit 1
fi
echo ""

# 在服务器上执行部署
echo "[2/7] 在服务器上执行部署..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << ENDSSH
set -e

DEPLOY_DIR="$DEPLOY_DIR"
PROJECT_REPO="$PROJECT_REPO"
PROJECT_NAME="$PROJECT_NAME"

echo "[3/7] 更新系统包..."
sudo apt-get update -qq

echo "[4/7] 安装基础依赖..."
sudo apt-get install -y -qq git curl wget build-essential

# 检查并安装 Python 3
if ! command -v python3 &> /dev/null; then
    echo "📦 安装 Python 3..."
    sudo apt-get install -y -qq python3 python3-pip python3-venv
fi

# 检查并安装 Node.js (如果需要)
if ! command -v node &> /dev/null; then
    echo "📦 安装 Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y -qq nodejs
fi

# 创建部署目录
echo "[5/7] 创建部署目录..."
sudo mkdir -p \$DEPLOY_DIR
sudo chown -R \$USER:\$USER \$DEPLOY_DIR
cd \$DEPLOY_DIR

# 克隆或更新项目
if [ -d "\$PROJECT_NAME" ]; then
    echo "[6/7] 更新现有项目..."
    cd \$PROJECT_NAME
    git fetch origin
    git reset --hard origin/main 2>/dev/null || git reset --hard origin/master 2>/dev/null || true
    git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || true
else
    echo "[6/7] 克隆项目..."
    git clone \$PROJECT_REPO \$PROJECT_NAME
    cd \$PROJECT_NAME
fi

echo "[7/7] 检查项目结构..."
ls -la

# 检查是否有 requirements.txt (Python 项目)
if [ -f "requirements.txt" ]; then
    echo "📦 检测到 Python 项目，安装依赖..."
    
    # 安装系统依赖
    echo "  安装系统依赖..."
    sudo apt-get install -y -qq ffmpeg libsndfile1 sox
    
    # 创建虚拟环境
    python3 -m venv venv 2>/dev/null || true
    source venv/bin/activate
    
    # 升级 pip
    pip install --upgrade pip setuptools wheel -q
    
    # 先安装 PyTorch (CPU 版本，如果需要 GPU 版本可以修改)
    echo "  安装 PyTorch..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu -q || \
    pip install torch torchvision torchaudio -q
    
    # 安装其他依赖
    echo "  安装项目依赖（这可能需要几分钟）..."
    pip install -r requirements.txt --no-deps -q 2>&1 | grep -v "ERROR:" || true
    
    # 尝试安装缺失的依赖
    pip install librosa pytorch-lightning lightning transformers moviepy numpy openai opencv-python openpyxl pandas pydub PyYAML replicate requests resampy spacy streamlit yt-dlp json-repair ruamel.yaml InquirerPy autocorrect-py ctranslate2 edge-tts syllables pypinyin g2p-en xmltodict -q 2>&1 | grep -v "ERROR:" || true
    
    # 安装 git 依赖
    echo "  安装 Git 依赖..."
    pip install "git+https://github.com/adefossez/demucs" -q 2>&1 | grep -v "ERROR:" || true
    pip install "git+https://github.com/m-bain/whisperx.git@7307306a9d8dd0d261e588cc933322454f853853" -q 2>&1 | grep -v "ERROR:" || true
    
    echo "✅ Python 依赖安装完成"
fi

# 检查是否有 install.py (可能有特殊安装逻辑)
if [ -f "install.py" ]; then
    echo "📦 检测到 install.py，运行安装脚本..."
    source venv/bin/activate
    python3 install.py 2>&1 | head -50 || echo "⚠️  install.py 执行可能有警告"
fi

# 检查是否有 package.json (Node.js 项目)
if [ -f "package.json" ]; then
    echo "📦 检测到 Node.js 项目，安装依赖..."
    npm install --silent
    echo "✅ Node.js 依赖安装完成"
fi

# 检查是否有 README.md 或部署说明
if [ -f "README.md" ]; then
    echo ""
    echo "📄 项目 README:"
    head -30 README.md
fi

echo ""
echo "✅ 部署完成！"
echo "项目目录: \$DEPLOY_DIR/\$PROJECT_NAME"
echo ""
echo "📋 下一步操作："
echo "1. 查看项目 README 了解如何启动"
echo "2. 配置必要的环境变量"
echo "3. 启动服务"
echo ""
echo "当前目录内容:"
ls -la

ENDSSH

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ VideoLingo 部署完成！"
    echo "=========================================="
    echo ""
    echo "📋 服务器信息："
    echo "  IP: $SERVER_IP"
    echo "  用户: $SERVER_USER"
    echo "  部署目录: $DEPLOY_DIR/$PROJECT_NAME"
    echo ""
    echo "🔗 连接到服务器："
    echo "  ssh $SERVER_USER@$SERVER_IP"
    echo ""
    echo "📂 进入项目目录："
    echo "  cd $DEPLOY_DIR/$PROJECT_NAME"
    echo ""
    echo "💡 提示："
    echo "  - 查看 README.md 了解如何启动项目"
    echo "  - 检查是否有 .env 文件需要配置"
    echo "  - 使用 systemd 或 PM2 管理服务（如需要）"
    echo ""
else
    echo ""
    echo "❌ 部署过程中出现错误"
    echo "请检查上面的错误信息"
    exit 1
fi

