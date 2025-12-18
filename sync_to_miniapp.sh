#!/bin/bash
# 自动同步主项目功能到小程序
# 使用方法: ./sync_to_miniapp.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN_PROJECT="$SCRIPT_DIR"
MINIAPP_PROJECT="$SCRIPT_DIR/../social-auto-upload-miniapp"

echo "=========================================="
echo "开始同步主项目功能到小程序"
echo "=========================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 python3，请先安装 Python 3"
    exit 1
fi

# 检查项目路径
if [ ! -d "$MAIN_PROJECT" ]; then
    echo "错误: 主项目路径不存在: $MAIN_PROJECT"
    exit 1
fi

if [ ! -d "$MINIAPP_PROJECT" ]; then
    echo "错误: 小程序项目路径不存在: $MINIAPP_PROJECT"
    echo "请确保小程序项目在: social-auto-upload-miniapp"
    exit 1
fi

# 运行Python同步脚本
cd "$MAIN_PROJECT"
python3 sync_to_miniapp.py

echo ""
echo "=========================================="
echo "同步完成！"
echo "=========================================="
echo ""
echo "下一步："
echo "1. 检查小程序项目中的更改"
echo "2. 在微信开发者工具中测试"
echo "3. 如有问题，查看 sync_report.json 了解详情"
echo ""





