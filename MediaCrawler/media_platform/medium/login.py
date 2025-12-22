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
import functools
import sys
from typing import Optional

from playwright.async_api import BrowserContext, Page
from tenacity import (RetryError, retry, retry_if_result, stop_after_attempt,
                      wait_fixed)

import config
from base.base_crawler import AbstractLogin
from tools import utils


class MediumLogin(AbstractLogin):
    """Medium登录类"""

    def __init__(
        self,
        login_type: str,
        browser_context: BrowserContext,
        context_page: Page,
        login_phone: Optional[str] = "",
        cookie_str: str = ""
    ):
        config.LOGIN_TYPE = login_type
        self.browser_context = browser_context
        self.context_page = context_page
        self.login_phone = login_phone
        self.cookie_str = cookie_str

    @retry(stop=stop_after_attempt(600), wait=wait_fixed(1), retry=retry_if_result(lambda value: value is False))
    async def check_login_state(self) -> bool:
        """检查登录状态"""
        current_cookie = await self.browser_context.cookies()
        _, cookie_dict = utils.convert_cookies(current_cookie)
        # Medium使用sid判断登录状态
        if cookie_dict.get("sid"):
            return True
        return False

    async def begin(self):
        """开始登录"""
        utils.logger.info("[MediumLogin.begin] Begin login medium ...")
        if config.LOGIN_TYPE == "qrcode":
            await self.login_by_qrcode()
        elif config.LOGIN_TYPE == "phone":
            await self.login_by_mobile()
        elif config.LOGIN_TYPE == "cookie":
            await self.login_by_cookies()
        else:
            raise ValueError("[MediumLogin.begin] Invalid Login Type Currently only supported qrcode or phone or cookie ...")

    async def login_by_mobile(self):
        """手机号登录（待实现）"""
        utils.logger.info("[MediumLogin.login_by_mobile] 手机号登录功能待实现")

    async def login_by_qrcode(self):
        """二维码登录"""
        utils.logger.info("[MediumLogin.login_by_qrcode] Begin login medium by qrcode ...")
        qrcode_img_selector = "xpath=//img[contains(@class,'qrcode')]"
        # 查找登录二维码
        base64_qrcode_img = await utils.find_login_qrcode(
            self.context_page,
            selector=qrcode_img_selector
        )
        if not base64_qrcode_img:
            utils.logger.info("[MediumLogin.login_by_qrcode] login failed, have not found qrcode please check ....")
            sys.exit()

        # 显示登录二维码
        partial_show_qrcode = functools.partial(utils.show_qrcode, base64_qrcode_img)
        asyncio.get_running_loop().run_in_executor(executor=None, func=partial_show_qrcode)

        utils.logger.info(f"[MediumLogin.login_by_qrcode] waiting for scan code login, remaining time is 120s")
        try:
            await self.check_login_state()
        except RetryError:
            utils.logger.info("[MediumLogin.login_by_qrcode] Login medium failed by qrcode login method ...")
            sys.exit()

        wait_redirect_seconds = 5
        utils.logger.info(f"[MediumLogin.login_by_qrcode] Login successful then wait for {wait_redirect_seconds} seconds redirect ...")
        await asyncio.sleep(wait_redirect_seconds)

    async def login_by_cookies(self):
        """Cookie登录"""
        utils.logger.info("[MediumLogin.login_by_cookies] Begin login medium by cookie ...")
        for key, value in utils.convert_str_cookie_to_dict(self.cookie_str).items():
            await self.browser_context.add_cookies([{
                'name': key,
                'value': value,
                'domain': ".medium.com",
                'path': "/"
            }])
        # 刷新页面让cookie生效
        await self.context_page.reload(wait_until='load')
        await asyncio.sleep(2)

