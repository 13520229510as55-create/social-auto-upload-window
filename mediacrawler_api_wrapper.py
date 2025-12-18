#!/usr/bin/env python3
"""
MediaCrawler HTTP API 包装器
最小化改造，为 MediaCrawler 提供 HTTP API 接口，方便 n8n 调用
"""

from flask import Flask, jsonify, request
import json
import subprocess
import os
from pathlib import Path
from datetime import datetime
import sqlite3
import time

app = Flask(__name__)

# MediaCrawler 项目路径（根据实际情况修改）
MEDIACRAWLER_DIR = Path("/path/to/MediaCrawler")  # 修改为实际路径
OUTPUT_DIR = Path("./mediacrawler_output")
OUTPUT_DIR.mkdir(exist_ok=True)

def standardize_mediacrawler_data(raw_data, platform):
    """
    将 MediaCrawler 的原始数据转换为统一格式
    """
    standardized = []
    
    for item in raw_data:
        # 根据平台类型提取数据
        if platform == 'xhs':  # 小红书
            standardized_item = {
                "source": "mediacrawler",
                "source_platform": "xiaohongshu",
                "content_id": item.get('note_id') or item.get('id', ''),
                "title": item.get('title', ''),
                "content": item.get('desc', '') or item.get('content', ''),
                "author": item.get('user_name', ''),
                "author_id": item.get('user_id', ''),
                "url": item.get('url', '') or f"https://www.xiaohongshu.com/explore/{item.get('note_id', '')}",
                "published_at": item.get('time', '') or item.get('create_time', ''),
                "media_urls": item.get('images', []) or item.get('video_url', []),
                "tags": item.get('tag_list', []) or [],
                "metadata": item
            }
        elif platform == 'dy':  # 抖音
            standardized_item = {
                "source": "mediacrawler",
                "source_platform": "douyin",
                "content_id": item.get('aweme_id') or item.get('id', ''),
                "title": item.get('desc', ''),
                "content": item.get('desc', ''),
                "author": item.get('author', {}).get('nickname', ''),
                "author_id": item.get('author', {}).get('uid', ''),
                "url": item.get('share_url', '') or f"https://www.douyin.com/video/{item.get('aweme_id', '')}",
                "published_at": item.get('create_time', ''),
                "media_urls": [item.get('video_url', '')] if item.get('video_url') else [],
                "tags": item.get('hashtag_list', []) or [],
                "metadata": item
            }
        elif platform == 'ks':  # 快手
            standardized_item = {
                "source": "mediacrawler",
                "source_platform": "kuaishou",
                "content_id": item.get('photo_id') or item.get('id', ''),
                "title": item.get('caption', ''),
                "content": item.get('caption', ''),
                "author": item.get('user_name', ''),
                "author_id": item.get('user_id', ''),
                "url": item.get('share_url', '') or f"https://www.kuaishou.com/short-video/{item.get('photo_id', '')}",
                "published_at": item.get('create_time', ''),
                "media_urls": [item.get('video_url', '')] if item.get('video_url') else [],
                "tags": [],
                "metadata": item
            }
        else:
            # 通用格式
            standardized_item = {
                "source": "mediacrawler",
                "source_platform": platform,
                "content_id": item.get('id', ''),
                "title": item.get('title', '') or item.get('desc', ''),
                "content": item.get('content', '') or item.get('desc', ''),
                "author": item.get('author', '') or item.get('user_name', ''),
                "author_id": item.get('author_id', '') or item.get('user_id', ''),
                "url": item.get('url', ''),
                "published_at": item.get('published_at', '') or item.get('create_time', ''),
                "media_urls": item.get('media_urls', []) or [],
                "tags": item.get('tags', []) or [],
                "metadata": item
            }
        
        standardized.append(standardized_item)
    
    return standardized

@app.route('/api/crawl', methods=['POST'])
def crawl_data():
    """
    触发 MediaCrawler 爬取并返回标准化数据
    """
    data = request.json or {}
    platform = data.get('platform', 'xhs')
    crawl_type = data.get('type', 'search')  # search 或 detail
    
    try:
        # 构建 MediaCrawler 命令
        # 注意：这里需要根据实际的 MediaCrawler 命令格式调整
        cmd = [
            'uv', 'run', 'main.py',
            '--platform', platform,
            '--lt', 'qrcode',
            '--type', crawl_type,
            '--save_data_option', 'json'  # 输出 JSON 格式
        ]
        
        # 执行爬取（异步，实际应该用后台任务）
        # 这里简化处理，实际应该用 celery 或类似工具
        output_file = OUTPUT_DIR / f"{platform}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # 运行 MediaCrawler（需要在实际的 MediaCrawler 目录中）
        os.chdir(MEDIACRAWLER_DIR)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10分钟超时
        )
        
        if result.returncode != 0:
            return jsonify({
                "code": 500,
                "msg": f"爬取失败: {result.stderr}",
                "data": None
            }), 500
        
        # 读取输出文件（MediaCrawler 应该输出到指定位置）
        # 这里需要根据实际输出路径调整
        data_file = MEDIACRAWLER_DIR / "data" / f"{platform}_*.json"
        # 找到最新的文件
        import glob
        files = glob.glob(str(data_file))
        if not files:
            return jsonify({
                "code": 404,
                "msg": "未找到输出文件",
                "data": None
            }), 404
        
        latest_file = max(files, key=os.path.getctime)
        
        # 读取并标准化数据
        with open(latest_file, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        standardized_data = standardize_mediacrawler_data(raw_data, platform)
        
        return jsonify({
            "code": 200,
            "msg": "爬取成功",
            "data": standardized_data
        }), 200
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "msg": f"处理失败: {str(e)}",
            "data": None
        }), 500

@app.route('/api/latest', methods=['GET'])
def get_latest():
    """
    获取最新爬取的数据（从数据库或文件）
    """
    platform = request.args.get('platform', 'xhs')
    
    try:
        # 从数据库读取（如果 MediaCrawler 使用数据库）
        # 或者从最新文件读取
        data_file = MEDIACRAWLER_DIR / "data" / f"{platform}_*.json"
        import glob
        files = glob.glob(str(data_file))
        
        if not files:
            return jsonify({
                "code": 404,
                "msg": "未找到数据文件",
                "data": []
            }), 404
        
        latest_file = max(files, key=os.path.getctime)
        
        # 检查文件是否在最近1小时内更新
        file_time = os.path.getmtime(latest_file)
        if time.time() - file_time > 3600:
            return jsonify({
                "code": 200,
                "msg": "数据已过期",
                "data": []
            }), 200
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        standardized_data = standardize_mediacrawler_data(raw_data, platform)
        
        return jsonify({
            "code": 200,
            "msg": "获取成功",
            "data": standardized_data
        }), 200
    
    except Exception as e:
        return jsonify({
            "code": 500,
            "msg": f"获取失败: {str(e)}",
            "data": None
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        "code": 200,
        "msg": "服务正常",
        "data": {
            "status": "healthy",
            "timestamp": datetime.now().isoformat()
        }
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

