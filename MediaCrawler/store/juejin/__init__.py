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

from typing import List

import config
from tools import utils
from var import source_keyword_var

from ._store_impl import *


class JueJinStoreFactory:
    STORES = {
        "csv": JueJinCsvStoreImplement,
        "db": JueJinDbStoreImplement,
        "json": JueJinJsonStoreImplement,
        "sqlite": JueJinSqliteStoreImplement,
        "mongodb": JueJinMongoStoreImplement,
        "excel": JueJinExcelStoreImplement,
    }

    @staticmethod
    def create_store():
        store_class = JueJinStoreFactory.STORES.get(config.SAVE_DATA_OPTION)
        if not store_class:
            raise ValueError("[JueJinStoreFactory.create_store] Invalid save option only supported csv or db or json or sqlite or mongodb or excel ...")
        return store_class()


async def update_juejin_article(article_item: Dict):
    """更新掘金文章
    
    Args:
        article_item: 文章数据，格式为result_model，包含：
            - article_id: 文章ID
            - article_info: 文章详细信息
            - author_user_info: 作者信息
            - tags: 标签列表（在result_model顶层）
            - category: 分类信息（在result_model顶层）
    """
    article_id = article_item.get("article_id", "")
    if not article_id:
        utils.logger.warning(f"[store.juejin.update_juejin_article] article_item缺少article_id: {list(article_item.keys())}")
        return
    
    user_info = article_item.get("author_user_info", {})
    article_info = article_item.get("article_info", {})
    # tags和category在result_model顶层，不在article_info中
    tags_list = article_item.get("tags", [])
    category_info = article_item.get("category", {})
    
    save_content_item = {
        "article_id": article_id,
        "title": article_info.get("title", ""),
        "desc": article_info.get("brief_content", ""),
        "content": article_info.get("content", ""),
        "create_time": article_info.get("ctime", 0),
        "update_time": article_info.get("mtime", 0),
        "user_id": user_info.get("user_id", ""),
        "nickname": user_info.get("user_name", ""),
        "avatar": user_info.get("avatar_large", ""),
        "liked_count": str(article_info.get("digg_count", 0)),
        "comment_count": str(article_info.get("comment_count", 0)),
        "view_count": str(article_info.get("view_count", 0)),
        "collect_count": str(article_info.get("collect_count", 0)),
        "share_count": str(article_info.get("share_count", 0)),
        "article_url": f"https://juejin.cn/post/{article_id}",
        "tags": ",".join([tag.get("tag_name", "") for tag in tags_list if isinstance(tag, dict)]),
        "category": category_info.get("category_name", ""),
        "source_keyword": source_keyword_var.get(),
    }
    
    utils.logger.info(f"[store.juejin.update_juejin_article] juejin article id:{article_id}, title:{save_content_item.get('title')}")
    await JueJinStoreFactory.create_store().store_content(content_item=save_content_item)


async def batch_update_juejin_comments(article_id: str, comments: List[Dict]):
    """批量更新掘金评论"""
    for comment_item in comments:
        await update_juejin_comment(article_id, comment_item)


async def update_juejin_comment(article_id: str, comment_item: Dict):
    """更新掘金评论"""
    comment_id = comment_item.get("comment_id", "")
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
    
    await JueJinStoreFactory.create_store().store_comment(comment_item=save_comment_item)

