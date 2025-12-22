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

from typing import Dict

from base.base_crawler import AbstractStore
from tools.async_file_writer import AsyncFileWriter
from var import crawler_type_var
from database.mongodb_store_base import MongoDBStoreBase
from store.excel_store_base import ExcelStoreBase


class MediumCsvStoreImplement(AbstractStore):
    """Medium CSV存储实现"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.writer = AsyncFileWriter(platform="medium", crawler_type=crawler_type_var.get())

    async def store_content(self, content_item: Dict):
        await self.writer.write_to_csv(item_type="contents", item=content_item)

    async def store_comment(self, comment_item: Dict):
        await self.writer.write_to_csv(item_type="comments", item=comment_item)

    async def store_creator(self, creator_item: Dict):
        pass

    def flush(self):
        pass


class MediumJsonStoreImplement(AbstractStore):
    """Medium JSON存储实现"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.writer = AsyncFileWriter(platform="medium", crawler_type=crawler_type_var.get())

    async def store_content(self, content_item: Dict):
        await self.writer.write_single_item_to_json(item_type="contents", item=content_item)

    async def store_comment(self, comment_item: Dict):
        await self.writer.write_single_item_to_json(item_type="comments", item=comment_item)

    async def store_creator(self, creator_item: Dict):
        pass

    def flush(self):
        pass


class MediumDbStoreImplement(AbstractStore):
    """Medium数据库存储实现（待实现）"""
    async def store_content(self, content_item: Dict):
        pass

    async def store_comment(self, comment_item: Dict):
        pass

    async def store_creator(self, creator_item: Dict):
        pass


class MediumSqliteStoreImplement(MediumDbStoreImplement):
    """Medium SQLite存储实现（待实现）"""
    pass


class MediumMongoStoreImplement(AbstractStore):
    """Medium MongoDB存储实现"""
    def __init__(self):
        self.mongo_store = MongoDBStoreBase(collection_prefix="medium")

    async def store_content(self, content_item: Dict):
        article_id = content_item.get("article_id")
        if not article_id:
            return
        await self.mongo_store.save_or_update(
            collection_suffix="contents",
            query={"article_id": article_id},
            data=content_item
        )

    async def store_comment(self, comment_item: Dict):
        comment_id = comment_item.get("comment_id")
        if not comment_id:
            return
        await self.mongo_store.save_or_update(
            collection_suffix="comments",
            query={"comment_id": comment_id},
            data=comment_item
        )

    async def store_creator(self, creator_item: Dict):
        user_id = creator_item.get("user_id")
        if not user_id:
            return
        await self.mongo_store.save_or_update(
            collection_suffix="creators",
            query={"user_id": user_id},
            data=creator_item
        )


class MediumExcelStoreImplement:
    """Medium Excel存储实现（待实现）"""
    pass

