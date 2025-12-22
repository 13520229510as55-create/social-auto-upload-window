# -*- coding: utf-8 -*-
"""
测试API接口
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_platforms():
    """测试获取平台列表"""
    print("测试获取平台列表...")
    response = requests.get(f"{BASE_URL}/platforms")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_get_config():
    """测试获取配置"""
    print("测试获取小红书配置...")
    response = requests.get(f"{BASE_URL}/config/xhs")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_dashboard_stats():
    """测试获取总览统计"""
    print("测试获取总览统计...")
    response = requests.get(f"{BASE_URL}/dashboard/stats")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_tasks():
    """测试获取任务列表"""
    print("测试获取任务列表...")
    response = requests.get(f"{BASE_URL}/tasks")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

if __name__ == "__main__":
    print("=" * 50)
    print("MediaCrawler Admin API 测试")
    print("=" * 50)
    print()
    
    try:
        test_platforms()
        test_get_config()
        test_dashboard_stats()
        test_tasks()
        print("所有测试完成！")
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到API服务器，请确保后端服务已启动 (python main.py)")
    except Exception as e:
        print(f"错误: {e}")

