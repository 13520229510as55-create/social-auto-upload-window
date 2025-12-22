#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时监控后端日志脚本（Python版本）
支持彩色输出和关键词高亮
"""

import sys
import time
import subprocess
from pathlib import Path

# 颜色定义
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    RESET = '\033[0m'

LOG_FILE = Path("/tmp/backend.log")

def colorize_line(line: str) -> str:
    """根据日志内容添加颜色"""
    line_lower = line.lower()
    
    # 错误/异常
    if any(keyword in line_lower for keyword in ['error', '错误', '失败', 'exception', 'traceback', '❌', '失败']):
        return f"{Colors.RED}{line}{Colors.RESET}"
    
    # 成功
    if any(keyword in line_lower for keyword in ['success', '成功', '✅', '完成', '✓']):
        return f"{Colors.GREEN}{line}{Colors.RESET}"
    
    # 警告
    if any(keyword in line_lower for keyword in ['warning', '警告', '⚠️']):
        return f"{Colors.YELLOW}{line}{Colors.RESET}"
    
    # 信息
    if any(keyword in line_lower for keyword in ['info:', '信息', '📊', '📋', '📝']):
        return f"{Colors.CYAN}{line}{Colors.RESET}"
    
    # 调试
    if any(keyword in line_lower for keyword in ['debug', '调试']):
        return f"{Colors.BLUE}{line}{Colors.RESET}"
    
    # 爬取相关
    if any(keyword in line_lower for keyword in ['爬取', '爬虫', 'crawler', '任务', 'task']):
        return f"{Colors.MAGENTA}{line}{Colors.RESET}"
    
    # Cookie/登录相关
    if any(keyword in line_lower for keyword in ['cookie', '登录', 'login', '二维码', 'qrcode']):
        return f"{Colors.CYAN}{line}{Colors.RESET}"
    
    return line

def main():
    print("=" * 50)
    print("📊 实时监控后端日志")
    print("=" * 50)
    print(f"日志文件: {LOG_FILE}")
    print("")
    
    # 检查日志文件是否存在
    if not LOG_FILE.exists():
        print(f"⚠️  日志文件不存在: {LOG_FILE}")
        print("正在等待日志文件创建...")
        for i in range(10):
            time.sleep(1)
            if LOG_FILE.exists():
                print("✅ 日志文件已创建")
                break
        else:
            print("❌ 日志文件仍未创建，请检查后端服务是否正在运行")
            sys.exit(1)
    
    print("✅ 开始监控日志...")
    print("按 Ctrl+C 停止监控")
    print("=" * 50)
    print("")
    
    try:
        # 使用 tail -f 实时监控日志
        process = subprocess.Popen(
            ['tail', '-f', str(LOG_FILE)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # 实时读取并输出
        for line in iter(process.stdout.readline, ''):
            if line:
                colored_line = colorize_line(line.rstrip())
                print(colored_line)
                sys.stdout.flush()
    
    except KeyboardInterrupt:
        print("\n\n✅ 监控已停止")
        process.terminate()
        sys.exit(0)
    except Exception as e:
        print(f"❌ 监控出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

