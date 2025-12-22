# -*- coding: utf-8 -*-
"""
登录服务模块
处理二维码登录、cookie管理等
"""

import asyncio
import base64
import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime, timedelta

from playwright.async_api import BrowserContext, Page, async_playwright

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 尝试导入依赖，如果失败则使用mock
try:
    import config
    from tools.crawler_util import find_login_qrcode
    # 移除 utils 导入，因为它会导入 slider_util，而 slider_util 需要 cv2（二维码登录不需要）
    # from tools import utils
    from tools.cdp_browser import CDPBrowserManager
    DEPENDENCIES_AVAILABLE = True
    print(f"[login_service] ✓ 所有依赖导入成功，DEPENDENCIES_AVAILABLE = True")
except ImportError as e:
    print(f"[login_service] 警告: 部分依赖未安装 ({e})，登录功能将受限")
    print(f"[login_service] 导入失败的模块: {type(e).__name__}: {e}")
    import traceback
    print(f"[login_service] 导入错误堆栈:\n{traceback.format_exc()}")
    DEPENDENCIES_AVAILABLE = False
    # 创建简单的mock函数
    async def find_login_qrcode_mock(page, selector):
        return ""
    find_login_qrcode = find_login_qrcode_mock
    CDPBrowserManager = None

# 存储登录会话
login_sessions: Dict[str, Dict] = {}

# Cookie存储目录
COOKIE_DIR = project_root / "cookies"


class LoginService:
    """登录服务类"""
    
    def __init__(self):
        """初始化登录服务"""
        self.cookie_dir = COOKIE_DIR
        self.cookie_dir.mkdir(exist_ok=True)
    
    async def get_qrcode(self, platform: str) -> Dict[str, str]:
        """
        获取登录二维码
        Args:
            platform: 平台名称
        Returns:
            包含qrcode_id和qrcode_base64的字典
        """
        # 调试：输出DEPENDENCIES_AVAILABLE的实际值
        print(f"[LoginService.get_qrcode] 调试: DEPENDENCIES_AVAILABLE = {DEPENDENCIES_AVAILABLE}")
        print(f"[LoginService.get_qrcode] 调试: DEPENDENCIES_AVAILABLE类型 = {type(DEPENDENCIES_AVAILABLE)}")
        if not DEPENDENCIES_AVAILABLE:
            # 如果依赖不可用，返回提示信息
            return {
                "qrcode_id": "",
                "qrcode_base64": "",
                "expires_in": 120,
                "error": "请先安装完整依赖: pip install -r ../requirements.txt 和 playwright install"
            }
        
        try:
            # 创建登录会话
            print(f"[LoginService.get_qrcode] ========== 开始获取二维码 ==========")
            print(f"[LoginService.get_qrcode] platform参数值: '{platform}' (类型: {type(platform).__name__})")
            session_id = f"{platform}_{int(asyncio.get_event_loop().time())}"
            print(f"[LoginService.get_qrcode] 会话ID: {session_id}")
            
            # 参考 social-auto-upload-window 的方式，直接使用 playwright 启动浏览器
            print("[LoginService.get_qrcode] 步骤1: 启动 Playwright...")
            try:
                playwright_instance = await async_playwright().start()
                print("[LoginService.get_qrcode] ✓ Playwright 启动成功")
            except Exception as e:
                print(f"[LoginService.get_qrcode] ✗ Playwright 启动失败: {e}")
                raise Exception(f"Playwright启动失败: {e}")
            
            # 直接使用 chromium.launch，不使用CDP模式（更简单可靠）
            print("[LoginService.get_qrcode] 步骤2: 启动浏览器（使用系统Chrome）...")
            import platform as platform_module  # 使用别名避免覆盖platform参数
            chrome_paths = []
            if platform_module.system() == "Darwin":  # macOS
                chrome_paths = [
                    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                    "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
                    "/Applications/Chromium.app/Contents/MacOS/Chromium"
                ]
            elif platform_module.system() == "Windows":
                chrome_paths = [
                    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                    "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
                ]
            else:  # Linux
                chrome_paths = [
                    "/usr/bin/google-chrome",
                    "/usr/bin/google-chrome-stable",
                    "/usr/bin/chromium-browser",
                    "/usr/bin/chromium"
                ]
            
            browser = None
            chrome_found = False
            for chrome_path in chrome_paths:
                if os.path.exists(chrome_path):
                    print(f"[LoginService.get_qrcode] 找到Chrome: {chrome_path}")
                    try:
                        browser = await playwright_instance.chromium.launch(
                            headless=False,
                            executable_path=chrome_path,
                            args=['--disable-blink-features=AutomationControlled']
                        )
                        print(f"[LoginService.get_qrcode] ✓ Chrome 浏览器启动成功: {chrome_path}")
                        chrome_found = True
                        break
                    except Exception as e:
                        print(f"[LoginService.get_qrcode] 使用 {chrome_path} 启动失败: {e}")
                        continue
            
            if not chrome_found:
                print("[LoginService.get_qrcode] 尝试使用 channel='chrome' 参数...")
                try:
                    browser = await playwright_instance.chromium.launch(
                        headless=False,
                        channel="chrome",
                        args=['--disable-blink-features=AutomationControlled']
                    )
                    print("[LoginService.get_qrcode] ✓ Chrome 浏览器启动成功（使用channel参数）")
                    chrome_found = True
                except Exception as e:
                    print(f"[LoginService.get_qrcode] channel='chrome' 也失败: {e}")
            
            if not chrome_found:
                print("[LoginService.get_qrcode] 所有Chrome启动方式都失败，使用默认Chromium...")
                try:
                    browser = await playwright_instance.chromium.launch(
                        headless=False,
                        args=['--disable-blink-features=AutomationControlled']
                    )
                    print("[LoginService.get_qrcode] ✓ 使用默认Chromium启动成功")
                except Exception as e2:
                    print(f"[LoginService.get_qrcode] ✗ 默认Chromium也启动失败: {e2}")
                    raise Exception(f"所有浏览器启动方式都失败，最后错误: {e2}")
            
            # 创建浏览器上下文
            print("[LoginService.get_qrcode] 步骤3: 创建浏览器上下文...")
            try:
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                print("[LoginService.get_qrcode] ✓ 浏览器上下文创建成功")
            except Exception as e:
                print(f"[LoginService.get_qrcode] ✗ 浏览器上下文创建失败: {e}")
                raise Exception(f"浏览器上下文创建失败: {e}")
            
            # 创建新页面
            print("[LoginService.get_qrcode] 步骤4: 创建新页面...")
            try:
                page = await context.new_page()
                print("[LoginService.get_qrcode] ✓ 新页面创建成功")
                print(f"[LoginService.get_qrcode] 页面对象: {page}")
            except Exception as e:
                print(f"[LoginService.get_qrcode] ✗ 页面创建失败: {e}")
                raise Exception(f"页面创建失败: {e}")
            
            print("[LoginService.get_qrcode] ✓ 浏览器启动流程完成")
            
            # 根据平台打开登录页面（普通用户网站，不是创作者网站）
            print(f"[LoginService.get_qrcode] 调试: platform参数 = '{platform}' (类型: {type(platform)})")
            login_url = self._get_login_url(platform)
            print(f"[LoginService.get_qrcode] 步骤5: 准备打开网页: '{login_url}' (长度: {len(login_url) if login_url else 0})")
            print(f"[LoginService.get_qrcode] 当前页面URL: {page.url}")
            
            # 打开网页
            print(f"[LoginService.get_qrcode] 步骤6: 正在导航到 {login_url}...")
            try:
                # 对于抖音等有持续网络请求的网站，使用 'load' 而不是 'networkidle'
                # 'load' 等待页面load事件完成即可，不等待所有网络请求完成
                wait_strategy = 'load' if platform == 'dy' else 'networkidle'
                print(f"[LoginService.get_qrcode] 使用等待策略: {wait_strategy}")
                await page.goto(login_url, wait_until=wait_strategy, timeout=60000)
                current_url = page.url
                print(f"[LoginService.get_qrcode] ✓ 页面导航成功")
                print(f"[LoginService.get_qrcode] 当前URL: {current_url}")
                print(f"[LoginService.get_qrcode] 目标URL: {login_url}")
                if current_url != login_url:
                    print(f"[LoginService.get_qrcode] ⚠️  警告: 当前URL与目标URL不一致")
            except Exception as e:
                print(f"[LoginService.get_qrcode] ✗ 页面导航失败: {e}")
                import traceback
                print(f"[LoginService.get_qrcode] 错误堆栈:\n{traceback.format_exc()}")
                # 尝试截图
                try:
                    await page.screenshot(path="/tmp/navigation_error.png")
                    print("[LoginService.get_qrcode] 已保存错误截图到 /tmp/navigation_error.png")
                except:
                    pass
                raise Exception(f"页面导航失败: {e}")
            
            print(f"[LoginService.get_qrcode] 步骤7: 等待页面完全加载（3秒）...")
            await asyncio.sleep(3)  # 等待页面完全加载
            print(f"[LoginService.get_qrcode] ✓ 页面加载等待完成")
            
            # 保存初始的web_session值（用于后续比较判断是否真的登录了）
            no_logged_in_session = ""
            if platform == "xhs":
                try:
                    initial_cookies = await context.cookies()
                    initial_cookie_dict = {c["name"]: c["value"] for c in initial_cookies}
                    no_logged_in_session = initial_cookie_dict.get("web_session", "")
                    print(f"[LoginService.get_qrcode] 保存初始web_session值: {no_logged_in_session[:30] if no_logged_in_session else '(空)'}...")
                except Exception as e:
                    print(f"[LoginService.get_qrcode] ⚠️ 获取初始web_session失败: {e}")
                    no_logged_in_session = ""
            
            # 对于知乎，直接返回页面截图，跳过所有其他处理
            if platform == "zhihu":
                print(f"[LoginService.get_qrcode] 步骤8: 知乎平台 - 直接返回页面截图，跳过二维码提取...")
                # 知乎直接返回页面截图，不进行二维码提取
                screenshot_path = "/tmp/xhs_login_page.png"
                base64_qrcode = None
                
                # 尝试多种截图方式（按优先级顺序）
                # 方法1: 使用 CDP 直接截图（最快，不等待字体）
                cdp_session = None
                try:
                    print(f"[LoginService.get_qrcode] 尝试CDP截图（不等待字体）...")
                    # 检查页面是否仍然有效
                    if page.is_closed():
                        raise Exception("页面已关闭，无法使用CDP截图")
                    
                    # 使用 CDP 的 Page.captureScreenshot 命令，不等待字体加载
                    try:
                        cdp_session = await page.context.new_cdp_session(page)
                    except Exception as cdp_error:
                        print(f"[LoginService.get_qrcode] ⚠️ CDP session创建失败: {cdp_error}，跳过CDP方式")
                        raise
                    
                    result = await cdp_session.send("Page.captureScreenshot", {
                        "format": "png",
                        "quality": 90,
                    })
                    screenshot_data = base64.b64decode(result["data"])
                    with open(screenshot_path, "wb") as f:
                        f.write(screenshot_data)
                    print(f"[LoginService.get_qrcode] ✓ CDP截图成功，已保存到: {screenshot_path}")
                    base64_qrcode = result["data"]  # CDP 已经返回 base64
                    print(f"[LoginService.get_qrcode] ✓ 截图已转换为base64，长度: {len(base64_qrcode)}")
                    print("[LoginService.get_qrcode] ⚠️ 知乎直接返回页面截图作为二维码")
                except Exception as e:
                    print(f"[LoginService.get_qrcode] ✗ CDP截图失败: {e}")
                    # 清理CDP session（如果已创建）
                    if cdp_session:
                        try:
                            await cdp_session.detach()
                        except:
                            pass
                    
                    # 如果 CDP 失败，检查页面状态并尝试普通截图方式
                    if page.is_closed():
                        print(f"[LoginService.get_qrcode] ⚠️ 页面已关闭，无法截图")
                        raise Exception("页面已关闭，无法获取截图")
                    
                    # 尝试普通截图方式（使用更短的超时时间，避免等待字体）
                    screenshot_attempts = [
                        ("普通截图（10秒超时，不等待字体）", 10000),
                        ("普通截图（5秒超时）", 5000),
                        ("普通截图（3秒超时）", 3000),
                    ]
                    
                    for method_name, timeout_val in screenshot_attempts:
                        try:
                            print(f"[LoginService.get_qrcode] 尝试{method_name}...")
                            # 检查页面是否仍然有效
                            if page.is_closed():
                                print(f"[LoginService.get_qrcode] ✗ 页面已关闭，跳过{method_name}")
                                continue
                            
                            await page.screenshot(path=screenshot_path, timeout=timeout_val)
                            print(f"[LoginService.get_qrcode] ✓ {method_name}成功，已保存到: {screenshot_path}")
                            
                            # 读取截图文件并转换为base64
                            with open(screenshot_path, "rb") as f:
                                screenshot_data = f.read()
                                base64_qrcode = base64.b64encode(screenshot_data).decode('utf-8')
                                print(f"[LoginService.get_qrcode] ✓ 截图已转换为base64，长度: {len(base64_qrcode)}")
                                print("[LoginService.get_qrcode] ⚠️ 知乎直接返回页面截图作为二维码")
                            break
                        except Exception as e2:
                            print(f"[LoginService.get_qrcode] ✗ {method_name}失败: {e2}")
                            # 如果页面已关闭，不再尝试其他方法
                            if "closed" in str(e2).lower() or page.is_closed():
                                print(f"[LoginService.get_qrcode] ⚠️ 页面已关闭，停止尝试截图")
                                break
                            continue
                
                if base64_qrcode:
                    print(f"[LoginService.get_qrcode] ✓ 知乎二维码获取完成（使用截图）")
                    return {
                        "qrcode_id": f"{platform}_{int(asyncio.get_event_loop().time())}",
                        "qrcode_base64": base64_qrcode,
                        "expires_in": 120,
                    }
                else:
                    raise Exception("所有截图方式都失败，无法获取知乎登录页面截图")
            
            # 对于快手，需要直接点击登录按钮（二维码不会自动出现）
            elif platform == "ks":
                print(f"[LoginService.get_qrcode] 步骤8: 处理快手登录框（直接点击登录按钮）...")
                try:
                    login_button_selector = self._get_login_button_selector(platform)
                    print(f"[LoginService.get_qrcode] 登录按钮选择器: {login_button_selector}")
                    if login_button_selector:
                        try:
                            login_button = await page.wait_for_selector(
                                login_button_selector, 
                                timeout=10000
                            )
                            if login_button:
                                print("[LoginService.get_qrcode] ✓ 找到登录按钮，准备点击...")
                                await login_button.click()
                                print("[LoginService.get_qrcode] ✓ 已点击登录按钮")
                                await asyncio.sleep(3)  # 等待登录框弹出
                                print("[LoginService.get_qrcode] ✓ 等待登录框弹出完成")
                            else:
                                print("[LoginService.get_qrcode] ✗ 未找到登录按钮元素")
                        except Exception as e:
                            print(f"[LoginService.get_qrcode] ✗ 点击登录按钮失败: {e}")
                            import traceback
                            print(f"[LoginService.get_qrcode] 错误堆栈:\n{traceback.format_exc()}")
                            # 尝试其他可能的登录按钮选择器
                            print("[LoginService.get_qrcode] 尝试快手的备用登录按钮选择器...")
                            try:
                                backup_selectors = [
                                    "xpath=//span[contains(@class,'btn-words')]",
                                    "xpath=//span[contains(text(),'立即') and contains(text(),'登录')]",
                                    "xpath=//span[contains(.,'登录')]",
                                    "xpath=//button[contains(.,'登录')]",
                                    "css=.btn-words"
                                ]
                                for backup_selector in backup_selectors:
                                    try:
                                        login_element = await page.wait_for_selector(backup_selector, timeout=3000)
                                        if login_element:
                                            print(f"[LoginService.get_qrcode] ✓ 通过备用选择器找到登录按钮: {backup_selector}")
                                            await login_element.click()
                                            await asyncio.sleep(3)
                                            print("[LoginService.get_qrcode] ✓ 通过备用选择器点击登录成功")
                                            break
                                    except:
                                        continue
                                else:
                                    print("[LoginService.get_qrcode] ✗ 所有备用登录按钮选择器都失败")
                            except Exception as e2:
                                print(f"[LoginService.get_qrcode] ✗ 备用登录方式也失败: {e2}")
                except Exception as e:
                    print(f"[LoginService.get_qrcode] ✗ 处理登录框时出错: {e}")
                    import traceback
                    print(f"[LoginService.get_qrcode] 错误堆栈:\n{traceback.format_exc()}")
            # 对于掘金，需要点击登录按钮弹出登录对话框
            elif platform == "juejin":
                print(f"[LoginService.get_qrcode] 步骤8: 处理掘金登录框（点击登录按钮）...")
                try:
                    login_button_selector = self._get_login_button_selector(platform)
                    print(f"[LoginService.get_qrcode] 登录按钮选择器: {login_button_selector}")
                    if login_button_selector:
                        try:
                            login_button = await page.wait_for_selector(
                                login_button_selector, 
                                timeout=10000
                            )
                            if login_button:
                                print("[LoginService.get_qrcode] ✓ 找到登录按钮，准备点击...")
                                await login_button.click()
                                print("[LoginService.get_qrcode] ✓ 已点击登录按钮")
                                # 掘金登录框弹出和二维码加载可能需要更长时间
                                await asyncio.sleep(5)  # 增加等待时间到5秒
                                print("[LoginService.get_qrcode] ✓ 等待登录框弹出完成")
                                
                                # 尝试等待登录对话框出现
                                try:
                                    # 掘金登录对话框可能的选择器
                                    dialog_selectors = [
                                        "xpath=//div[contains(@class,'login')]",
                                        "xpath=//div[contains(@class,'modal')]",
                                        "xpath=//div[contains(@class,'dialog')]",
                                    ]
                                    for dialog_selector in dialog_selectors:
                                        try:
                                            await page.wait_for_selector(dialog_selector, timeout=3000)
                                            print(f"[LoginService.get_qrcode] ✓ 登录对话框已出现: {dialog_selector}")
                                            break
                                        except:
                                            continue
                                except:
                                    print("[LoginService.get_qrcode] 未检测到登录对话框，继续查找二维码...")
                            else:
                                print("[LoginService.get_qrcode] ✗ 未找到登录按钮元素")
                        except Exception as e:
                            print(f"[LoginService.get_qrcode] ✗ 点击登录按钮失败: {e}")
                            import traceback
                            print(f"[LoginService.get_qrcode] 错误堆栈:\n{traceback.format_exc()}")
                except Exception as e:
                    print(f"[LoginService.get_qrcode] ✗ 处理登录框时出错: {e}")
                    import traceback
                    print(f"[LoginService.get_qrcode] 错误堆栈:\n{traceback.format_exc()}")
            # 对于抖音，需要处理登录对话框（参考douyin/login.py的popup_login_dialog方法）
            elif platform == "dy":
                print(f"[LoginService.get_qrcode] 步骤8: 处理抖音登录框...")
                try:
                    dialog_selector = "xpath=//div[@id='login-panel-new']"
                    print(f"[LoginService.get_qrcode] 等待登录对话框出现，选择器: {dialog_selector}")
                    try:
                        # 检查对话框是否自动弹出，等待最多10秒
                        await page.wait_for_selector(dialog_selector, timeout=10000)
                        print("[LoginService.get_qrcode] ✓ 登录对话框已自动弹出")
                    except Exception as e:
                        print(f"[LoginService.get_qrcode] 登录对话框未自动弹出: {e}")
                        # 如果对话框没有自动弹出，点击登录按钮
                        print("[LoginService.get_qrcode] 尝试点击登录按钮...")
                        login_button_selector = self._get_login_button_selector(platform)
                        print(f"[LoginService.get_qrcode] 登录按钮选择器: {login_button_selector}")
                        if login_button_selector:
                            try:
                                login_button = await page.wait_for_selector(
                                    login_button_selector, 
                                    timeout=5000
                                )
                                if login_button:
                                    print("[LoginService.get_qrcode] ✓ 找到登录按钮，准备点击...")
                                    await login_button.click()
                                    print("[LoginService.get_qrcode] ✓ 已点击登录按钮")
                                    await asyncio.sleep(0.5)  # 等待登录框弹出（与douyin/login.py一致）
                                    print("[LoginService.get_qrcode] ✓ 等待登录框弹出完成")
                                else:
                                    print("[LoginService.get_qrcode] ✗ 未找到登录按钮元素")
                            except Exception as e:
                                print(f"[LoginService.get_qrcode] ✗ 点击登录按钮失败: {e}")
                                import traceback
                                print(f"[LoginService.get_qrcode] 错误堆栈:\n{traceback.format_exc()}")
                except Exception as e:
                    print(f"[LoginService.get_qrcode] ✗ 处理登录框时出错: {e}")
                    import traceback
                    print(f"[LoginService.get_qrcode] 错误堆栈:\n{traceback.format_exc()}")
            # 对于小红书，如果登录框没有自动弹出，需要点击登录按钮
            elif platform == "xhs":
                print(f"[LoginService.get_qrcode] 步骤8: 处理小红书登录框...")
                try:
                    # 先尝试查找二维码，如果找不到，说明登录框没有弹出
                    qrcode_selector = self._get_qrcode_selector(platform)
                    print(f"[LoginService.get_qrcode] 等待二维码出现，选择器: {qrcode_selector}")
                    try:
                        await page.wait_for_selector(qrcode_selector, timeout=5000)
                        print("[LoginService.get_qrcode] ✓ 二维码已自动出现")
                    except Exception as e:
                        print(f"[LoginService.get_qrcode] 二维码未自动出现: {e}")
                        # 如果找不到二维码，点击登录按钮
                        print("[LoginService.get_qrcode] 尝试点击登录按钮...")
                        login_button_selector = self._get_login_button_selector(platform)
                        print(f"[LoginService.get_qrcode] 登录按钮选择器: {login_button_selector}")
                        if login_button_selector:
                            try:
                                login_button = await page.wait_for_selector(
                                    login_button_selector, 
                                    timeout=5000
                                )
                                if login_button:
                                    print("[LoginService.get_qrcode] ✓ 找到登录按钮，准备点击...")
                                    await login_button.click()
                                    print("[LoginService.get_qrcode] ✓ 已点击登录按钮")
                                    await asyncio.sleep(2)  # 等待登录框弹出
                                    print("[LoginService.get_qrcode] ✓ 等待登录框弹出完成")
                                else:
                                    print("[LoginService.get_qrcode] ✗ 未找到登录按钮元素")
                            except Exception as e:
                                print(f"[LoginService.get_qrcode] ✗ 点击登录按钮失败: {e}")
                                import traceback
                                print(f"[LoginService.get_qrcode] 错误堆栈:\n{traceback.format_exc()}")
                                # 尝试其他可能的登录按钮选择器
                                print("[LoginService.get_qrcode] 尝试备用登录按钮选择器...")
                                try:
                                    login_link = await page.query_selector("text=登录")
                                    if login_link:
                                        await login_link.click()
                                        await asyncio.sleep(2)
                                        print("[LoginService.get_qrcode] ✓ 通过文字链接点击登录成功")
                                    else:
                                        print("[LoginService.get_qrcode] ✗ 未找到文字链接登录按钮")
                                except Exception as e2:
                                    print(f"[LoginService.get_qrcode] ✗ 备用登录方式也失败: {e2}")
                except Exception as e:
                    print(f"[LoginService.get_qrcode] ✗ 处理登录框时出错: {e}")
                    import traceback
                    print(f"[LoginService.get_qrcode] 错误堆栈:\n{traceback.format_exc()}")
            # 查找二维码（非知乎平台）
            print(f"[LoginService.get_qrcode] 步骤9: 开始查找二维码...")
            qrcode_selector = self._get_qrcode_selector(platform)
            print(f"[LoginService.get_qrcode] 二维码选择器: {qrcode_selector}")
            
            # 初始化变量（用于非知乎平台）
            zhihu_is_canvas = False
            
            # 对于掘金，使用更长的等待时间和多个选择器
            if platform == "juejin":
                print(f"[LoginService.get_qrcode] 掘金平台：使用扩展的二维码查找策略...")
                # 尝试多个可能的二维码选择器（优先使用精确匹配）
                juejin_qrcode_selectors = [
                    "xpath=//img[@class='qrcode-img']",  # 精确匹配掘金的二维码class
                    "xpath=//img[contains(@class,'qrcode-img')]",  # 包含qrcode-img
                    "xpath=//img[contains(@class,'qrcode')]",  # 包含qrcode
                    "xpath=//canvas[contains(@class,'qrcode')]",  # canvas二维码
                    "xpath=//div[contains(@class,'qrcode')]//img",  # div内的img
                    "xpath=//img[contains(@src,'qrcode')]",  # src包含qrcode
                    "xpath=//img[contains(@src,'data:image')]",  # data URI格式的图片
                    "xpath=//div[contains(@class,'login')]//img",  # 登录框内的img
                ]
                qrcode_found = False
                for selector in juejin_qrcode_selectors:
                    try:
                        print(f"[LoginService.get_qrcode] 尝试选择器: {selector}")
                        await page.wait_for_selector(selector, timeout=5000)
                        print(f"[LoginService.get_qrcode] ✓ 找到二维码元素: {selector}")
                        qrcode_selector = selector
                        qrcode_found = True
                        break
                    except Exception as e:
                        print(f"[LoginService.get_qrcode] 选择器 {selector} 未找到: {e}")
                        continue
                
                if not qrcode_found:
                    print(f"[LoginService.get_qrcode] ✗ 所有掘金二维码选择器都未找到")
                    # 保存截图用于调试
                    try:
                        await page.screenshot(path="/tmp/juejin_login_page.png", full_page=True)
                        print("[LoginService.get_qrcode] ✓ 已保存页面截图到 /tmp/juejin_login_page.png")
                    except:
                        pass
                    raise Exception("无法找到掘金二维码，请查看截图: /tmp/juejin_login_page.png")
            else:
                # 其他平台使用原来的逻辑
                # 等待二维码出现，最多等待5秒（减少等待时间）
                print(f"[LoginService.get_qrcode] 等待二维码元素出现（最多5秒）...")
                try:
                    await page.wait_for_selector(qrcode_selector, timeout=5000)
                    print("[LoginService.get_qrcode] ✓ 二维码元素已找到")
                except Exception as e:
                    print(f"[LoginService.get_qrcode] ✗ 等待二维码超时: {e}")
                # 尝试截图查看页面状态
                print("[LoginService.get_qrcode] 尝试保存页面截图...")
                try:
                    await page.screenshot(path="/tmp/xhs_login_page.png", full_page=True)
                    print("[LoginService.get_qrcode] ✓ 已保存页面截图到 /tmp/xhs_login_page.png")
                    # 获取页面HTML内容（前1000字符）
                    try:
                        page_content = await page.content()
                        with open("/tmp/xhs_login_page.html", "w", encoding="utf-8") as f:
                            f.write(page_content[:5000])  # 只保存前5000字符
                        print("[LoginService.get_qrcode] ✓ 已保存页面HTML片段到 /tmp/xhs_login_page.html")
                    except:
                        pass
                except Exception as screenshot_error:
                    print(f"[LoginService.get_qrcode] ✗ 截图保存失败: {screenshot_error}")
            
            print(f"[LoginService.get_qrcode] 步骤10: 提取二维码图片...")
            # 对于知乎，如果是canvas元素，使用专门的canvas提取方法
            if platform == "zhihu" and zhihu_is_canvas:
                print("[LoginService.get_qrcode] 使用canvas提取方法...")
                from tools.crawler_util import find_qrcode_img_from_canvas
                try:
                    base64_qrcode = await find_qrcode_img_from_canvas(page, qrcode_selector)
                    print(f"[LoginService.get_qrcode] canvas提取结果: {'成功' if base64_qrcode else '失败'}")
                    if base64_qrcode:
                        print(f"[LoginService.get_qrcode] canvas提取的base64长度: {len(base64_qrcode)}, 前50字符: {base64_qrcode[:50]}")
                    else:
                        print("[LoginService.get_qrcode] canvas提取失败，直接返回截图...")
                        # 知乎提取失败，直接返回截图
                        try:
                            screenshot_path = "/tmp/xhs_login_page.png"
                            # 直接截图，不检查文件是否存在（确保是最新的）
                            await page.screenshot(path=screenshot_path, full_page=True)
                            print(f"[LoginService.get_qrcode] ✓ 已保存页面截图到 {screenshot_path}")
                            
                            # 读取截图文件并转换为base64
                            with open(screenshot_path, "rb") as f:
                                screenshot_data = f.read()
                                base64_qrcode = base64.b64encode(screenshot_data).decode('utf-8')
                                print(f"[LoginService.get_qrcode] ✓ 知乎截图已转换为base64，长度: {len(base64_qrcode)}")
                                print("[LoginService.get_qrcode] ⚠️ 知乎使用页面截图作为备用二维码")
                        except Exception as screenshot_error:
                            print(f"[LoginService.get_qrcode] ✗ 获取知乎截图失败: {screenshot_error}")
                            base64_qrcode = ""
                except Exception as e:
                    print(f"[LoginService.get_qrcode] ✗ canvas提取失败: {e}")
                    import traceback
                    print(f"[LoginService.get_qrcode] 错误堆栈:\n{traceback.format_exc()}")
                    # 知乎canvas提取异常，直接返回截图
                    try:
                        screenshot_path = "/tmp/xhs_login_page.png"
                        # 直接截图，不检查文件是否存在（确保是最新的）
                        await page.screenshot(path=screenshot_path, full_page=True)
                        print(f"[LoginService.get_qrcode] ✓ 已保存页面截图到 {screenshot_path}")
                        
                        with open(screenshot_path, "rb") as f:
                            screenshot_data = f.read()
                            base64_qrcode = base64.b64encode(screenshot_data).decode('utf-8')
                            print(f"[LoginService.get_qrcode] ✓ 知乎截图已转换为base64，长度: {len(base64_qrcode)}")
                            print("[LoginService.get_qrcode] ⚠️ 知乎使用页面截图作为备用二维码")
                    except Exception as screenshot_error:
                        print(f"[LoginService.get_qrcode] ✗ 获取知乎截图失败: {screenshot_error}")
                        base64_qrcode = ""
            else:
                base64_qrcode = await find_login_qrcode(page, qrcode_selector)
                print(f"[LoginService.get_qrcode] 第一次提取结果: {'成功' if base64_qrcode else '失败'}")
            if base64_qrcode:
                print(f"[LoginService.get_qrcode] 提取的base64长度: {len(base64_qrcode)}, 前50字符: {base64_qrcode[:50]}")
            
            if not base64_qrcode:
                print("[LoginService.get_qrcode] ✗ 二维码提取失败，直接返回登录页面截图...")
                # 如果无法获取二维码，直接返回登录页面截图
                try:
                    screenshot_path = "/tmp/xhs_login_page.png"
                    
                    # 直接截图，不检查文件是否存在（确保是最新的）
                    await page.screenshot(path=screenshot_path, full_page=True)
                    print(f"[LoginService.get_qrcode] ✓ 已保存页面截图到 {screenshot_path}")
                    
                    # 读取截图文件并转换为base64
                    with open(screenshot_path, "rb") as f:
                        screenshot_data = f.read()
                        base64_qrcode = base64.b64encode(screenshot_data).decode('utf-8')
                        print(f"[LoginService.get_qrcode] ✓ 截图已转换为base64，长度: {len(base64_qrcode)}")
                        print("[LoginService.get_qrcode] ⚠️ 使用登录页面截图作为备用二维码")
                except Exception as screenshot_error:
                    print(f"[LoginService.get_qrcode] ✗ 获取截图失败: {screenshot_error}")
                    import traceback
                    print(f"[LoginService.get_qrcode] 错误堆栈:\n{traceback.format_exc()}")
                    # 如果截图也失败，尝试最后一次截图
                    try:
                        screenshot_path = "/tmp/xhs_login_page.png"
                        await page.screenshot(path=screenshot_path, full_page=True)
                        with open(screenshot_path, "rb") as f:
                            screenshot_data = f.read()
                            base64_qrcode = base64.b64encode(screenshot_data).decode('utf-8')
                            print("[LoginService.get_qrcode] ✓ 最后一次截图成功，返回截图")
                    except Exception as final_error:
                        print(f"[LoginService.get_qrcode] ✗ 最后一次截图也失败: {final_error}")
                        # 即使截图失败，也返回一个空字符串，而不是抛出异常
                        base64_qrcode = ""
                        print("[LoginService.get_qrcode] ⚠️ 所有方式都失败，返回空二维码")
            
            # 清理base64字符串，确保返回纯base64（不包含data:image前缀）
            # find_login_qrcode 可能返回:
            # 1. 纯base64字符串
            # 2. data:image/png;base64,xxxxx 格式
            # 3. URL地址（需要下载）
            print(f"[LoginService.get_qrcode] 原始base64格式检查...")
            print(f"[LoginService.get_qrcode] 前100字符: {base64_qrcode[:100]}")
            
            if base64_qrcode.startswith("data:image"):
                # 如果已经包含data:image前缀，提取纯base64部分
                if "," in base64_qrcode:
                    base64_qrcode = base64_qrcode.split(",", 1)[1]
                    print("[LoginService.get_qrcode] ✓ 已移除data:image前缀")
            elif base64_qrcode.startswith("http://") or base64_qrcode.startswith("https://"):
                # 如果是URL，需要下载
                print(f"[LoginService.get_qrcode] 检测到URL，需要下载: {base64_qrcode}")
                try:
                    import httpx
                    async with httpx.AsyncClient(follow_redirects=True) as client:
                        resp = await client.get(base64_qrcode, headers={"User-Agent": "Mozilla/5.0"})
                        if resp.status_code == 200:
                            base64_qrcode = base64.b64encode(resp.content).decode('utf-8')
                            print("[LoginService.get_qrcode] ✓ 从URL下载二维码成功")
                        else:
                            raise Exception(f"下载二维码失败，状态码: {resp.status_code}")
                except Exception as e:
                    print(f"[LoginService.get_qrcode] ✗ 下载二维码失败: {e}")
                    raise
            
            # 验证base64格式
            try:
                base64.b64decode(base64_qrcode)
                print("[LoginService.get_qrcode] ✓ base64格式验证通过")
            except Exception as e:
                print(f"[LoginService.get_qrcode] ✗ base64格式验证失败: {e}")
                raise Exception(f"二维码base64格式无效: {e}")
            
            print(f"[LoginService.get_qrcode] ✓ 成功获取二维码，最终base64长度: {len(base64_qrcode)}")
            
            # 保存会话信息（包括初始的web_session值）
            login_sessions[session_id] = {
                "platform": platform,
                "browser": browser,
                "context": context,
                "page": page,
                "playwright": playwright_instance,  # 保存playwright实例
                "status": "pending",
                "created_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(seconds=120),
                "no_logged_in_session": no_logged_in_session  # 保存初始web_session值
            }
            
            return {
                "qrcode_id": session_id,
                "qrcode_base64": base64_qrcode,
                "expires_in": 120
            }
        except Exception as e:
            import traceback
            error_msg = f"获取二维码失败: {str(e)}"
            error_trace = traceback.format_exc()
            print(f"[LoginService.get_qrcode] ✗ {error_msg}")
            print(f"[LoginService.get_qrcode] 完整错误堆栈:\n{error_trace}")
            # 尝试保存最终状态截图
            try:
                if 'page' in locals():
                    await page.screenshot(path="/tmp/xhs_login_error_final.png", full_page=True)
                    print("[LoginService.get_qrcode] ✓ 已保存最终错误截图到 /tmp/xhs_login_error_final.png")
            except:
                pass
            raise Exception(error_msg)
    
    async def check_login_status(self, qrcode_id: str) -> Dict[str, any]:
        """
        检查登录状态
        Args:
            qrcode_id: 二维码ID
        Returns:
            登录状态信息
        """
        if qrcode_id not in login_sessions:
            # 会话不存在，检查是否有已保存的cookie（可能已经登录成功但会话过期）
            print(f"[LoginService.check_login_status] 会话 {qrcode_id} 不存在，检查是否有已保存的cookie...")
            # 从qrcode_id中提取平台名称（格式：platform_timestamp）
            platform = qrcode_id.split("_")[0] if "_" in qrcode_id else "xhs"
            cookie_file = self.cookie_dir / f"{platform}_cookies.json"
            print(f"[LoginService.check_login_status] 检查平台 {platform} 的cookie文件: {cookie_file}")
            if cookie_file.exists():
                print(f"[LoginService.check_login_status] ✓ 找到已保存的cookie文件: {cookie_file}")
                try:
                    with open(cookie_file, "r", encoding="utf-8") as f:
                        cookie_data = json.load(f)
                        cookie_str = cookie_data.get("cookie_str", "")
                        if cookie_str:
                            print(f"[LoginService.check_login_status] ✓ Cookie已存在，返回success状态")
                            return {
                                "status": "success",
                                "message": "登录成功（cookie已保存）",
                                "cookie": cookie_str
                            }
                except Exception as e:
                    print(f"[LoginService.check_login_status] 读取cookie文件失败: {e}")
            else:
                print(f"[LoginService.check_login_status] Cookie文件不存在: {cookie_file}")
            return {"status": "expired", "message": "会话已过期"}
        
        session = login_sessions[qrcode_id]
        
        # 检查是否过期（但不过早清理，给用户更多时间）
        if datetime.now() > session["expires_at"]:
            # 即使过期，也先检查一下登录状态，可能用户已经登录成功
            print(f"[LoginService.check_login_status] 会话已过期，但先检查登录状态...")
            try:
                context: BrowserContext = session.get("context")
                page: Page = session.get("page")
                platform = session.get("platform", "xhs")
                
                if context and page:
                    try:
                        cookies = await asyncio.wait_for(context.cookies(), timeout=5.0)
                        cookie_dict = {c["name"]: c["value"] for c in cookies}
                        is_logged_in = self._check_platform_login_status(platform, cookie_dict, page)
                    except asyncio.TimeoutError:
                        print(f"[LoginService.check_login_status] 检查过期会话的登录状态超时")
                        is_logged_in = False
                    except Exception as e:
                        print(f"[LoginService.check_login_status] 检查过期会话的登录状态出错: {e}")
                        is_logged_in = False
                    
                    if is_logged_in:
                        # 即使过期，如果检测到登录成功，也保存cookie
                        print(f"[LoginService.check_login_status] 检测到登录成功（即使会话过期），保存cookie...")
                        cookie_str = "; ".join([f"{k}={v}" for k, v in cookie_dict.items()])
                        await self._save_cookie(platform, cookie_str, cookie_dict)
                        await self._cleanup_session(qrcode_id)
                        return {
                            "status": "success",
                            "message": "登录成功",
                            "cookie": cookie_str
                        }
            except Exception as e:
                print(f"[LoginService.check_login_status] 检查过期会话的登录状态时出错: {e}")
            
            # 如果检查失败，再清理会话
            await self._cleanup_session(qrcode_id)
            return {"status": "expired", "message": "二维码已过期，请重新获取二维码"}
        
        try:
            context: BrowserContext = session["context"]
            page: Page = session["page"]
            platform = session["platform"]
            
            # 检查登录状态
            # 对于快手，尝试获取所有cookie（不指定URL），因为passToken可能在.kuaishou.com域下
            if platform == "ks":
                # 先尝试获取所有cookie
                cookies = await context.cookies()
                print(f"[LoginService.check_login_status] 快手：获取所有cookie，数量: {len(cookies)}")
                # 如果没有找到passToken，再尝试指定域名
                cookie_dict_temp = {c["name"]: c["value"] for c in cookies}
                if "passToken" not in cookie_dict_temp:
                    print(f"[LoginService.check_login_status] 快手：在所有cookie中未找到passToken，尝试获取www.kuaishou.com的cookie...")
                    cookies_specific = await context.cookies("https://www.kuaishou.com")
                    print(f"[LoginService.check_login_status] 快手：www.kuaishou.com域的cookie数量: {len(cookies_specific)}")
                    # 合并cookie
                    cookies_dict = {c["name"]: c for c in cookies}
                    for c in cookies_specific:
                        cookies_dict[c["name"]] = c
                    cookies = list(cookies_dict.values())
                    print(f"[LoginService.check_login_status] 快手：合并后的cookie数量: {len(cookies)}")
            else:
                # 添加超时控制，避免获取cookie时阻塞太久
                try:
                    cookies = await asyncio.wait_for(context.cookies(), timeout=5.0)
                except asyncio.TimeoutError:
                    print(f"[LoginService.check_login_status] 获取cookie超时，返回pending状态")
                    return {
                        "status": "pending",
                        "message": "正在检查登录状态，请稍候..."
                    }
            
            cookie_dict = {}
            for cookie in cookies:
                cookie_dict[cookie["name"]] = cookie["value"]
            
            # 根据平台判断登录状态
            print(f"[LoginService.check_login_status] 获取到 {len(cookie_dict)} 个Cookie")
            print(f"[LoginService.check_login_status] Cookie键列表（前20个）: {list(cookie_dict.keys())[:20]}")
            # 特别检查passToken
            if platform == "ks":
                passToken = cookie_dict.get("passToken")
                print(f"[LoginService.check_login_status] 快手passToken: {passToken[:30] if passToken and len(passToken) > 30 else passToken}... (存在: {bool(passToken)})")
            
            # 检查登录状态（同步函数，快速执行）
            # 获取初始的web_session值（用于比较）
            no_logged_in_session = session.get("no_logged_in_session", "")
            try:
                is_logged_in = self._check_platform_login_status(platform, cookie_dict, page, no_logged_in_session)
            except Exception as e:
                print(f"[LoginService.check_login_status] 检查登录状态出错: {e}")
                import traceback
                print(f"[LoginService.check_login_status] 错误堆栈:\n{traceback.format_exc()}")
                # 如果检查出错，也返回pending，不中断流程
                is_logged_in = False
            
            print(f"[LoginService.check_login_status] 登录状态检查结果: {is_logged_in}")
            
            if is_logged_in:
                # 保存cookie
                print(f"[LoginService.check_login_status] 检测到登录成功，开始保存cookie...")
                cookie_str = "; ".join([f"{k}={v}" for k, v in cookie_dict.items()])
                print(f"[LoginService.check_login_status] Cookie字符串长度: {len(cookie_str)}")
                await self._save_cookie(platform, cookie_str, cookie_dict)
                print(f"[LoginService.check_login_status] ✓ Cookie保存完成")
                
                session["status"] = "success"
                session["cookie"] = cookie_str
                session["cookie_dict"] = cookie_dict
                
                # 登录成功后，前端会收到success响应并自动关闭二维码显示
                # 这里不需要等待二维码消失，直接返回success即可
                # 延迟清理，给前端时间获取结果（延迟2秒后关闭浏览器，确保前端已收到success响应并关闭二维码显示）
                print(f"[LoginService.check_login_status] 登录成功，将在2秒后关闭浏览器（给前端时间关闭二维码显示）...")
                asyncio.create_task(self._delayed_cleanup(qrcode_id, 2))
                
                return {
                    "status": "success",
                    "message": "登录成功",
                    "cookie": cookie_str
                }
            
            return {
                "status": "pending",
                "message": "等待扫码"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def _cleanup_session(self, qrcode_id: str):
        """清理登录会话"""
        if qrcode_id not in login_sessions:
            return
        
        session = login_sessions[qrcode_id]
        print(f"[LoginService._cleanup_session] 开始清理会话: {qrcode_id}")
        
        try:
            # 按照正确顺序关闭：先关闭page，再关闭context，再关闭browser，最后关闭playwright
            if "page" in session and session["page"]:
                try:
                    await session["page"].close()
                    print(f"[LoginService._cleanup_session] ✓ 页面已关闭")
                except Exception as e:
                    print(f"[LoginService._cleanup_session] 关闭页面时出错: {e}")
            
            if "context" in session and session["context"]:
                try:
                    await session["context"].close()
                    print(f"[LoginService._cleanup_session] ✓ 浏览器上下文已关闭")
                except Exception as e:
                    print(f"[LoginService._cleanup_session] 关闭浏览器上下文时出错: {e}")
            
            if "browser" in session and session["browser"]:
                try:
                    await session["browser"].close()
                    print(f"[LoginService._cleanup_session] ✓ 浏览器已关闭")
                except Exception as e:
                    print(f"[LoginService._cleanup_session] 关闭浏览器时出错: {e}")
            
            if "playwright" in session and session["playwright"]:
                try:
                    await session["playwright"].stop()
                    print(f"[LoginService._cleanup_session] ✓ Playwright已停止")
                except Exception as e:
                    print(f"[LoginService._cleanup_session] 停止Playwright时出错: {e}")
        except Exception as e:
            print(f"[LoginService._cleanup_session] 清理会话时出错: {e}")
            import traceback
            print(f"[LoginService._cleanup_session] 错误堆栈:\n{traceback.format_exc()}")
        finally:
            # 确保从sessions中删除，即使关闭过程出错
            if qrcode_id in login_sessions:
                del login_sessions[qrcode_id]
                print(f"[LoginService._cleanup_session] ✓ 会话已从缓存中删除")
    
    async def _delayed_cleanup(self, qrcode_id: str, delay: int):
        """延迟清理会话"""
        await asyncio.sleep(delay)
        await self._cleanup_session(qrcode_id)
    
    def _get_login_url(self, platform: str) -> str:
        """获取平台登录URL（普通用户网站，不是创作者网站）"""
        urls = {
            "xhs": "https://www.xiaohongshu.com/explore",  # 小红书探索页面，会自动弹出登录框
            "dy": "https://www.douyin.com",
            "ks": "https://www.kuaishou.com",
            "bili": "https://www.bilibili.com",
            "wb": "https://weibo.com",
            "tieba": "https://tieba.baidu.com",
            "zhihu": "https://www.zhihu.com",
            "juejin": "https://juejin.cn",  # 掘金
            "medium": "https://medium.com"  # Medium
        }
        result = urls.get(platform, "")
        print(f"[LoginService._get_login_url] platform='{platform}', 返回URL='{result}'")
        return result
    
    def _get_qrcode_selector(self, platform: str) -> str:
        """获取二维码选择器"""
        selectors = {
            "xhs": "xpath=//img[@class='qrcode-img']",  # 小红书二维码选择器
            "dy": "xpath=//div[@id='animate_qrcode_container']//img",  # 抖音二维码选择器（与douyin/login.py一致）
            "ks": "xpath=//div[@class='qrcode-img']//img",  # 快手二维码选择器（与kuaishou/login.py一致）
            "bili": "xpath=//img[contains(@class,'qrcode')]",
            "wb": "xpath=//img[contains(@class,'qrcode')]",
            "tieba": "xpath=//img[contains(@class,'qrcode')]",
            "zhihu": "xpath=//canvas[@class='Qrcode-qrcode']",  # 知乎二维码选择器（使用canvas元素）
            "juejin": "xpath=//img[@class='qrcode-img']",  # 掘金二维码选择器（精确匹配class='qrcode-img'）
            "medium": "xpath=//img[contains(@class,'qrcode')]"  # Medium二维码选择器
        }
        return selectors.get(platform, "xpath=//img[contains(@class,'qrcode')]")
    
    def _get_login_button_selector(self, platform: str) -> str:
        """获取登录按钮选择器（如果登录框没有自动弹出）"""
        selectors = {
            "xhs": "xpath=//*[@id='app']/div[1]/div[2]/div[1]/ul/div[1]/button",  # 小红书登录按钮
            "dy": "xpath=//p[text() = '登录']",  # 抖音登录按钮（与douyin/login.py一致）
            "ks": "xpath=//span[contains(@class,'btn-words') and contains(.,'登录')]",  # 快手登录按钮（匹配<span class="btn-words">...登录</span>）
            "bili": "",
            "wb": "",
            "tieba": "",
            "zhihu": "xpath=//button[contains(text(),'扫码登录')]",  # 知乎扫码登录按钮
            "juejin": "xpath=//button[contains(@class,'login-button')]",  # 掘金登录按钮
            "medium": ""  # Medium登录按钮
        }
        return selectors.get(platform, "")
    
    def _check_platform_login_status(self, platform: str, cookie_dict: Dict, page: Page, no_logged_in_session: str = "") -> bool:
        """检查平台登录状态"""
        print(f"[LoginService._check_platform_login_status] 检查平台 {platform} 的登录状态...")
        print(f"[LoginService._check_platform_login_status] Cookie数量: {len(cookie_dict)}")
        print(f"[LoginService._check_platform_login_status] Cookie键列表: {list(cookie_dict.keys())[:20]}")
        
        # 根据平台的关键cookie判断
        platform_key_cookies = {
            "xhs": ["web_session", "a1", "webId"],  # 小红书多个关键cookie
            "dy": ["sid_guard", "sid_tt"],
            "ks": ["passToken"],  # 快手使用passToken判断登录状态（与kuaishou/login.py一致）
            "bili": ["SESSDATA", "DedeUserID"],
            "wb": ["SUB", "SUBP"],
            "tieba": ["BAIDUID"],
            "zhihu": ["z_c0"],
            "juejin": ["sessionid"],  # 掘金使用sessionid判断登录状态
            "medium": ["sid"]  # Medium使用sid判断登录状态
        }
        
        key_cookies = platform_key_cookies.get(platform, [])
        if key_cookies:
            # 检查关键cookie是否存在且有值（至少有一个关键cookie存在）
            for key_cookie in key_cookies:
                cookie_value = cookie_dict.get(key_cookie)
                print(f"[LoginService._check_platform_login_status] 检查关键Cookie '{key_cookie}' = '{cookie_value[:30] if cookie_value and len(cookie_value) > 30 else cookie_value}...' (长度: {len(cookie_value) if cookie_value else 0})")
                if cookie_value and len(cookie_value) > 10:  # cookie值长度大于10才认为有效
                    print(f"[LoginService._check_platform_login_status] ✓ 找到有效关键Cookie: {key_cookie}")
                    # 对于小红书，需要比较web_session是否变化
                    if platform == "xhs" and key_cookie == "web_session":
                        current_web_session = cookie_value
                        print(f"[LoginService._check_platform_login_status] 初始web_session: {no_logged_in_session[:30] if no_logged_in_session else '(空)'}...")
                        print(f"[LoginService._check_platform_login_status] 当前web_session: {current_web_session[:30] if current_web_session else '(空)'}...")
                        
                        # 如果初始值为空，但当前有值，说明登录了
                        if not no_logged_in_session and current_web_session:
                            print(f"[LoginService._check_platform_login_status] ✓ 初始值为空但当前有值，说明已登录")
                            return True
                        
                        # 如果初始值和当前值都存在且不同，说明登录了
                        if no_logged_in_session and current_web_session and no_logged_in_session != current_web_session:
                            print(f"[LoginService._check_platform_login_status] ✓ web_session已变化，说明已登录")
                            return True
                        
                        # 如果初始值和当前值相同，说明还没有登录（只是保留了之前的cookie）
                        if no_logged_in_session and current_web_session and no_logged_in_session == current_web_session:
                            print(f"[LoginService._check_platform_login_status] ⚠️ web_session未变化，说明还未登录（可能是之前的cookie）")
                            return False
                        
                        # 如果都没有值，说明未登录
                        if not current_web_session:
                            print(f"[LoginService._check_platform_login_status] ✗ web_session不存在，未登录")
                            return False
                    elif platform == "xhs":
                        # 对于其他关键cookie（a1, webId），也需要检查web_session是否变化
                        web_session = cookie_dict.get("web_session", "")
                        if web_session:
                            current_web_session = web_session
                            print(f"[LoginService._check_platform_login_status] 检查web_session变化: 初始={no_logged_in_session[:30] if no_logged_in_session else '(空)'}..., 当前={current_web_session[:30] if current_web_session else '(空)'}...")
                            
                            if not no_logged_in_session and current_web_session:
                                print(f"[LoginService._check_platform_login_status] ✓ 初始值为空但当前有值，说明已登录")
                                return True
                            
                            if no_logged_in_session and current_web_session and no_logged_in_session != current_web_session:
                                print(f"[LoginService._check_platform_login_status] ✓ web_session已变化，说明已登录")
                                return True
                            
                            if no_logged_in_session and current_web_session and no_logged_in_session == current_web_session:
                                print(f"[LoginService._check_platform_login_status] ⚠️ web_session未变化，说明还未登录")
                                return False
                    else:
                        # 其他平台直接返回True
                        return True
        
        print(f"[LoginService._check_platform_login_status] ✗ 未找到有效的关键Cookie")
        return False
    
    def _get_cookie_file_path(self, platform: str) -> Path:
        """
        获取cookie文件路径
        Args:
            platform: 平台名称
        Returns:
            cookie文件路径
        """
        # 使用统一的cookie目录（项目根目录下的cookies文件夹）
        cookie_dir = self.cookie_dir
        cookie_dir.mkdir(exist_ok=True)
        return cookie_dir / f"{platform}_cookies.json"
    
    async def _save_cookie(self, platform: str, cookie_str: str, cookie_dict: Dict):
        """保存cookie到文件"""
        try:
            cookie_file = self.cookie_dir / f"{platform}_cookies.json"
            print(f"[LoginService._save_cookie] 开始保存cookie，平台: {platform}")
            print(f"[LoginService._save_cookie] Cookie文件路径: {cookie_file}")
            print(f"[LoginService._save_cookie] Cookie数量: {len(cookie_dict)}")
            print(f"[LoginService._save_cookie] Cookie键列表: {list(cookie_dict.keys())[:10]}")
            
            cookie_data = {
                "cookie_str": cookie_str,
                "cookie_dict": cookie_dict,
                "platform": platform,
                "saved_at": datetime.now().isoformat()
            }
            with open(cookie_file, "w", encoding="utf-8") as f:
                json.dump(cookie_data, f, ensure_ascii=False, indent=2)
            
            print(f"[LoginService._save_cookie] ✓ Cookie已成功保存到: {cookie_file}")
            # 验证文件是否存在
            if cookie_file.exists():
                file_size = cookie_file.stat().st_size
                print(f"[LoginService._save_cookie] ✓ 文件验证成功，大小: {file_size} 字节")
            else:
                print(f"[LoginService._save_cookie] ✗ 文件保存后验证失败，文件不存在")
        except Exception as e:
            print(f"[LoginService._save_cookie] ✗ 保存cookie失败: {e}")
            import traceback
            print(f"[LoginService._save_cookie] 错误堆栈:\n{traceback.format_exc()}")
            raise
    
    async def delete_cookie(self, platform: str) -> bool:
        """
        删除指定平台的cookie
        Args:
            platform: 平台名称
        Returns:
            是否删除成功
        """
        try:
            # 使用与_save_cookie相同的路径格式（.json文件）
            cookie_file = self.cookie_dir / f"{platform}_cookies.json"
            if cookie_file.exists():
                cookie_file.unlink()
                print(f"[LoginService] 已删除cookie文件: {cookie_file}")
                return True
            print(f"[LoginService] Cookie文件不存在: {cookie_file}")
            return False
        except Exception as e:
            print(f"[LoginService] 删除cookie失败: {e}")
            import traceback
            print(f"[LoginService] 错误堆栈:\n{traceback.format_exc()}")
            return False
    
    async def load_cookie(self, platform: str) -> Optional[str]:
        """加载保存的cookie"""
        cookie_file = self.cookie_dir / f"{platform}_cookies.json"
        if cookie_file.exists():
            with open(cookie_file, "r", encoding="utf-8") as f:
                cookie_data = json.load(f)
                return cookie_data.get("cookie_str")
        return None
    
    async def has_valid_cookie(self, platform: str) -> bool:
        """检查是否有有效的cookie"""
        cookie = await self.load_cookie(platform)
        return cookie is not None and len(cookie) > 0
    
    async def verify_cookie_validity(self, platform: str, cookie_str: str) -> bool:
        """
        验证Cookie是否有效
        通过尝试使用Cookie访问平台API来验证
        """
        if not cookie_str or len(cookie_str) == 0:
            return False
        
        try:
            if platform == "xhs":
                # 对于小红书，直接使用API验证Cookie有效性（更简单、更快）
                from media_platform.xhs.client import XiaoHongShuClient
                
                try:
                    # 创建客户端并尝试ping接口验证Cookie
                    client = XiaoHongShuClient(cookies=cookie_str)
                    await client.pong()
                    print(f"[LoginService.verify_cookie_validity] ✓ Cookie验证成功（通过pong接口）")
                    return True
                except Exception as pong_error:
                    error_msg = str(pong_error)
                    print(f"[LoginService.verify_cookie_validity] ⚠️ pong接口验证失败: {pong_error}")
                    # 检查是否是权限错误（说明Cookie无效）
                    if "没有权限" in error_msg or "权限" in error_msg or "登录" in error_msg or "DataFetchError" in str(type(pong_error).__name__):
                        print(f"[LoginService.verify_cookie_validity] ❌ Cookie无效（权限错误）")
                        return False
                    # 其他错误可能是网络问题，暂时认为Cookie可能有效（避免误判）
                    print(f"[LoginService.verify_cookie_validity] ⚠️ 可能是网络问题，暂时认为Cookie有效")
                    return True
            else:
                # 其他平台暂时只检查Cookie是否存在
                return cookie_str is not None and len(cookie_str) > 0
        except Exception as e:
            print(f"[LoginService.verify_cookie_validity] Cookie验证过程出错: {e}")
            import traceback
            print(f"[LoginService.verify_cookie_validity] 错误堆栈:\n{traceback.format_exc()}")
            # 验证出错时，暂时认为Cookie有效（避免误判，让实际使用来判断）
            print(f"[LoginService.verify_cookie_validity] ⚠️ 验证出错，暂时认为Cookie有效，将在实际使用时判断")
            return True


# 全局登录服务实例
login_service = LoginService()

