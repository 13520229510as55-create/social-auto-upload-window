#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""解压部署包脚本"""
import zipfile
import os
import shutil

zip_path = r'C:\temp\social-auto-upload-window-deploy.zip'
extract_path = r'C:\temp\extracted'
target_path = r'C:\social-auto-upload-window'

# 清理目标目录
if os.path.exists(target_path):
    shutil.rmtree(target_path)

# 创建目录
os.makedirs(extract_path, exist_ok=True)
os.makedirs(target_path, exist_ok=True)

# 解压
print("正在解压文件...")
with zipfile.ZipFile(zip_path, 'r') as z:
    z.extractall(extract_path)

# 复制文件
src = os.path.join(extract_path, 'social-auto-upload-window')
if os.path.exists(src):
    print("正在复制文件...")
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(target_path, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)
    print("✅ 文件部署完成")
else:
    print("❌ 源目录不存在")

