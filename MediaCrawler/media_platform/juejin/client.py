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

import asyncio
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import httpx
from playwright.async_api import BrowserContext, Page
from tenacity import retry, stop_after_attempt, wait_fixed

import config
from base.base_crawler import AbstractApiClient
from proxy.proxy_mixin import ProxyRefreshMixin
from tools import utils

if TYPE_CHECKING:
    from proxy.proxy_ip_pool import ProxyIpPool

from .exception import DataFetchError, IPBlockError
from .field import SearchSortType


class JueJinClient(AbstractApiClient, ProxyRefreshMixin):
    """掘金客户端"""

    def __init__(
        self,
        timeout=60,
        proxy=None,
        *,
        headers: Dict[str, str],
        playwright_page: Page,
        cookie_dict: Dict[str, str],
        proxy_ip_pool: Optional["ProxyIpPool"] = None,
    ):
        self.proxy = proxy
        self.timeout = timeout
        self.headers = headers
        self._host = "https://api.juejin.cn"
        self.playwright_page = playwright_page
        self.cookie_dict = cookie_dict
        # 初始化代理池（来自 ProxyRefreshMixin）
        self.init_proxy_pool(proxy_ip_pool)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    async def request(self, method, url, **kwargs):
        """发送HTTP请求"""
        # 每次请求前检测代理是否过期
        await self._refresh_proxy_if_expired()

        async with httpx.AsyncClient(proxy=self.proxy, timeout=self.timeout) as client:
            response = await client.request(method, url, **kwargs)
            
            if response.status_code == 403:
                raise IPBlockError("IP被封禁")
            
            if response.status_code != 200:
                raise DataFetchError(f"请求失败，状态码: {response.status_code}, 响应: {response.text[:200]}")
            
            try:
                return response.json()
            except Exception as e:
                raise DataFetchError(f"解析响应失败: {e}, 响应: {response.text[:200]}")

    async def get(self, uri: str, params: Optional[Dict] = None, headers: Optional[Dict] = None):
        """GET请求"""
        url = f"{self._host}{uri}"
        request_headers = headers or self.headers
        if params:
            from urllib.parse import urlencode
            url = f"{url}?{urlencode(params)}"
        return await self.request("GET", url, headers=request_headers)

    async def post(self, uri: str, data: Optional[Dict] = None, headers: Optional[Dict] = None):
        """POST请求"""
        url = f"{self._host}{uri}"
        request_headers = headers or self.headers
        return await self.request("POST", url, json=data, headers=request_headers)

    async def pong(self, browser_context: BrowserContext) -> bool:
        """检查登录状态"""
        try:
            local_storage = await self.playwright_page.evaluate("() => window.localStorage")
            if local_storage.get("juejin_user_id"):
                return True
            
            _, cookie_dict = utils.convert_cookies(await browser_context.cookies())
            return bool(cookie_dict.get("sessionid"))
        except:
            return False

    async def update_cookies(self, browser_context: BrowserContext):
        """更新cookie"""
        cookie_str, cookie_dict = utils.convert_cookies(await browser_context.cookies())
        self.headers["Cookie"] = cookie_str
        self.cookie_dict = cookie_dict

    async def search_info_by_keyword(
        self,
        keyword: str,
        page: int = 1,
        page_size: int = 20,
        sort_type: SearchSortType = SearchSortType.GENERAL,
    ) -> Dict:
        """
        搜索文章
        Args:
            keyword: 关键词
            page: 页码
            page_size: 每页数量
            sort_type: 排序类型
        Returns:
            搜索结果
        """
        # 获取uuid和aid（从cookie中解析）
        uuid = "7551689397956937231"  # 默认值
        aid = "2608"  # 默认值
        
        try:
            # 尝试从cookie中获取uuid
            cookie_dict = self.cookie_dict
            # 从__tea_cookie_tokens_2608中解析uuid
            tea_cookie = cookie_dict.get("__tea_cookie_tokens_2608", "")
            if tea_cookie:
                import urllib.parse
                import json
                try:
                    decoded = urllib.parse.unquote(tea_cookie)
                    tokens = json.loads(decoded)
                    uuid = tokens.get("user_unique_id", uuid)
                    aid = "2608"  # aid通常固定为2608
                except Exception as parse_e:
                    utils.logger.warning(f"[JueJinClient.search_info_by_keyword] 解析cookie失败: {parse_e}")
        except Exception as e:
            utils.logger.warning(f"[JueJinClient.search_info_by_keyword] 获取uuid失败，使用默认值: {e}")
        
        # 掘金搜索API的正确格式：GET请求，参数在URL中
        # API路径：/search_api/v1/search
        # 参数：aid, uuid, spider, query, id_type, cursor, limit, search_type, sort_type, version
        params = {
            "aid": aid,
            "uuid": uuid,
            "spider": "0",
            "query": keyword,  # 使用query而不是key_word
            "id_type": "0",
            "cursor": str((page - 1) * page_size),
            "limit": str(page_size),
            "search_type": "0",
            "sort_type": sort_type.value,
            "version": "1",
        }
        utils.logger.info(f"[JueJinClient.search_info_by_keyword] 搜索参数: {params}")
        
        try:
            # 使用正确的API路径：/search_api/v1/search
            result = await self.get("/search_api/v1/search", params=params)
            utils.logger.info(f"[JueJinClient.search_info_by_keyword] API响应状态: err_no={result.get('err_no')}, err_msg={result.get('err_msg', '')}")
            utils.logger.info(f"[JueJinClient.search_info_by_keyword] 响应数据键: {list(result.keys())}")
            if result.get("data"):
                utils.logger.info(f"[JueJinClient.search_info_by_keyword] 响应数据数量: {len(result.get('data', []))}")
            return result
        except Exception as e:
            utils.logger.error(f"[JueJinClient.search_info_by_keyword] API调用失败: {e}")
            import traceback
            utils.logger.error(f"[JueJinClient.search_info_by_keyword] 错误堆栈:\n{traceback.format_exc()}")
            raise

    async def get_article_by_id(self, article_id: str) -> Dict:
        """
        获取文章详情
        Args:
            article_id: 文章ID
        Returns:
            文章详情
        """
        params = {"article_id": article_id}
        return await self.post("/content_api/v1/article/detail", data=params)

    async def get_user_articles(
        self,
        user_id: str,
        cursor: str = "0",
        limit: int = 20,
    ) -> Dict:
        """
        获取用户文章列表
        Args:
            user_id: 用户ID
            cursor: 游标
            limit: 每页数量
        Returns:
            文章列表
        """
        params = {
            "user_id": user_id,
            "cursor": cursor,
            "sort_type": 2,  # 按时间排序
            "limit": limit,
        }
        return await self.post("/content_api/v1/article/query_list", data=params)

    async def get_article_comments(
        self,
        article_id: str,
        cursor: str = "0",
        limit: int = 20,
    ) -> Dict:
        """
        获取文章评论
        Args:
            article_id: 文章ID
            cursor: 游标
            limit: 每页数量
        Returns:
            评论列表
        """
        params = {
            "item_id": article_id,
            "item_type": 2,  # 2表示文章
            "cursor": cursor,
            "limit": limit,
        }
        return await self.post("/interact_api/v1/comment/list", data=params)

