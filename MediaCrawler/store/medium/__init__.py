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

from typing import Dict, List

import config
from tools import utils
from var import source_keyword_var

from ._store_impl import *


class MediumStoreFactory:
    STORES = {
        "csv": MediumCsvStoreImplement,
        "db": MediumDbStoreImplement,
        "json": MediumJsonStoreImplement,
        "sqlite": MediumSqliteStoreImplement,
        "mongodb": MediumMongoStoreImplement,
        "excel": MediumExcelStoreImplement,
    }

    @staticmethod
    def create_store():
        store_class = MediumStoreFactory.STORES.get(config.SAVE_DATA_OPTION)
        if not store_class:
            raise ValueError("[MediumStoreFactory.create_store] Invalid save option only supported csv or db or json or sqlite or mongodb or excel ...")
        return store_class()


async def update_medium_article(article_item: Dict):
    """更新Medium文章"""
    article_id = article_item.get("id", "") or article_item.get("article_id", "")
    if not article_id:
        return
    
    # Medium的文章数据结构可能不同，需要根据实际API响应调整
    author_info = article_item.get("author", {}) or article_item.get("creator", {})
    
    save_content_item = {
        "article_id": article_id,
        "title": article_item.get("title", ""),
        "desc": article_item.get("subtitle", "") or article_item.get("description", ""),
        "content": article_item.get("content", ""),
        "create_time": article_item.get("createdAt", 0) or article_item.get("created_at", 0),
        "update_time": article_item.get("updatedAt", 0) or article_item.get("updated_at", 0),
        "user_id": author_info.get("userId", "") or author_info.get("id", ""),
        "nickname": author_info.get("name", ""),
        "avatar": author_info.get("image", ""),
        "liked_count": str(article_item.get("claps", 0) or article_item.get("likes", 0)),
        "comment_count": str(article_item.get("responses", 0) or article_item.get("comments", 0)),
        "view_count": str(article_item.get("views", 0)),
        "article_url": article_item.get("url", f"https://medium.com/p/{article_id}"),
        "tags": ",".join([tag.get("name", "") for tag in article_item.get("tags", [])]),
        "source_keyword": source_keyword_var.get(),
    }
    
    utils.logger.info(f"[store.medium.update_medium_article] medium article id:{article_id}, title:{save_content_item.get('title')}")
    await MediumStoreFactory.create_store().store_content(content_item=save_content_item)


async def batch_update_medium_comments(article_id: str, comments: List[Dict]):
    """批量更新Medium评论"""
    for comment_item in comments:
        await update_medium_comment(article_id, comment_item)


async def update_medium_comment(article_id: str, comment_item: Dict):
    """更新Medium评论"""
    comment_id = comment_item.get("comment_id", "") or comment_item.get("id", "")
    if not comment_id:
        return
    
    save_comment_item = {
        "comment_id": comment_id,
        "article_id": article_id,
        "content": comment_item.get("content", ""),
        "user_id": comment_item.get("user_id", ""),
        "nickname": comment_item.get("nickname", ""),
        "avatar": comment_item.get("avatar", ""),
        "like_count": comment_item.get("like_count", 0),
        "create_time": comment_item.get("create_time", 0),
    }
    
    await MediumStoreFactory.create_store().store_comment(comment_item=save_comment_item)

