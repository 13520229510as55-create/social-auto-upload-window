#!/bin/bash
# 全自动测试和修复脚本

SERVER_IP="150.107.38.113"
SERVER_USER="ubuntu"
SERVER_PASS="15831929073asAS"
REMOTE_DIR="/home/ubuntu/social-auto-upload"

echo "🚀 开始全自动测试和修复流程..."
echo "=========================================="

# 使用expect自动处理SSH密码
expect << EOF
set timeout 300
spawn ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "cd ${REMOTE_DIR} && python3 test_tencent_full_flow_server.py 2>&1"
expect {
    "password:" {
        send "${SERVER_PASS}\r"
        exp_continue
    }
    "yes/no" {
        send "yes\r"
        exp_continue
    }
    eof
}
wait
EOF

echo ""
echo "📥 下载测试结果和截图..."
expect << EOF
set timeout 60
spawn scp -r -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/logs/screenshots/tencent ./test_results/screenshots/ 2>/dev/null || true
expect {
    "password:" {
        send "${SERVER_PASS}\r"
        exp_continue
    }
    eof
}
EOF

echo "✅ 测试完成，请查看结果"

