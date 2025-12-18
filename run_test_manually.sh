#!/bin/bash
# 手动运行测试的辅助脚本

echo "🚀 视频号发布测试 - 手动运行指南"
echo "=================================="
echo ""
echo "请按照以下步骤操作："
echo ""
echo "1. 连接到服务器："
echo "   ssh ubuntu@150.107.38.113"
echo "   密码: 15831929073asAS"
echo ""
echo "2. 进入项目目录："
echo "   cd /home/ubuntu/social-auto-upload"
echo ""
echo "3. 运行测试："
echo "   python3 test_tencent_full_flow_server.py"
echo ""
echo "4. 查看截图（测试完成后）："
echo "   ls -lh logs/screenshots/tencent/"
echo ""
echo "=================================="
echo ""
read -p "是否现在连接到服务器？(y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "正在连接..."
    ssh ubuntu@150.107.38.113
fi

