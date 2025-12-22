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
from store import juejin as juejin_store
from tools import utils
from tools.cdp_browser import CDPBrowserManager
from var import crawler_type_var, source_keyword_var

from .client import JueJinClient
from .exception import DataFetchError
from .field import SearchSortType
from .help import parse_article_info_from_url, parse_creator_info_from_url
from .login import JueJinLogin


class JueJinCrawler(AbstractCrawler):
    """掘金爬虫"""

    context_page: Page
    juejin_client: JueJinClient
    browser_context: BrowserContext
    cdp_manager: Optional[CDPBrowserManager]

    def __init__(self) -> None:
        self.index_url = "https://juejin.cn"
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
                utils.logger.info("[JueJinCrawler] 使用CDP模式启动浏览器")
                self.browser_context = await self.launch_browser_with_cdp(
                    playwright,
                    playwright_proxy_format,
                    None,
                    headless=config.CDP_HEADLESS,
                )
            else:
                utils.logger.info("[JueJinCrawler] 使用标准模式启动浏览器")
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

            self.juejin_client = await self.create_juejin_client(httpx_proxy_format)
            if not await self.juejin_client.pong(browser_context=self.browser_context):
                login_obj = JueJinLogin(
                    login_type=config.LOGIN_TYPE,
                    login_phone="",
                    browser_context=self.browser_context,
                    context_page=self.context_page,
                    cookie_str=config.COOKIES,
                )
                await login_obj.begin()
                await self.juejin_client.update_cookies(browser_context=self.browser_context)

            crawler_type_var.set(config.CRAWLER_TYPE)
            
            # 检查必要的配置
            if config.CRAWLER_TYPE == "search":
                if not config.KEYWORDS or not config.KEYWORDS.strip():
                    utils.logger.error("[JueJinCrawler.start] 搜索模式需要配置关键词，但KEYWORDS为空")
                    raise ValueError("搜索模式需要配置关键词，请设置KEYWORDS")
                utils.logger.info(f"[JueJinCrawler.start] 开始搜索模式，关键词: {config.KEYWORDS}")
                await self.search()
            elif config.CRAWLER_TYPE == "detail":
                specified_urls = getattr(config, "JUEJIN_SPECIFIED_ARTICLE_URL_LIST", [])
                if not specified_urls:
                    utils.logger.error("[JueJinCrawler.start] 详情模式需要配置文章URL列表，但JUEJIN_SPECIFIED_ARTICLE_URL_LIST为空")
                    raise ValueError("详情模式需要配置文章URL列表，请设置JUEJIN_SPECIFIED_ARTICLE_URL_LIST")
                utils.logger.info(f"[JueJinCrawler.start] 开始详情模式，文章数量: {len(specified_urls)}")
                await self.get_specified_articles()
            elif config.CRAWLER_TYPE == "creator":
                creator_ids = getattr(config, "JUEJIN_CREATOR_ID_LIST", [])
                if not creator_ids:
                    utils.logger.error("[JueJinCrawler.start] 创作者模式需要配置创作者ID列表，但JUEJIN_CREATOR_ID_LIST为空")
                    raise ValueError("创作者模式需要配置创作者ID列表，请设置JUEJIN_CREATOR_ID_LIST")
                utils.logger.info(f"[JueJinCrawler.start] 开始创作者模式，创作者数量: {len(creator_ids)}")
                await self.get_creators_and_articles()
            else:
                utils.logger.warning(f"[JueJinCrawler.start] 未知的爬取类型: {config.CRAWLER_TYPE}")

            utils.logger.info("[JueJinCrawler.start] JueJin Crawler finished ...")

    async def search(self) -> None:
        """搜索文章"""
        utils.logger.info("[JueJinCrawler.search] Begin search juejin keywords")
        
        # 检查关键词配置
        if not config.KEYWORDS or not config.KEYWORDS.strip():
            utils.logger.error("[JueJinCrawler.search] KEYWORDS为空，无法进行搜索")
            raise ValueError("KEYWORDS配置为空，请设置搜索关键词")
        
        limit_count = 20
        if config.CRAWLER_MAX_NOTES_COUNT < limit_count:
            config.CRAWLER_MAX_NOTES_COUNT = limit_count
        
        start_page = config.START_PAGE
        keywords_list = [k.strip() for k in config.KEYWORDS.split(",") if k.strip()]
        if not keywords_list:
            utils.logger.error("[JueJinCrawler.search] 关键词列表为空（可能是空白字符）")
            raise ValueError("关键词列表为空，请检查KEYWORDS配置")
        
        utils.logger.info(f"[JueJinCrawler.search] 关键词列表: {keywords_list}")
        
        for keyword in keywords_list:
            source_keyword_var.set(keyword)
            utils.logger.info(f"[JueJinCrawler.search] Current keyword: {keyword}")
            article_list: List[str] = []
            page = 1
            
            while (page - start_page + 1) * limit_count <= config.CRAWLER_MAX_NOTES_COUNT:
                if page < start_page:
                    utils.logger.info(f"[JueJinCrawler.search] Skip {page}")
                    page += 1
                    continue
                
                try:
                    utils.logger.info(f"[JueJinCrawler.search] search juejin keyword: {keyword}, page: {page}")
                    search_res = await self.juejin_client.search_info_by_keyword(
                        keyword=keyword,
                        page=page,
                        page_size=limit_count,
                        sort_type=SearchSortType.GENERAL,
                    )
                    
                    if search_res.get("err_no") != 0:
                        utils.logger.error(f"[JueJinCrawler.search] 搜索失败: {search_res.get('err_msg', '未知错误')}")
                        break
                    
                    data = search_res.get("data", [])
                    if not data or len(data) == 0:
                        utils.logger.info(f"[JueJinCrawler.search] search juejin keyword: {keyword}, page: {page} is empty")
                        break
                    
                    for idx, item in enumerate(data):
                        # 掘金搜索API返回的数据结构是嵌套的：
                        # item = {
                        #     'result_type': 2,
                        #     'result_model': {
                        #         'article_id': 'xxx',
                        #         'article_info': {...},
                        #         'author_user_info': {...},
                        #         ...
                        #     }
                        # }
                        result_model = item.get("result_model", {})
                        if not result_model:
                            utils.logger.warning(f"[JueJinCrawler.search] 文章项缺少result_model: {item}")
                            continue
                        
                        # 从result_model中获取article_id
                        article_id = result_model.get("article_id", "") or result_model.get("article_info", {}).get("article_id", "")
                        if article_id:
                            article_list.append(article_id)
                            utils.logger.info(f"[JueJinCrawler.search] 处理第 {idx+1}/{len(data)} 篇文章，ID: {article_id}, 标题: {result_model.get('article_info', {}).get('title', '')[:50]}")
                            try:
                                # 传递整个result_model作为article_item（包含article_info、author_user_info等完整信息）
                                await juejin_store.update_juejin_article(article_item=result_model)
                                utils.logger.info(f"[JueJinCrawler.search] ✓ 文章 {article_id} 已保存到数据列表")
                            except Exception as e:
                                utils.logger.error(f"[JueJinCrawler.search] ✗ 保存文章 {article_id} 失败: {e}")
                                import traceback
                                utils.logger.error(f"[JueJinCrawler.search] 错误堆栈:\n{traceback.format_exc()}")
                        else:
                            utils.logger.warning(f"[JueJinCrawler.search] 文章项缺少article_id，result_model keys: {list(result_model.keys())}")
                    
                    page += 1
                    await asyncio.sleep(config.CRAWLER_MAX_SLEEP_SEC)
                except DataFetchError as e:
                    utils.logger.error(f"[JueJinCrawler.search] search juejin keyword: {keyword} failed: {e}")
                    import traceback
                    utils.logger.error(f"[JueJinCrawler.search] 错误堆栈:\n{traceback.format_exc()}")
                    break
                except Exception as e:
                    utils.logger.error(f"[JueJinCrawler.search] 未预期的错误: {type(e).__name__}: {e}")
                    import traceback
                    utils.logger.error(f"[JueJinCrawler.search] 错误堆栈:\n{traceback.format_exc()}")
                    break
            
            utils.logger.info(f"[JueJinCrawler.search] keyword:{keyword}, article_list:{article_list}")
            await self.batch_get_article_comments(article_list)

    async def get_specified_articles(self):
        """获取指定文章详情"""
        utils.logger.info("[JueJinCrawler.get_specified_articles] Parsing article URLs...")
        article_id_list = []
        
        # 从配置中获取文章URL列表（需要添加配置支持）
        specified_urls = getattr(config, "JUEJIN_SPECIFIED_ARTICLE_URL_LIST", [])
        for article_url in specified_urls:
            try:
                article_info = parse_article_info_from_url(article_url)
                article_id_list.append(article_info.article_id)
                utils.logger.info(f"[JueJinCrawler.get_specified_articles] Parsed article ID: {article_info.article_id}")
            except ValueError as e:
                utils.logger.error(f"[JueJinCrawler.get_specified_articles] Failed to parse article URL: {e}")
                continue
        
        semaphore = asyncio.Semaphore(config.MAX_CONCURRENCY_NUM)
        task_list = [self.get_article_detail(article_id=article_id, semaphore=semaphore) for article_id in article_id_list]
        article_details = await asyncio.gather(*task_list)
        
        for article_detail in article_details:
            if article_detail is not None:
                await juejin_store.update_juejin_article(article_item=article_detail)
        
        await self.batch_get_article_comments(article_id_list)

    async def get_article_detail(self, article_id: str, semaphore: asyncio.Semaphore) -> Any:
        """获取文章详情"""
        async with semaphore:
            try:
                result = await self.juejin_client.get_article_by_id(article_id)
                if result.get("err_no") == 0:
                    await asyncio.sleep(config.CRAWLER_MAX_SLEEP_SEC)
                    return result.get("data", {})
                else:
                    utils.logger.error(f"[JueJinCrawler.get_article_detail] Get article detail error: {result.get('err_msg')}")
                    return None
            except DataFetchError as ex:
                utils.logger.error(f"[JueJinCrawler.get_article_detail] Get article detail error: {ex}")
                return None

    async def batch_get_article_comments(self, article_list: List[str]) -> None:
        """批量获取文章评论"""
        if not config.ENABLE_GET_COMMENTS:
            utils.logger.info(f"[JueJinCrawler.batch_get_article_comments] 评论爬取模式未启用")
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
                cursor = "0"
                all_comments = []
                
                while len(all_comments) < config.CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES:
                    comments_res = await self.juejin_client.get_article_comments(
                        article_id=article_id,
                        cursor=cursor,
                        limit=20,
                    )
                    
                    if comments_res.get("err_no") != 0:
                        break
                    
                    comments = comments_res.get("data", [])
                    if not comments or len(comments) == 0:
                        break
                    
                    for comment in comments:
                        comment_item = {
                            "comment_id": comment.get("comment_id", ""),
                            "article_id": article_id,
                            "content": comment.get("comment_info", {}).get("comment_content", ""),
                            "user_id": comment.get("user_info", {}).get("user_id", ""),
                            "nickname": comment.get("user_info", {}).get("user_name", ""),
                            "avatar": comment.get("user_info", {}).get("avatar_large", ""),
                            "like_count": comment.get("comment_info", {}).get("digg_count", 0),
                            "create_time": comment.get("comment_info", {}).get("ctime", 0),
                        }
                        all_comments.append(comment_item)
                    
                    cursor = comments_res.get("cursor", "0")
                    if cursor == "0":
                        break
                    
                    await asyncio.sleep(crawl_interval)
                
                await juejin_store.batch_update_juejin_comments(article_id, all_comments)
                utils.logger.info(f"[JueJinCrawler.get_comments] article_id: {article_id} comments have all been obtained")
            except DataFetchError as e:
                utils.logger.error(f"[JueJinCrawler.get_comments] article_id: {article_id} get comments failed, error: {e}")

    async def get_creators_and_articles(self) -> None:
        """获取创作者及其文章"""
        utils.logger.info("[JueJinCrawler.get_creators_and_articles] Begin get juejin creators")
        
        # 从配置中获取创作者ID列表（需要添加配置支持）
        creator_urls = getattr(config, "JUEJIN_CREATOR_ID_LIST", [])
        for creator_url in creator_urls:
            try:
                creator_info_parsed = parse_creator_info_from_url(creator_url)
                user_id = creator_info_parsed.user_id
                utils.logger.info(f"[JueJinCrawler.get_creators_and_articles] Parsed user_id: {user_id}")
            except ValueError as e:
                utils.logger.error(f"[JueJinCrawler.get_creators_and_articles] Failed to parse creator URL: {e}")
                continue

            # 获取用户文章列表
            cursor = "0"
            all_articles = []
            while True:
                try:
                    articles_res = await self.juejin_client.get_user_articles(
                        user_id=user_id,
                        cursor=cursor,
                        limit=20,
                    )
                    
                    if articles_res.get("err_no") != 0:
                        break
                    
                    articles = articles_res.get("data", [])
                    if not articles or len(articles) == 0:
                        break
                    
                    for article in articles:
                        await juejin_store.update_juejin_article(article_item=article)
                        all_articles.append(article.get("article_id", ""))
                    
                    cursor = articles_res.get("cursor", "0")
                    if cursor == "0":
                        break
                    
                    await asyncio.sleep(config.CRAWLER_MAX_SLEEP_SEC)
                except DataFetchError as e:
                    utils.logger.error(f"[JueJinCrawler.get_creators_and_articles] Failed to get user articles: {e}")
                    break
            
            await self.batch_get_article_comments(all_articles)

    async def create_juejin_client(self, httpx_proxy: Optional[str]) -> JueJinClient:
        """创建掘金客户端"""
        cookie_str, cookie_dict = utils.convert_cookies(await self.browser_context.cookies())
        juejin_client = JueJinClient(
            proxy=httpx_proxy,
            headers={
                "User-Agent": await self.context_page.evaluate("() => navigator.userAgent"),
                "Cookie": cookie_str,
                "Host": "api.juejin.cn",
                "Origin": "https://juejin.cn",
                "Referer": "https://juejin.cn/",
                "Content-Type": "application/json",
            },
            playwright_page=self.context_page,
            cookie_dict=cookie_dict,
            proxy_ip_pool=self.ip_proxy_pool,
        )
        return juejin_client

    async def launch_browser(
        self,
        chromium: BrowserType,
        playwright_proxy: Optional[Dict],
        user_agent: Optional[str],
        headless: bool = True,
    ) -> BrowserContext:
        """启动浏览器"""
        utils.logger.info("[JueJinCrawler.launch_browser] Begin create browser context ...")
        if config.SAVE_LOGIN_STATE:
            # feat issue #14
            # we will save login state to avoid login every time
            user_data_dir = os.path.join(os.getcwd(), "browser_data", config.USER_DATA_DIR % config.PLATFORM)
            # 如果目录存在但可能被锁定，先尝试清理锁文件
            if os.path.exists(user_data_dir):
                try:
                    # 检查是否有锁文件
                    lock_files = [
                        os.path.join(user_data_dir, "SingletonLock"),
                        os.path.join(user_data_dir, "Default", "SingletonLock"),
                    ]
                    for lock_file in lock_files:
                        if os.path.exists(lock_file):
                            utils.logger.warning(f"[JueJinCrawler.launch_browser] 发现锁文件，尝试删除: {lock_file}")
                            try:
                                os.remove(lock_file)
                            except Exception as e:
                                utils.logger.warning(f"[JueJinCrawler.launch_browser] 删除锁文件失败: {e}")
                except Exception as e:
                    utils.logger.warning(f"[JueJinCrawler.launch_browser] 检查锁文件时出错: {e}")
            
            try:
                browser_context = await chromium.launch_persistent_context(
                    user_data_dir=user_data_dir,
                    accept_downloads=True,
                    headless=headless,
                    proxy=playwright_proxy,  # type: ignore
                    viewport={
                        "width": 1920,
                        "height": 1080
                    },
                    user_agent=user_agent,
                    channel="chrome",  # 使用系统的Chrome稳定版
                )
                return browser_context
            except Exception as e:
                utils.logger.error(f"[JueJinCrawler.launch_browser] 启动持久化上下文失败: {e}")
                # 如果持久化上下文启动失败，尝试清理目录后重试
                utils.logger.info("[JueJinCrawler.launch_browser] 尝试清理浏览器数据目录后重试...")
                try:
                    import shutil
                    if os.path.exists(user_data_dir):
                        shutil.rmtree(user_data_dir)
                    await asyncio.sleep(1)
                    browser_context = await chromium.launch_persistent_context(
                        user_data_dir=user_data_dir,
                        accept_downloads=True,
                        headless=headless,
                        proxy=playwright_proxy,  # type: ignore
                        viewport={
                            "width": 1920,
                            "height": 1080
                        },
                        user_agent=user_agent,
                        channel="chrome",
                    )
                    return browser_context
                except Exception as retry_e:
                    utils.logger.error(f"[JueJinCrawler.launch_browser] 重试启动持久化上下文也失败: {retry_e}")
                    # 如果还是失败，使用非持久化模式
                    utils.logger.info("[JueJinCrawler.launch_browser] 回退到非持久化模式...")
                    browser = await chromium.launch(headless=headless, proxy=playwright_proxy, channel="chrome")  # type: ignore
                    browser_context = await browser.new_context(viewport={"width": 1920, "height": 1080}, user_agent=user_agent)
                    return browser_context
        else:
            browser = await chromium.launch(headless=headless, proxy=playwright_proxy, channel="chrome")  # type: ignore
            browser_context = await browser.new_context(viewport={"width": 1920, "height": 1080}, user_agent=user_agent)
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
            utils.logger.info(f"[JueJinCrawler] CDP浏览器信息: {browser_info}")
            return browser_context
        except Exception as e:
            utils.logger.error(f"[JueJinCrawler] CDP模式启动失败，回退到标准模式: {e}")
            chromium = playwright.chromium
            return await self.launch_browser(chromium, playwright_proxy, user_agent, headless)

    async def close(self) -> None:
        """关闭浏览器上下文"""
        if self.cdp_manager:
            await self.cdp_manager.cleanup()
            self.cdp_manager = None
        else:
            await self.browser_context.close()
        utils.logger.info("[JueJinCrawler.close] Browser context closed ...")

