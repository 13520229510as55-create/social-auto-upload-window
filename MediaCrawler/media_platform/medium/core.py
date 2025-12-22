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
import os
from asyncio import Task
from typing import Any, Dict, List, Optional

from playwright.async_api import (
    BrowserContext,
    BrowserType,
    Page,
    Playwright,
    async_playwright,
)

import config
from base.base_crawler import AbstractCrawler
from proxy.proxy_ip_pool import IpInfoModel, create_ip_pool
from store import medium as medium_store
from tools import utils
from tools.cdp_browser import CDPBrowserManager
from var import crawler_type_var, source_keyword_var

from .client import MediumClient
from .exception import DataFetchError
from .field import SearchSortType
from .help import parse_article_info_from_url, parse_creator_info_from_url
from .login import MediumLogin


class MediumCrawler(AbstractCrawler):
    """Medium爬虫"""

    context_page: Page
    medium_client: MediumClient
    browser_context: BrowserContext
    cdp_manager: Optional[CDPBrowserManager]

    def __init__(self) -> None:
        self.index_url = "https://medium.com"
        self.cdp_manager = None
        self.ip_proxy_pool = None

    async def start(self) -> None:
        """启动爬虫"""
        playwright_proxy_format, httpx_proxy_format = None, None
        if config.ENABLE_IP_PROXY:
            self.ip_proxy_pool = await create_ip_pool(config.IP_PROXY_POOL_COUNT, enable_validate_ip=True)
            ip_proxy_info: IpInfoModel = await self.ip_proxy_pool.get_proxy()
            playwright_proxy_format, httpx_proxy_format = utils.format_proxy_info(ip_proxy_info)

        async with async_playwright() as playwright:
            if config.ENABLE_CDP_MODE:
                utils.logger.info("[MediumCrawler] 使用CDP模式启动浏览器")
                self.browser_context = await self.launch_browser_with_cdp(
                    playwright,
                    playwright_proxy_format,
                    None,
                    headless=config.CDP_HEADLESS,
                )
            else:
                utils.logger.info("[MediumCrawler] 使用标准模式启动浏览器")
                chromium = playwright.chromium
                self.browser_context = await self.launch_browser(
                    chromium,
                    playwright_proxy_format,
                    user_agent=None,
                    headless=config.HEADLESS,
                )
                await self.browser_context.add_init_script(path="libs/stealth.min.js")

            self.context_page = await self.browser_context.new_page()
            await self.context_page.goto(self.index_url, wait_until='load', timeout=60000)
            await asyncio.sleep(2)

            self.medium_client = await self.create_medium_client(httpx_proxy_format)
            if not await self.medium_client.pong(browser_context=self.browser_context):
                login_obj = MediumLogin(
                    login_type=config.LOGIN_TYPE,
                    login_phone="",
                    browser_context=self.browser_context,
                    context_page=self.context_page,
                    cookie_str=config.COOKIES,
                )
                await login_obj.begin()
                await self.medium_client.update_cookies(browser_context=self.browser_context)

            crawler_type_var.set(config.CRAWLER_TYPE)
            if config.CRAWLER_TYPE == "search":
                await self.search()
            elif config.CRAWLER_TYPE == "detail":
                await self.get_specified_articles()
            elif config.CRAWLER_TYPE == "creator":
                await self.get_creators_and_articles()

            utils.logger.info("[MediumCrawler.start] Medium Crawler finished ...")

    async def search(self) -> None:
        """搜索文章"""
        utils.logger.info("[MediumCrawler.search] Begin search medium keywords")
        limit_count = 20
        if config.CRAWLER_MAX_NOTES_COUNT < limit_count:
            config.CRAWLER_MAX_NOTES_COUNT = limit_count
        
        start_page = config.START_PAGE
        for keyword in config.KEYWORDS.split(","):
            source_keyword_var.set(keyword)
            utils.logger.info(f"[MediumCrawler.search] Current keyword: {keyword}")
            article_list: List[str] = []
            page = 1
            
            while (page - start_page + 1) * limit_count <= config.CRAWLER_MAX_NOTES_COUNT:
                if page < start_page:
                    utils.logger.info(f"[MediumCrawler.search] Skip {page}")
                    page += 1
                    continue
                
                try:
                    utils.logger.info(f"[MediumCrawler.search] search medium keyword: {keyword}, page: {page}")
                    # Medium的搜索可能需要通过页面爬取，这里使用简化的API调用
                    search_res = await self.medium_client.search_articles(
                        query=keyword,
                        page=page,
                        sort=SearchSortType.RELEVANCE,
                    )
                    
                    # 解析搜索结果（需要根据实际API响应格式调整）
                    articles = search_res.get("posts", []) or search_res.get("articles", []) or []
                    if not articles or len(articles) == 0:
                        utils.logger.info(f"[MediumCrawler.search] search medium keyword: {keyword}, page: {page} is empty")
                        break
                    
                    for item in articles:
                        article_id = item.get("id", "") or item.get("article_id", "")
                        if article_id:
                            article_list.append(article_id)
                            await medium_store.update_medium_article(article_item=item)
                    
                    page += 1
                    await asyncio.sleep(config.CRAWLER_MAX_SLEEP_SEC)
                except DataFetchError as e:
                    utils.logger.error(f"[MediumCrawler.search] search medium keyword: {keyword} failed: {e}")
                    break
            
            utils.logger.info(f"[MediumCrawler.search] keyword:{keyword}, article_list:{article_list}")
            await self.batch_get_article_comments(article_list)

    async def get_specified_articles(self):
        """获取指定文章详情"""
        utils.logger.info("[MediumCrawler.get_specified_articles] Parsing article URLs...")
        article_id_list = []
        
        # 从配置中获取文章URL列表（需要添加配置支持）
        specified_urls = getattr(config, "MEDIUM_SPECIFIED_ARTICLE_URL_LIST", [])
        for article_url in specified_urls:
            try:
                article_info = parse_article_info_from_url(article_url)
                article_id_list.append(article_info.article_id)
                utils.logger.info(f"[MediumCrawler.get_specified_articles] Parsed article ID: {article_info.article_id}")
            except ValueError as e:
                utils.logger.error(f"[MediumCrawler.get_specified_articles] Failed to parse article URL: {e}")
                continue
        
        semaphore = asyncio.Semaphore(config.MAX_CONCURRENCY_NUM)
        task_list = [self.get_article_detail(article_id=article_id, semaphore=semaphore) for article_id in article_id_list]
        article_details = await asyncio.gather(*task_list)
        
        for article_detail in article_details:
            if article_detail is not None:
                await medium_store.update_medium_article(article_item=article_detail)
        
        await self.batch_get_article_comments(article_id_list)

    async def get_article_detail(self, article_id: str, semaphore: asyncio.Semaphore) -> Any:
        """获取文章详情"""
        async with semaphore:
            try:
                result = await self.medium_client.get_article_by_id(article_id)
                await asyncio.sleep(config.CRAWLER_MAX_SLEEP_SEC)
                return result
            except DataFetchError as ex:
                utils.logger.error(f"[MediumCrawler.get_article_detail] Get article detail error: {ex}")
                return None

    async def batch_get_article_comments(self, article_list: List[str]) -> None:
        """批量获取文章评论"""
        if not config.ENABLE_GET_COMMENTS:
            utils.logger.info(f"[MediumCrawler.batch_get_article_comments] 评论爬取模式未启用")
            return

        task_list: List[Task] = []
        semaphore = asyncio.Semaphore(config.MAX_CONCURRENCY_NUM)
        for article_id in article_list:
            task = asyncio.create_task(self.get_comments(article_id, semaphore), name=article_id)
            task_list.append(task)
        
        if len(task_list) > 0:
            await asyncio.wait(task_list)

    async def get_comments(self, article_id: str, semaphore: asyncio.Semaphore) -> None:
        """获取文章评论"""
        async with semaphore:
            try:
                crawl_interval = config.CRAWLER_MAX_SLEEP_SEC
                page = 1
                all_comments = []
                
                while len(all_comments) < config.CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES:
                    comments_res = await self.medium_client.get_article_comments(
                        article_id=article_id,
                        page=page,
                    )
                    
                    comments = comments_res.get("comments", []) or comments_res.get("data", []) or []
                    if not comments or len(comments) == 0:
                        break
                    
                    for comment in comments:
                        comment_item = {
                            "comment_id": comment.get("id", ""),
                            "article_id": article_id,
                            "content": comment.get("content", ""),
                            "user_id": comment.get("userId", ""),
                            "nickname": comment.get("author", {}).get("name", ""),
                            "avatar": comment.get("author", {}).get("image", ""),
                            "like_count": comment.get("likes", 0),
                            "create_time": comment.get("createdAt", 0),
                        }
                        all_comments.append(comment_item)
                    
                    page += 1
                    await asyncio.sleep(crawl_interval)
                
                await medium_store.batch_update_medium_comments(article_id, all_comments)
                utils.logger.info(f"[MediumCrawler.get_comments] article_id: {article_id} comments have all been obtained")
            except DataFetchError as e:
                utils.logger.error(f"[MediumCrawler.get_comments] article_id: {article_id} get comments failed, error: {e}")

    async def get_creators_and_articles(self) -> None:
        """获取创作者及其文章"""
        utils.logger.info("[MediumCrawler.get_creators_and_articles] Begin get medium creators")
        
        # 从配置中获取创作者ID列表（需要添加配置支持）
        creator_urls = getattr(config, "MEDIUM_CREATOR_ID_LIST", [])
        for creator_url in creator_urls:
            try:
                creator_info_parsed = parse_creator_info_from_url(creator_url)
                user_id = creator_info_parsed.user_id
                utils.logger.info(f"[MediumCrawler.get_creators_and_articles] Parsed user_id: {user_id}")
            except ValueError as e:
                utils.logger.error(f"[MediumCrawler.get_creators_and_articles] Failed to parse creator URL: {e}")
                continue

            # 获取用户文章列表
            page = 1
            all_articles = []
            while True:
                try:
                    articles_res = await self.medium_client.get_user_articles(
                        user_id=user_id,
                        page=page,
                    )
                    
                    articles = articles_res.get("posts", []) or articles_res.get("articles", []) or []
                    if not articles or len(articles) == 0:
                        break
                    
                    for article in articles:
                        await medium_store.update_medium_article(article_item=article)
                        article_id = article.get("id", "") or article.get("article_id", "")
                        if article_id:
                            all_articles.append(article_id)
                    
                    page += 1
                    await asyncio.sleep(config.CRAWLER_MAX_SLEEP_SEC)
                except DataFetchError as e:
                    utils.logger.error(f"[MediumCrawler.get_creators_and_articles] Failed to get user articles: {e}")
                    break
            
            await self.batch_get_article_comments(all_articles)

    async def create_medium_client(self, httpx_proxy: Optional[str]) -> MediumClient:
        """创建Medium客户端"""
        cookie_str, cookie_dict = utils.convert_cookies(await self.browser_context.cookies())
        medium_client = MediumClient(
            proxy=httpx_proxy,
            headers={
                "User-Agent": await self.context_page.evaluate("() => navigator.userAgent"),
                "Cookie": cookie_str,
                "Host": "medium.com",
                "Origin": "https://medium.com",
                "Referer": "https://medium.com/",
                "Accept": "application/json",
            },
            playwright_page=self.context_page,
            cookie_dict=cookie_dict,
            proxy_ip_pool=self.ip_proxy_pool,
        )
        return medium_client

    async def launch_browser(
        self,
        chromium: BrowserType,
        playwright_proxy: Optional[Dict],
        user_agent: Optional[str],
        headless: bool = True,
    ) -> BrowserContext:
        """启动浏览器"""
        if config.SAVE_LOGIN_STATE:
            user_data_dir = os.path.join(os.getcwd(), "browser_data", config.USER_DATA_DIR % config.PLATFORM)
            browser_context = await chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                accept_downloads=True,
                headless=headless,
                proxy=playwright_proxy,
                viewport={"width": 1920, "height": 1080},
                user_agent=user_agent,
            )
            return browser_context
        else:
            browser = await chromium.launch(headless=headless, proxy=playwright_proxy)
            browser_context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent=user_agent
            )
            return browser_context

    async def launch_browser_with_cdp(
        self,
        playwright: Playwright,
        playwright_proxy: Optional[Dict],
        user_agent: Optional[str],
        headless: bool = True,
    ) -> BrowserContext:
        """使用CDP模式启动浏览器"""
        try:
            self.cdp_manager = CDPBrowserManager()
            browser_context = await self.cdp_manager.launch_and_connect(
                playwright=playwright,
                playwright_proxy=playwright_proxy,
                user_agent=user_agent,
                headless=headless,
            )
            await self.cdp_manager.add_stealth_script()
            browser_info = await self.cdp_manager.get_browser_info()
            utils.logger.info(f"[MediumCrawler] CDP浏览器信息: {browser_info}")
            return browser_context
        except Exception as e:
            utils.logger.error(f"[MediumCrawler] CDP模式启动失败，回退到标准模式: {e}")
            chromium = playwright.chromium
            return await self.launch_browser(chromium, playwright_proxy, user_agent, headless)

    async def close(self) -> None:
        """关闭浏览器上下文"""
        if self.cdp_manager:
            await self.cdp_manager.cleanup()
            self.cdp_manager = None
        else:
            await self.browser_context.close()
        utils.logger.info("[MediumCrawler.close] Browser context closed ...")

