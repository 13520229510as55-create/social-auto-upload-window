# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。

import re
from urllib.parse import urlparse, parse_qs

from model.m_juejin import ArticleUrlInfo, CreatorUrlInfo


def parse_article_info_from_url(url: str) -> ArticleUrlInfo:
    """
    从掘金文章URL中解析出文章ID
    支持以下格式:
    1. 普通文章链接: https://juejin.cn/post/1234567890
    2. 短链接: https://juejin.cn/pin/1234567890
    3. 纯ID: 1234567890

    Args:
        url: 掘金文章链接或ID
    Returns:
        ArticleUrlInfo: 包含文章ID的对象
    """
    # 如果是纯数字ID,直接返回
    if url.isdigit():
        return ArticleUrlInfo(article_id=url, user_id="")

    # 从URL中提取文章ID
    # 匹配 /post/数字 或 /pin/数字
    patterns = [
        r'/post/(\d+)',
        r'/pin/(\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            article_id = match.group(1)
            return ArticleUrlInfo(article_id=article_id, user_id="")

    raise ValueError(f"无法从URL中解析出文章ID: {url}")


def parse_creator_info_from_url(url: str) -> CreatorUrlInfo:
    """
    从掘金用户URL中解析出用户ID
    支持以下格式:
    1. 用户主页: https://juejin.cn/user/1234567890
    2. 用户主页: https://juejin.cn/user/username

    Args:
        url: 掘金用户链接
    Returns:
        CreatorUrlInfo: 包含用户ID的对象
    """
    # 从URL中提取用户ID
    pattern = r'/user/([^/?]+)'
    match = re.search(pattern, url)
    if match:
        user_id = match.group(1)
        return CreatorUrlInfo(user_id=user_id)

    raise ValueError(f"无法从URL中解析出用户ID: {url}")

