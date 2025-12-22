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

from enum import Enum


class SearchSortType(Enum):
    """搜索排序类型"""
    # 默认（综合排序）
    GENERAL = "0"
    # 最新
    LATEST = "1"
    # 最热
    HOTTEST = "2"


class ArticleType(Enum):
    """文章类型"""
    ALL = "all"
    ARTICLE = "article"
    POST = "post"

