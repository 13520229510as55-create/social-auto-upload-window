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


class MediumClient(AbstractApiClient, ProxyRefreshMixin):
    """Medium客户端"""

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
        self._host = "https://medium.com"
        self._api_host = "https://medium.com/_/api"
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
                # Medium API返回的是JSONP格式，需要解析
                text = response.text
                if text.startswith("])}while(1);</x>"):
                    # 移除JSONP包装
                    text = text.replace("])}while(1);</x>", "")
                return eval(text) if text.startswith("{") else response.json()
            except Exception as e:
                raise DataFetchError(f"解析响应失败: {e}, 响应: {response.text[:200]}")

    async def get(self, uri: str, params: Optional[Dict] = None, headers: Optional[Dict] = None):
        """GET请求"""
        url = f"{self._api_host}{uri}" if uri.startswith("/") else f"{self._api_host}/{uri}"
        request_headers = headers or self.headers
        if params:
            from urllib.parse import urlencode
            url = f"{url}?{urlencode(params)}"
        return await self.request("GET", url, headers=request_headers)

    async def post(self, uri: str, data: Optional[Dict] = None, headers: Optional[Dict] = None):
        """POST请求"""
        url = f"{self._api_host}{uri}" if uri.startswith("/") else f"{self._api_host}/{uri}"
        request_headers = headers or self.headers
        return await self.request("POST", url, json=data, headers=request_headers)

    async def pong(self, browser_context: BrowserContext) -> bool:
        """检查登录状态"""
        try:
            _, cookie_dict = utils.convert_cookies(await browser_context.cookies())
            # Medium使用sid判断登录状态
            return bool(cookie_dict.get("sid"))
        except:
            return False

    async def update_cookies(self, browser_context: BrowserContext):
        """更新cookie"""
        cookie_str, cookie_dict = utils.convert_cookies(await browser_context.cookies())
        self.headers["Cookie"] = cookie_str
        self.cookie_dict = cookie_dict

    async def search_articles(
        self,
        query: str,
        page: int = 1,
        sort: SearchSortType = SearchSortType.RELEVANCE,
    ) -> Dict:
        """
        搜索文章
        Args:
            query: 搜索关键词
            page: 页码
            sort: 排序类型
        Returns:
            搜索结果
        """
        # Medium的搜索API比较复杂，这里使用简化的实现
        # 实际使用时可能需要通过页面爬取
        params = {
            "q": query,
            "page": page,
            "sort": sort.value,
        }
        # 注意：Medium的API可能需要特殊处理
        return await self.get("/search", params=params)

    async def get_article_by_id(self, article_id: str) -> Dict:
        """
        获取文章详情
        Args:
            article_id: 文章ID
        Returns:
            文章详情
        """
        # Medium的文章详情API
        return await self.get(f"/posts/{article_id}")

    async def get_user_articles(
        self,
        user_id: str,
        page: int = 1,
    ) -> Dict:
        """
        获取用户文章列表
        Args:
            user_id: 用户ID（@username格式）
            page: 页码
        Returns:
            文章列表
        """
        return await self.get(f"/users/{user_id}/posts", params={"page": page})

    async def get_article_comments(
        self,
        article_id: str,
        page: int = 1,
    ) -> Dict:
        """
        获取文章评论
        Args:
            article_id: 文章ID
            page: 页码
        Returns:
            评论列表
        """
        return await self.get(f"/posts/{article_id}/comments", params={"page": page})

