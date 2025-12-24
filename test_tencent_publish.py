#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试脚本：模拟完整的视频号发布流程
"""
import sys
import os
from pathlib import Path

# 添加项目路径到sys.path
BASE_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(BASE_DIR))

from myUtils.postVideo import post_video_tencent
from datetime import datetime

def test_tencent_publish():
    """测试视频号发布流程"""
    
    print("=" * 60)
    print("开始测试视频号发布流程")
    print("=" * 60)
    
    # 测试参数
    title = "测试发布-自动化测试"
    files = ["10de1756-e0c6-11f0-a0a2-5254001a4788_f7b15827-e1a9-4a4a-b44e-bc29275792ce_output_0.mp4"]
    tags = []
    account_list = ["38fa9e5a-e0c2-11f0-8f26-cea02fcca853.json"]
    category = None
    enableTimer = 0  # 不定时发布
    videos_per_day = 1
    daily_times = None
    start_days = 0
    is_draft = False
    
    print(f"\n测试参数:")
    print(f"  标题: {title}")
    print(f"  视频文件: {files}")
    print(f"  Cookie文件: {account_list}")
    print(f"  是否定时: {enableTimer}")
    print(f"  是否草稿: {is_draft}")
    print()
    
    # 验证文件是否存在
    video_path = BASE_DIR / "videoFile" / files[0]
    cookie_path = BASE_DIR / "cookiesFile" / account_list[0]
    
    print("验证文件:")
    if video_path.exists():
        size_mb = video_path.stat().st_size / (1024 * 1024)
        print(f"  [OK] 视频文件存在: {video_path} ({size_mb:.2f} MB)")
    else:
        print(f"  [ERROR] 视频文件不存在: {video_path}")
        return
    
    if cookie_path.exists():
        size_kb = cookie_path.stat().st_size / 1024
        print(f"  [OK] Cookie文件存在: {cookie_path} ({size_kb:.2f} KB)")
    else:
        print(f"  [ERROR] Cookie文件不存在: {cookie_path}")
        return
    
    print("\n" + "=" * 60)
    print("开始发布流程...")
    print("=" * 60 + "\n")
    
    try:
        # 调用发布函数
        post_video_tencent(
            title=title,
            files=files,
            tags=tags,
            account_file=account_list,
            category=category,
            enableTimer=enableTimer,
            videos_per_day=videos_per_day,
            daily_times=daily_times,
            start_days=start_days,
            is_draft=is_draft
        )
        
        print("\n" + "=" * 60)
        print("[SUCCESS] 发布流程完成")
        print("=" * 60)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"[ERROR] 发布流程失败: {str(e)}")
        print("=" * 60)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tencent_publish()

