# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/media_platform/kuaishou/login.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1
#

# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。


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


class KuaishouLogin(AbstractLogin):
    def __init__(self,
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

    async def begin(self):
        """Start login xiaohongshu"""
        utils.logger.info("[KuaishouLogin.begin] Begin login kuaishou ...")
        if config.LOGIN_TYPE == "qrcode":
            await self.login_by_qrcode()
        elif config.LOGIN_TYPE == "phone":
            await self.login_by_mobile()
        elif config.LOGIN_TYPE == "cookie":
            await self.login_by_cookies()
        else:
            raise ValueError("[KuaishouLogin.begin] Invalid Login Type Currently only supported qrcode or phone or cookie ...")

    @retry(stop=stop_after_attempt(600), wait=wait_fixed(1), retry=retry_if_result(lambda value: value is False))
    async def check_login_state(self) -> bool:
        """
            Check if the current login status is successful and return True otherwise return False
            retry decorator will retry 20 times if the return value is False, and the retry interval is 1 second
            if max retry times reached, raise RetryError
        """
        current_cookie = await self.browser_context.cookies()
        _, cookie_dict = utils.convert_cookies(current_cookie)
        kuaishou_pass_token = cookie_dict.get("passToken")
        if kuaishou_pass_token:
            return True
        return False

    async def login_by_qrcode(self):
        """login kuaishou website and keep webdriver login state"""
        utils.logger.info("[KuaishouLogin.login_by_qrcode] Begin login kuaishou by qrcode ...")

        # click login button (updated to match actual HTML: <span class="btn-words">...登录</span>)
        login_button_selector = "xpath=//span[contains(@class,'btn-words') and contains(.,'登录')]"
        utils.logger.info(f"[KuaishouLogin.login_by_qrcode] 等待登录按钮出现: {login_button_selector}")
        try:
            await self.context_page.wait_for_selector(login_button_selector, timeout=10000)
            login_button_ele = self.context_page.locator(login_button_selector)
            await login_button_ele.click()
            utils.logger.info("[KuaishouLogin.login_by_qrcode] ✓ 已点击登录按钮")
            await asyncio.sleep(2)  # 等待登录框弹出
        except Exception as e:
            utils.logger.error(f"[KuaishouLogin.login_by_qrcode] 点击登录按钮失败: {e}")
            # 尝试备用选择器
            backup_selectors = [
                "xpath=//span[contains(@class,'btn-words')]",
                "xpath=//span[contains(.,'登录')]",
                "css=.btn-words"
            ]
            for backup_selector in backup_selectors:
                try:
                    utils.logger.info(f"[KuaishouLogin.login_by_qrcode] 尝试备用选择器: {backup_selector}")
                    await self.context_page.wait_for_selector(backup_selector, timeout=3000)
                    login_button_ele = self.context_page.locator(backup_selector)
                    await login_button_ele.click()
                    utils.logger.info(f"[KuaishouLogin.login_by_qrcode] ✓ 通过备用选择器点击成功: {backup_selector}")
                    await asyncio.sleep(2)
                    break
                except:
                    continue
            else:
                raise Exception("所有登录按钮选择器都失败")

        # find login qrcode
        qrcode_img_selector = "//div[@class='qrcode-img']//img"
        base64_qrcode_img = await utils.find_login_qrcode(
            self.context_page,
            selector=qrcode_img_selector
        )
        if not base64_qrcode_img:
            utils.logger.info("[KuaishouLogin.login_by_qrcode] login failed , have not found qrcode please check ....")
            sys.exit()


        # show login qrcode
        partial_show_qrcode = functools.partial(utils.show_qrcode, base64_qrcode_img)
        asyncio.get_running_loop().run_in_executor(executor=None, func=partial_show_qrcode)

        utils.logger.info(f"[KuaishouLogin.login_by_qrcode] waiting for scan code login, remaining time is 20s")
        try:
            await self.check_login_state()
        except RetryError:
            utils.logger.info("[KuaishouLogin.login_by_qrcode] Login kuaishou failed by qrcode login method ...")
            sys.exit()

        wait_redirect_seconds = 5
        utils.logger.info(f"[KuaishouLogin.login_by_qrcode] Login successful then wait for {wait_redirect_seconds} seconds redirect ...")
        await asyncio.sleep(wait_redirect_seconds)

    async def login_by_mobile(self):
        pass

    async def login_by_cookies(self):
        utils.logger.info("[KuaishouLogin.login_by_cookies] Begin login kuaishou by cookie ...")
        for key, value in utils.convert_str_cookie_to_dict(self.cookie_str).items():
            await self.browser_context.add_cookies([{
                'name': key,
                'value': value,
                'domain': ".kuaishou.com",
                'path': "/"
            }])
