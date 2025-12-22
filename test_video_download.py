#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试视频下载功能"""
import sys
import os
sys.path.insert(0, r'C:\social-auto-upload-window')

# 设置输出编码
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("测试视频下载功能（通过代理）")
print("=" * 60)
print()

# 测试 URL（使用一个小的测试文件）
test_url = "https://storage.googleapis.com/n8n-test-3344/f2918f70-13f8-4aee-99a0-f6ac8547842a_output_0.mp4"

try:
    from sau_backend import download_video_from_url
    from conf import HTTP_PROXY, HTTPS_PROXY
    
    print(f"代理配置:")
    print(f"  HTTP_PROXY: {HTTP_PROXY}")
    print(f"  HTTPS_PROXY: {HTTPS_PROXY}")
    print()
    print(f"测试 URL: {test_url}")
    print()
    print("开始下载...")
    print("-" * 60)
    
    # 调用下载函数
    result = download_video_from_url(test_url, max_retries=3)
    
    print("-" * 60)
    print(f"[OK] 下载成功！")
    print(f"文件名: {result}")
    print()
    print("=" * 60)
    print("测试完成！视频下载功能正常工作。")
    print("=" * 60)
    
except Exception as e:
    print(f"[ERROR] 下载失败: {str(e)}")
    import traceback
    traceback.print_exc()
    print()
    print("=" * 60)
    print("测试失败，请检查:")
    print("  1. 代理服务器是否正常运行")
    print("  2. 安全组是否已配置")
    print("  3. 后端代码是否正确")
    print("=" * 60)

