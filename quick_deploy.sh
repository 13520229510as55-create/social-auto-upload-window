#!/bin/bash
# 快速部署脚本 - 只上传修改的代码文件

SERVER_IP="101.126.158.155"
SERVER_USER="root"
SERVER_PASSWORD="15831929073asAS"
DEPLOY_DIR="/opt/social-auto-upload"

echo "=========================================="
echo "快速部署修改的代码文件"
echo "=========================================="

# 需要上传的文件
FILES=(
    "sau_backend.py"
    "uploader/tencent_uploader/main.py"
)

echo "�� 上传文件到服务器..."
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  上传: $file"
        sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no "$file" ${SERVER_USER}@${SERVER_IP}:${DEPLOY_DIR}/"$file"
    else
        echo "  ⚠️  文件不存在: $file"
    fi
done

echo ""
echo "✅ 文件上传完成！"
echo ""
echo "下一步：请在服务器上重启服务"
echo "  ssh ${SERVER_USER}@${SERVER_IP}"
echo "  cd ${DEPLOY_DIR}"
echo "  ./stop.sh && ./start.sh"
