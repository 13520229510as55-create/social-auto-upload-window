#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试代理连接"""
import requests
import sys

proxy_url = "http://150.107.38.113:10810"
proxies = {
    'http': proxy_url,
    'https': proxy_url
}

# -*- coding: utf-8 -*-
import sys
import io
# 设置输出编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 50)
print("测试代理服务器连接")
print("=" * 50)
print(f"\n代理地址: {proxy_url}\n")

# 测试 1: 基本连接测试
print("[1/3] 测试代理服务器连接...")
try:
    r = requests.get('https://www.google.com', proxies=proxies, timeout=10, verify=False)
    print(f"✅ 连接成功，状态码: {r.status_code}")
except Exception as e:
    print(f"❌ 连接失败: {str(e)}")
    print("   可能原因: 安全组未配置或代理服务器未运行")
print()

# 测试 2: Google Cloud Storage 连接测试
print("[2/3] 测试 Google Cloud Storage 连接...")
try:
    r = requests.get('https://storage.googleapis.com', proxies=proxies, timeout=10, verify=False)
    print(f"✅ 连接成功，状态码: {r.status_code}")
except Exception as e:
    print(f"❌ 连接失败: {str(e)}")
print()

# 测试 3: 检查配置文件
print("[3/3] 检查配置文件...")
try:
    import sys
    sys.path.insert(0, r'C:\social-auto-upload-window')
    from conf import HTTP_PROXY, HTTPS_PROXY
    print(f"HTTP_PROXY: {HTTP_PROXY}")
    print(f"HTTPS_PROXY: {HTTPS_PROXY}")
except Exception as e:
    print(f"[ERROR] 读取配置失败: {str(e)}")
print()

print("=" * 50)
print("💡 如果连接失败，请检查:")
print("  1. 云服务商安全组是否开放端口 10810")
print("  2. 代理服务器是否正常运行")
print("  3. 防火墙是否阻止连接")
print("=" * 50)

