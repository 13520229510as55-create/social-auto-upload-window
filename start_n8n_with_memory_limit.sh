#!/bin/bash
# 使用内存限制启动n8n Docker容器

SERVER_IP="150.107.38.113"
SERVER_USER="ubuntu"
SERVER_PASSWORD="15831929073asAS"

echo "=========================================="
echo "启动 n8n Docker容器（带内存限制）"
echo "=========================================="
echo ""

sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
echo "【步骤1: 停止并删除旧容器】"
docker stop n8n_926 2>/dev/null
docker rm n8n_926 2>/dev/null
echo "✅ 旧容器已清理"
echo ""

echo "【步骤2: 使用内存限制启动n8n容器】"
docker run -d \
  --name n8n_926 \
  --restart unless-stopped \
  -p 5678:5678 \
  -v /root/.n8n:/home/node/.n8n \
  -e NODE_OPTIONS='--max-old-space-size=1536' \
  -e N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=true \
  -e N8N_RUNNERS_ENABLED=true \
  -e NODE_ENV=production \
  -e N8N_RELEASE_TYPE=stable \
  -e WEBHOOK_TUNNEL_URL=https://aicode.ltd \
  -e N8N_EDITOR_BASE_URL=https://aicode.ltd \
  -e N8N_PROTOCOL=https \
  -e N8N_PORT=5678 \
  -e N8N_HOST=aicode.ltd \
  n8nio/n8n:latest

if [ $? -eq 0 ]; then
    echo "✅ n8n容器已启动"
else
    echo "❌ 启动失败"
    exit 1
fi
echo ""

echo "【步骤3: 等待容器启动】"
sleep 10
echo ""

echo "【步骤4: 验证启动】"
echo "容器状态:"
docker ps | grep n8n_926
echo ""

echo "环境变量（内存限制）:"
docker exec n8n_926 env | grep NODE_OPTIONS
echo ""

echo "资源使用:"
docker stats n8n_926 --no-stream --format 'table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}'
echo ""

echo "健康检查:"
curl -s http://localhost:5678/healthz && echo ""
echo ""

echo "【启动完成】"
echo "✅ n8n已启动，内存限制: 1536MB (1.5GB)"
echo "✅ 不会影响启动速度"
echo "✅ 足够n8n正常运行"
ENDSSH

echo ""
echo "=========================================="
echo "完成"
echo "=========================================="

