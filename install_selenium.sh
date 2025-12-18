#!/bin/bash

echo "=================================="
echo "Selenium 依赖安装脚本"
echo "=================================="
echo ""

# 检查 Python
echo "检查 Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3"
    exit 1
fi
echo "✅ Python3: $(python3 --version)"

# 检查 pip
echo ""
echo "检查 pip..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ 未找到 pip3"
    exit 1
fi
echo "✅ pip3: $(pip3 --version)"

# 安装 Selenium
echo ""
echo "安装 Selenium..."
pip3 install selenium

if [ $? -eq 0 ]; then
    echo "✅ Selenium 安装成功"
else
    echo "❌ Selenium 安装失败"
    exit 1
fi

# 安装 webdriver-manager（自动管理 ChromeDriver）
echo ""
echo "安装 webdriver-manager..."
pip3 install webdriver-manager

if [ $? -eq 0 ]; then
    echo "✅ webdriver-manager 安装成功"
else
    echo "❌ webdriver-manager 安装失败"
    exit 1
fi

# 检查 ChromeDriver
echo ""
echo "检查 ChromeDriver..."
if command -v chromedriver &> /dev/null; then
    echo "✅ ChromeDriver 已安装: $(chromedriver --version)"
else
    echo "⚠️ ChromeDriver 未安装"
    echo "   使用 webdriver-manager 会自动下载"
fi

# 测试 Selenium
echo ""
echo "测试 Selenium 导入..."
python3 -c "from selenium import webdriver; print('✅ Selenium 导入成功')"

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================="
    echo "✅ Selenium 安装完成！"
    echo "=================================="
    echo ""
    echo "使用方法:"
    echo "1. 设置环境变量:"
    echo "   export AUTOMATION_TOOL=selenium"
    echo ""
    echo "2. 重启服务:"
    echo "   pm2 restart sau-backend"
    echo ""
    echo "3. 或者直接启动:"
    echo "   AUTOMATION_TOOL=selenium python sau_backend.py"
    echo ""
else
    echo "❌ Selenium 测试失败"
    exit 1
fi
