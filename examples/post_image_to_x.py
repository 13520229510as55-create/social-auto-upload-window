#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
X (Twitter) API v1 发图示例
使用 tweepy 库实现
"""

import tweepy
from pathlib import Path
from typing import List, Optional

def post_image_to_x(
    api_key: str,
    api_secret_key: str,
    access_token: str,
    access_token_secret: str,
    image_path: str,
    text: str = "",
    media_category: str = "tweet_image"
) -> dict:
    """
    使用 X API v1 发布带图片的推文
    
    Args:
        api_key: API Key
        api_secret_key: API Secret Key
        access_token: Access Token
        access_token_secret: Access Token Secret
        image_path: 图片文件路径
        text: 推文文本内容（可选）
        media_category: 媒体类别（默认: tweet_image）
    
    Returns:
        推文数据字典
    
    Raises:
        FileNotFoundError: 图片文件不存在
        tweepy.TweepyException: API 调用失败
    """
    # 验证图片文件是否存在
    image_file = Path(image_path)
    if not image_file.exists():
        raise FileNotFoundError(f"图片文件不存在: {image_path}")
    
    # OAuth 1.0a 认证
    auth = tweepy.OAuth1UserHandler(
        api_key,
        api_secret_key,
        access_token,
        access_token_secret
    )
    api = tweepy.API(auth, wait_on_rate_limit=True)
    
    # 上传图片
    print(f"📤 正在上传图片: {image_path}")
    media = api.media_upload(
        image_path,
        media_category=media_category
    )
    print(f"✅ 图片上传成功，media_id: {media.media_id}")
    
    # 发布推文
    if text:
        print(f"📝 发布推文: {text}")
    else:
        print("📝 发布推文（无文本）")
    
    tweet = api.update_status(
        status=text,
        media_ids=[media.media_id]
    )
    
    print(f"✅ 推文发布成功！")
    print(f"   Tweet ID: {tweet.id}")
    print(f"   链接: https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}")
    
    return {
        'tweet_id': tweet.id,
        'text': tweet.text,
        'media_id': media.media_id,
        'url': f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}"
    }


def post_multiple_images_to_x(
    api_key: str,
    api_secret_key: str,
    access_token: str,
    access_token_secret: str,
    image_paths: List[str],
    text: str = ""
) -> dict:
    """
    发布包含多张图片的推文（最多4张）
    
    Args:
        api_key: API Key
        api_secret_key: API Secret Key
        access_token: Access Token
        access_token_secret: Access Token Secret
        image_paths: 图片文件路径列表（最多4张）
        text: 推文文本内容（可选）
    
    Returns:
        推文数据字典
    """
    # 限制最多4张图片
    image_paths = image_paths[:4]
    
    # OAuth 1.0a 认证
    auth = tweepy.OAuth1UserHandler(
        api_key,
        api_secret_key,
        access_token,
        access_token_secret
    )
    api = tweepy.API(auth, wait_on_rate_limit=True)
    
    # 上传所有图片
    media_ids = []
    for image_path in image_paths:
        image_file = Path(image_path)
        if not image_file.exists():
            print(f"⚠️  跳过不存在的文件: {image_path}")
            continue
        
        print(f"📤 正在上传图片: {image_path}")
        media = api.media_upload(image_path)
        media_ids.append(media.media_id)
        print(f"✅ 图片上传成功，media_id: {media.media_id}")
    
    if not media_ids:
        raise ValueError("没有成功上传任何图片")
    
    # 发布推文
    print(f"📝 发布推文，包含 {len(media_ids)} 张图片")
    tweet = api.update_status(
        status=text,
        media_ids=media_ids
    )
    
    print(f"✅ 推文发布成功！")
    print(f"   Tweet ID: {tweet.id}")
    print(f"   链接: https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}")
    
    return {
        'tweet_id': tweet.id,
        'text': tweet.text,
        'media_ids': media_ids,
        'url': f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}"
    }


if __name__ == "__main__":
    # 配置 API 凭证（请替换为实际的凭证）
    API_KEY = "YOUR_API_KEY"
    API_SECRET_KEY = "YOUR_API_SECRET_KEY"
    ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"
    ACCESS_TOKEN_SECRET = "YOUR_ACCESS_TOKEN_SECRET"
    
    # 示例1: 发布单张图片
    try:
        result = post_image_to_x(
            api_key=API_KEY,
            api_secret_key=API_SECRET_KEY,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_TOKEN_SECRET,
            image_path="path/to/image.jpg",
            text="这是一条带图片的推文 #测试"
        )
        print(f"\n发布结果: {result}")
    except Exception as e:
        print(f"❌ 发布失败: {e}")
    
    # 示例2: 发布多张图片
    # try:
    #     result = post_multiple_images_to_x(
    #         api_key=API_KEY,
    #         api_secret_key=API_SECRET_KEY,
    #         access_token=ACCESS_TOKEN,
    #         access_token_secret=ACCESS_TOKEN_SECRET,
    #         image_paths=[
    #             "path/to/image1.jpg",
    #             "path/to/image2.jpg",
    #             "path/to/image3.jpg"
    #         ],
    #         text="这是一条包含多张图片的推文 #测试"
    #     )
    #     print(f"\n发布结果: {result}")
    # except Exception as e:
    #     print(f"❌ 发布失败: {e}")


