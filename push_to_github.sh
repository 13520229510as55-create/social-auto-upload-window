#!/bin/bash
# GitHub 代码推送脚本

echo "📤 准备推送到 GitHub..."
echo ""

# 读取 Token
read -p "请输入您的 GitHub Personal Access Token: " TOKEN

if [ -z "$TOKEN" ]; then
    echo "❌ Token 不能为空"
    exit 1
fi

# 配置远程仓库 URL
git remote set-url origin https://$\{TOKEN\}@github.com/13520229510as55-create/social-upload.git

# 推送代码
echo "🚀 开始推送..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 推送成功！"
    echo "📦 仓库地址: https://github.com/13520229510as55-create/social-upload"
else
    echo ""
    echo "❌ 推送失败，请检查："
    echo "   1. 仓库是否已创建"
    echo "   2. Token 是否正确"
    echo "   3. Token 是否有 repo 权限"
fi
