#!/bin/bash
# 上传修复后的代码到服务器

SERVER_IP="150.107.38.113"
SERVER_USER="ubuntu"
SERVER_PASS="15831929073asAS"
REMOTE_DIR="/home/ubuntu/social-auto-upload"

echo "🚀 开始上传修复后的代码到服务器..."
echo "=========================================="

# 重试函数
upload_with_retry() {
    local file=$1
    local remote_path=$2
    local max_retries=5
    local retry=0
    
    while [ $retry -lt $max_retries ]; do
        echo ""
        echo "📤 尝试上传: $file (第 $((retry+1)) 次)"
        
        if sshpass -p "$SERVER_PASS" scp -o StrictHostKeyChecking=no -o ConnectTimeout=30 "$file" "${SERVER_USER}@${SERVER_IP}:${remote_path}" 2>&1; then
            echo "✅ 上传成功: $file"
            return 0
        else
            retry=$((retry+1))
            if [ $retry -lt $max_retries ]; then
                echo "⚠️  上传失败，等待 5 秒后重试..."
                sleep 5
            fi
        fi
    done
    
    echo "❌ 上传失败: $file (已重试 $max_retries 次)"
    return 1
}

# 上传文件
echo ""
echo "📤 上传文件列表:"
echo "  1. uploader/tencent_uploader/main.py"
echo "  2. test_tencent_full_flow_server.py"
echo ""

# 上传主文件
upload_with_retry "uploader/tencent_uploader/main.py" "${REMOTE_DIR}/uploader/tencent_uploader/main.py"

# 上传测试脚本
upload_with_retry "test_tencent_full_flow_server.py" "${REMOTE_DIR}/test_tencent_full_flow_server.py"

echo ""
echo "=========================================="
echo "✅ 上传完成！"
echo ""
echo "📋 验证文件:"
sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=30 "${SERVER_USER}@${SERVER_IP}" "cd ${REMOTE_DIR} && ls -lh uploader/tencent_uploader/main.py test_tencent_full_flow_server.py 2>&1" 2>&1 || echo "⚠️  无法验证，但文件可能已上传"

