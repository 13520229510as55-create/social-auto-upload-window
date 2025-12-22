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
from urllib.parse import urlparse

from model.m_medium import ArticleUrlInfo, CreatorUrlInfo


def parse_article_info_from_url(url: str) -> ArticleUrlInfo:
    """
    从Medium文章URL中解析出文章ID
    支持以下格式:
    1. 普通文章链接: https://medium.com/@username/article-title-1234567890
    2. 短链接: https://medium.com/p/article-id

    Args:
        url: Medium文章链接
    Returns:
        ArticleUrlInfo: 包含文章ID的对象
    """
    # 从URL中提取文章ID
    # Medium的文章URL格式: https://medium.com/@username/article-slug-{id}
    # 或者: https://medium.com/p/{id}
    
    # 匹配 /p/ 后面的ID
    pattern = r'/p/([a-zA-Z0-9]+)'
    match = re.search(pattern, url)
    if match:
        article_id = match.group(1)
        return ArticleUrlInfo(article_id=article_id, user_id="")
    
    # 尝试从slug中提取ID（通常是URL的最后一部分）
    parts = url.rstrip('/').split('/')
    if len(parts) > 0:
        last_part = parts[-1]
        # 如果最后一部分包含ID（通常是32位十六进制字符串）
        if len(last_part) >= 20:
            article_id = last_part
            return ArticleUrlInfo(article_id=article_id, user_id="")
    
    raise ValueError(f"无法从URL中解析出文章ID: {url}")


def parse_creator_info_from_url(url: str) -> CreatorUrlInfo:
    """
    从Medium用户URL中解析出用户ID
    支持以下格式:
    1. 用户主页: https://medium.com/@username

    Args:
        url: Medium用户链接
    Returns:
        CreatorUrlInfo: 包含用户ID的对象
    """
    # Medium用户URL格式: https://medium.com/@username
    pattern = r'/@([^/?]+)'
    match = re.search(pattern, url)
    if match:
        user_id = match.group(1)
        return CreatorUrlInfo(user_id=user_id)

    raise ValueError(f"无法从URL中解析出用户ID: {url}")

