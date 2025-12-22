#!/usr/bin/env python3
"""
远程部署脚本 - 尝试多种方式连接到 Windows 服务器
"""
import os
import subprocess
import sys
from pathlib import Path

SERVER_IP = "39.105.227.6"
SERVER_USER = "administrator"
SERVER_PASS = "15831929073asAS"
TEMP_DIR = r"C:\temp"
PROJECT_DIR = r"C:\social-auto-upload-window"

def try_ssh_upload():
    """尝试通过 SSH 上传文件"""
    print("[方法1] 尝试通过 SSH 连接...")
    zip_file = Path.home() / "social-auto-upload-window-deploy.zip"
    deploy_bat = Path(__file__).parent / "deploy_on_windows.bat"
    
    if not zip_file.exists():
        print(f"❌ 找不到部署包: {zip_file}")
        return False
    
    # 测试 SSH 连接
    test_cmd = [
        "sshpass", "-p", SERVER_PASS,
        "ssh", "-o", "StrictHostKeyChecking=no",
        "-o", "ConnectTimeout=5",
        f"{SERVER_USER}@{SERVER_IP}",
        "echo 'SSH连接成功'"
    ]
    
    try:
        result = subprocess.run(test_cmd, capture_output=True, timeout=10)
        if result.returncode == 0:
            print("✅ SSH 连接成功，开始上传文件...")
            
            # 创建目录
            mkdir_cmd = [
                "sshpass", "-p", SERVER_PASS,
                "ssh", "-o", "StrictHostKeyChecking=no",
                f"{SERVER_USER}@{SERVER_IP}",
                f"mkdir -p {TEMP_DIR.replace(chr(92), '/')}"
            ]
            subprocess.run(mkdir_cmd, capture_output=True)
            
            # 上传文件
            scp_cmd = [
                "sshpass", "-p", SERVER_PASS,
                "scp", "-o", "StrictHostKeyChecking=no",
                str(zip_file),
                f"{SERVER_USER}@{SERVER_IP}:{TEMP_DIR.replace(chr(92), '/')}/"
            ]
            result = subprocess.run(scp_cmd, capture_output=True)
            if result.returncode == 0:
                print("✅ 部署包上传成功")
                
                # 上传部署脚本
                scp_cmd2 = [
                    "sshpass", "-p", SERVER_PASS,
                    "scp", "-o", "StrictHostKeyChecking=no",
                    str(deploy_bat),
                    f"{SERVER_USER}@{SERVER_IP}:{TEMP_DIR.replace(chr(92), '/')}/"
                ]
                subprocess.run(scp_cmd2, capture_output=True)
                print("✅ 部署脚本上传成功")
                
                print("\n📋 文件已上传，请在服务器上执行：")
                print(f"   cd {TEMP_DIR}")
                print("   deploy_on_windows.bat")
                return True
            else:
                print(f"❌ 上传失败: {result.stderr.decode()}")
        else:
            print("⚠️  SSH 连接失败（服务器可能未开启 SSH）")
    except Exception as e:
        print(f"⚠️  SSH 连接异常: {e}")
    
    return False

def print_manual_steps():
    """打印手动部署步骤"""
    zip_file = Path.home() / "social-auto-upload-window-deploy.zip"
    deploy_bat = Path(__file__).parent / "deploy_on_windows.bat"
    
    print("\n" + "="*50)
    print("📋 手动部署步骤（推荐）")
    print("="*50)
    print("\n1. 使用远程桌面连接到服务器：")
    print(f"   地址: {SERVER_IP}:3389")
    print(f"   用户名: {SERVER_USER}")
    print(f"   密码: {SERVER_PASS}")
    print("\n2. 上传以下文件到服务器 C:\\temp\\ 目录：")
    print(f"   - {zip_file}")
    print(f"   - {deploy_bat}")
    print("\n3. 在服务器 CMD 中执行：")
    print(f"   cd {TEMP_DIR}")
    print("   deploy_on_windows.bat")
    print("\n4. 部署完成后，启动服务：")
    print(f"   cd {PROJECT_DIR}")
    print("   start-win.bat")
    print("\n" + "="*50)

if __name__ == "__main__":
    print("="*50)
    print("🚀 远程部署到 Windows 服务器")
    print("="*50)
    print()
    
    # 尝试 SSH
    if not try_ssh_upload():
        print_manual_steps()
    
    print("\n✅ 部署准备完成！")

