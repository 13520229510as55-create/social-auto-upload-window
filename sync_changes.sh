#!/bin/bash
# 同步修改的文件到 Windows 服务器

SERVER_IP="39.105.227.6"
SERVER_USER="administrator"
SERVER_PASS="15831929073asAS"
REMOTE_DIR="/c/social-auto-upload-window"

echo "=========================================="
echo "🔄 同步修改文件到 Windows 服务器"
echo "服务器: ${SERVER_IP}"
echo "=========================================="
echo ""

# 修改的文件列表
FILES_TO_SYNC=(
    "myUtils/auth.py"
    "sau_frontend/vite.config.js"
)

# 检查 SSH 连接
echo "📡 检查服务器连接..."
if command -v sshpass &> /dev/null && command -v ssh &> /dev/null; then
    # 测试 SSH 连接（端口 22）
    if sshpass -p "$SERVER_PASS" ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no -p 22 "${SERVER_USER}@${SERVER_IP}" "echo Connected" 2>/dev/null; then
        echo "✅ SSH 连接成功"
        echo ""
        
        # 同步文件
        for file in "${FILES_TO_SYNC[@]}"; do
            echo "📤 上传: $file"
            
            # 创建远程目录
            remote_dir=$(dirname "$REMOTE_DIR/$file")
            sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no -p 22 "${SERVER_USER}@${SERVER_IP}" "mkdir -p '$remote_dir'" 2>/dev/null
            
            # 上传文件
            if sshpass -p "$SERVER_PASS" scp -o StrictHostKeyChecking=no -P 22 "$file" "${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/$file" 2>/dev/null; then
                echo "   ✅ 成功"
            else
                echo "   ❌ 失败"
            fi
        done
        
        echo ""
        echo "=========================================="
        echo "✅ 同步完成！"
        echo "=========================================="
        echo ""
        echo "🔄 请在服务器上重启服务："
        echo "   1. 停止当前运行的服务"
        echo "   2. 重新运行: python sau_backend.py"
        echo "   3. 前端: cd sau_frontend && npm run dev"
        
    else
        echo "❌ SSH 连接失败（端口 22）"
        USE_MANUAL=1
    fi
else
    echo "⚠️  未安装 sshpass 或 ssh 工具"
    USE_MANUAL=1
fi

# 如果 SSH 失败，提供手动方案
if [ ! -z "$USE_MANUAL" ]; then
    echo ""
    echo "=========================================="
    echo "📋 手动同步方案"
    echo "=========================================="
    echo ""
    echo "请手动将以下文件复制到服务器："
    echo ""
    
    for file in "${FILES_TO_SYNC[@]}"; do
        full_path="$(pwd)/$file"
        echo "📁 本地: $full_path"
        echo "   ➜ 服务器: C:\\social-auto-upload-window\\${file//\//\\}"
        echo ""
    done
    
    echo "步骤："
    echo "1. 使用远程桌面连接到 ${SERVER_IP}"
    echo "2. 将上述文件复制到对应位置"
    echo "3. 重启服务"
    echo ""
fi

