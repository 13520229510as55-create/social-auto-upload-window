import asyncio
import sqlite3
import time

from playwright.async_api import async_playwright

from myUtils.auth import check_cookie
from utils.base_social_media import set_init_script
import uuid
from pathlib import Path
from conf import BASE_DIR, LOCAL_CHROME_HEADLESS

# 抖音登录
async def douyin_cookie_gen(id,status_queue):
    url_changed_event = asyncio.Event()
    async def on_url_change():
        # 检查是否是主框架的变化
        if page.url != original_url:
            url_changed_event.set()
    async with async_playwright() as playwright:
        options = {
            'headless': LOCAL_CHROME_HEADLESS
        }
        # Make sure to run headed.
        browser = await playwright.chromium.launch(**options)
        # Setup context however you like.
        context = await browser.new_context()  # Pass any options
        context = await set_init_script(context)
        # Pause the page, and start recording manually.
        page = await context.new_page()
        await page.goto("https://creator.douyin.com/")
        original_url = page.url
        img_locator = page.get_by_role("img", name="二维码")
        # 获取 src 属性值
        src = await img_locator.get_attribute("src")
        print("✅ 图片地址:", src)
        status_queue.put(src)
        # 监听页面的 'framenavigated' 事件，只关注主框架的变化
        page.on('framenavigated',
                lambda frame: asyncio.create_task(on_url_change()) if frame == page.main_frame else None)
        try:
            # 等待 URL 变化或超时
            await asyncio.wait_for(url_changed_event.wait(), timeout=200)  # 最多等待 200 秒
            print("监听页面跳转成功")
        except asyncio.TimeoutError:
            print("监听页面跳转超时")
            await page.close()
            await context.close()
            await browser.close()
            status_queue.put("500")
            return None
        uuid_v1 = uuid.uuid1()
        print(f"UUID v1: {uuid_v1}")
        # 确保cookiesFile目录存在
        cookies_dir = Path(BASE_DIR / "cookiesFile")
        cookies_dir.mkdir(exist_ok=True)
        await context.storage_state(path=cookies_dir / f"{uuid_v1}.json")
        result = await check_cookie(3, f"{uuid_v1}.json")
        if not result:
            status_queue.put("500")
            await page.close()
            await context.close()
            await browser.close()
            return None
        await page.close()
        await context.close()
        await browser.close()
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                                INSERT INTO user_info (type, filePath, userName, status)
                                VALUES (?, ?, ?, ?)
                                ''', (3, f"{uuid_v1}.json", id, 1))
            conn.commit()
            print("✅ 用户状态已记录")
        status_queue.put("200")


# 视频号登录
async def get_tencent_cookie(id,status_queue):
    url_changed_event = asyncio.Event()
    async def on_url_change():
        # 检查是否是主框架的变化
        if page.url != original_url:
            url_changed_event.set()

    async with async_playwright() as playwright:
        options = {
            'args': [
                '--lang en-GB'
            ],
            'headless': LOCAL_CHROME_HEADLESS,  # Set headless option here
        }
        # Make sure to run headed.
        browser = await playwright.chromium.launch(**options)
        # Setup context however you like.
        context = await browser.new_context()  # Pass any options
        # Pause the page, and start recording manually.
        context = await set_init_script(context)
        page = await context.new_page()
        await page.goto("https://channels.weixin.qq.com")
        original_url = page.url

        # 监听页面的 'framenavigated' 事件，只关注主框架的变化
        page.on('framenavigated',
                lambda frame: asyncio.create_task(on_url_change()) if frame == page.main_frame else None)

        # 等待 iframe 出现（最多等 60 秒）
        iframe_locator = page.frame_locator("iframe").first

        # 获取 iframe 中的第一个 img 元素
        img_locator = iframe_locator.get_by_role("img").first

        # 获取 src 属性值
        src = await img_locator.get_attribute("src")
        print("✅ 图片地址:", src)
        status_queue.put(src)

        try:
            # 等待 URL 变化或超时
            await asyncio.wait_for(url_changed_event.wait(), timeout=200)  # 最多等待 200 秒
            print("监听页面跳转成功")
        except asyncio.TimeoutError:
            status_queue.put("500")
            print("监听页面跳转超时")
            await page.close()
            await context.close()
            await browser.close()
            return None
        uuid_v1 = uuid.uuid1()
        print(f"UUID v1: {uuid_v1}")
        # 确保cookiesFile目录存在
        cookies_dir = Path(BASE_DIR / "cookiesFile")
        cookies_dir.mkdir(exist_ok=True)
        await context.storage_state(path=cookies_dir / f"{uuid_v1}.json")
        result = await check_cookie(2,f"{uuid_v1}.json")
        if not result:
            status_queue.put("500")
            await page.close()
            await context.close()
            await browser.close()
            return None
        await page.close()
        await context.close()
        await browser.close()

        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                                INSERT INTO user_info (type, filePath, userName, status)
                                VALUES (?, ?, ?, ?)
                                ''', (2, f"{uuid_v1}.json", id, 1))
            conn.commit()
            print("✅ 用户状态已记录")
        status_queue.put("200")

# 快手登录
async def get_ks_cookie(id,status_queue):
    url_changed_event = asyncio.Event()
    async def on_url_change():
        # 检查是否是主框架的变化
        if page.url != original_url:
            url_changed_event.set()
    async with async_playwright() as playwright:
        options = {
            'args': [
                '--lang en-GB'
            ],
            'headless': LOCAL_CHROME_HEADLESS,  # Set headless option here
        }
        # Make sure to run headed.
        browser = await playwright.chromium.launch(**options)
        # Setup context however you like.
        context = await browser.new_context()  # Pass any options
        context = await set_init_script(context)
        # Pause the page, and start recording manually.
        page = await context.new_page()
        await page.goto("https://cp.kuaishou.com")

        # 定位并点击“立即登录”按钮（类型为 link）
        await page.get_by_role("link", name="立即登录").click()
        await page.get_by_text("扫码登录").click()
        img_locator = page.get_by_role("img", name="qrcode")
        # 获取 src 属性值
        src = await img_locator.get_attribute("src")
        original_url = page.url
        print("✅ 图片地址:", src)
        status_queue.put(src)
        # 监听页面的 'framenavigated' 事件，只关注主框架的变化
        page.on('framenavigated',
                lambda frame: asyncio.create_task(on_url_change()) if frame == page.main_frame else None)

        try:
            # 等待 URL 变化或超时
            await asyncio.wait_for(url_changed_event.wait(), timeout=200)  # 最多等待 200 秒
            print("监听页面跳转成功")
        except asyncio.TimeoutError:
            status_queue.put("500")
            print("监听页面跳转超时")
            await page.close()
            await context.close()
            await browser.close()
            return None
        uuid_v1 = uuid.uuid1()
        print(f"UUID v1: {uuid_v1}")
        # 确保cookiesFile目录存在
        cookies_dir = Path(BASE_DIR / "cookiesFile")
        cookies_dir.mkdir(exist_ok=True)
        await context.storage_state(path=cookies_dir / f"{uuid_v1}.json")
        result = await check_cookie(4, f"{uuid_v1}.json")
        if not result:
            status_queue.put("500")
            await page.close()
            await context.close()
            await browser.close()
            return None
        await page.close()
        await context.close()
        await browser.close()

        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                                        INSERT INTO user_info (type, filePath, userName, status)
                                        VALUES (?, ?, ?, ?)
                                        ''', (4, f"{uuid_v1}.json", id, 1))
            conn.commit()
            print("✅ 用户状态已记录")
        status_queue.put("200")

# 小红书登录
async def xiaohongshu_cookie_gen(id, status_queue):
    """
    小红书登录函数，支持实时日志输出
    """
    url_changed_event = asyncio.Event()
    login_success = False
    uuid_v1 = None
    temp_cookie_path = None

    def send_log(message):
        """发送日志消息到前端"""
        log_msg = f"status:[小红书登录] {message}"
        status_queue.put(log_msg)
        print(f"[小红书登录] {message}", flush=True)

    async def on_url_change():
        # 检查是否是主框架的变化
        if page.url != original_url:
            url_changed_event.set()
            send_log(f"检测到URL变化: {original_url} -> {page.url}")

    async with async_playwright() as playwright:
        try:
            send_log("开始启动浏览器...")
            options = {
                'args': [
                    '--lang en-GB'
                ],
                'headless': LOCAL_CHROME_HEADLESS,
            }
            browser = await playwright.chromium.launch(**options)
            context = await browser.new_context()
            context = await set_init_script(context)
            page = await context.new_page()
            
            send_log("正在访问小红书创作者中心...")
            await page.goto("https://creator.xiaohongshu.com/", timeout=60000)
            send_log("页面加载完成，正在查找登录按钮...")
            
            # 等待登录按钮出现
            try:
                await page.locator('img.css-wemwzq').wait_for(state='visible', timeout=10000)
                send_log("找到登录按钮，正在点击...")
                await page.locator('img.css-wemwzq').click()
                await asyncio.sleep(2)  # 等待二维码加载
            except Exception as e:
                send_log(f"查找或点击登录按钮失败: {str(e)}")
                # 尝试其他方式查找登录入口
                try:
                    send_log("尝试其他方式查找登录入口...")
                    login_links = page.locator('text=登录').or_(page.locator('text=扫码登录'))
                    await login_links.first.wait_for(state='visible', timeout=5000)
                    await login_links.first.click()
                    await asyncio.sleep(2)
                except Exception as e2:
                    send_log(f"查找登录入口失败: {str(e2)}")
                    status_queue.put("500")
                    await page.close()
                    await context.close()
                    await browser.close()
                    return None

            # 查找二维码图片
            send_log("正在查找二维码...")
            try:
                img_locator = page.get_by_role("img").nth(2)
                await img_locator.wait_for(state='visible', timeout=10000)
                src = await img_locator.get_attribute("src")
                if src:
                    send_log("二维码已生成，请使用小红书APP扫码")
                    status_queue.put(src)
                    original_url = page.url
                    send_log(f"当前页面URL: {original_url}")
                else:
                    send_log("警告: 二维码src为空")
                    status_queue.put("500")
                    await page.close()
                    await context.close()
                    await browser.close()
                    return None
            except Exception as e:
                send_log(f"查找二维码失败: {str(e)}")
                status_queue.put("500")
                await page.close()
                await context.close()
                await browser.close()
                return None

            # 创建临时cookie文件路径
            uuid_v1 = uuid.uuid1()
            cookies_dir = Path(BASE_DIR / "cookiesFile")
            cookies_dir.mkdir(exist_ok=True)
            temp_cookie_path = cookies_dir / f"temp_{uuid_v1}.json"
            send_log(f"创建临时Cookie文件: {temp_cookie_path.name}")

            # 监听页面的 'framenavigated' 事件
            page.on('framenavigated',
                    lambda frame: asyncio.create_task(on_url_change()) if frame == page.main_frame else None)

            # 开始监控登录状态
            send_log("开始监控登录状态，请扫码并确认登录...")
            start_time = time.time()
            check_interval = 5  # 每5秒检查一次
            max_wait_time = 200  # 最多等待200秒
            
            while not login_success:
                current_time = time.time()
                elapsed_time = current_time - start_time
                
                # 检查超时
                if elapsed_time > max_wait_time:
                    send_log(f"登录超时（已等待 {int(elapsed_time)} 秒），请重新尝试")
                    status_queue.put("500")
                    await page.close()
                    await context.close()
                    await browser.close()
                    return None

                # 检查URL是否变化
                if url_changed_event.is_set():
                    send_log("检测到URL变化，可能已登录成功")
                    current_url = page.url
                    send_log(f"新URL: {current_url}")
                    if "creator.xiaohongshu.com" in current_url and "creator.xiaohongshu.com/" != current_url:
                        send_log("URL已跳转，正在验证Cookie...")
                        login_success = True
                        break

                # 检查二维码是否消失（表示可能已扫码）
                try:
                    is_visible = await img_locator.is_visible(timeout=1000)
                    if not is_visible:
                        send_log("二维码已消失，可能已扫码成功，正在验证Cookie...")
                        # 等待一下，让页面完全加载
                        await asyncio.sleep(2)
                        login_success = True
                        break
                except:
                    # 二维码元素不存在，可能已登录
                    send_log("二维码元素已不存在，可能已登录成功")
                    await asyncio.sleep(2)
                    login_success = True
                    break

                # 定期检查Cookie（每5秒）
                if int(elapsed_time) % check_interval == 0 and int(elapsed_time) > 0:
                    send_log(f"定期检查Cookie（已等待 {int(elapsed_time)} 秒）...")
                    try:
                        # 保存当前Cookie状态
                        await context.storage_state(path=str(temp_cookie_path))
                        
                        # 验证Cookie是否有效
                        result = await check_cookie(1, temp_cookie_path.name)
                        if result:
                            send_log("Cookie验证成功！登录已完成")
                            login_success = True
                            break
                        else:
                            send_log("Cookie验证失败，继续等待...")
                    except Exception as e:
                        send_log(f"检查Cookie时出错: {str(e)}")

                # 等待一段时间再检查
                await asyncio.sleep(1)

            # 登录成功，保存Cookie
            if login_success:
                send_log("登录成功，正在保存Cookie...")
                try:
                    # 最终保存Cookie
                    final_cookie_path = cookies_dir / f"{uuid_v1}.json"
                    await context.storage_state(path=str(final_cookie_path))
                    send_log(f"Cookie已保存到: {final_cookie_path.name}")
                    
                    # 验证Cookie
                    result = await check_cookie(1, f"{uuid_v1}.json")
                    if result:
                        send_log("Cookie验证通过")
                        
                        # 保存到数据库
                        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
                            cursor = conn.cursor()
                            cursor.execute('''
                                           INSERT INTO user_info (type, filePath, userName, status)
                                           VALUES (?, ?, ?, ?)
                                           ''', (1, f"{uuid_v1}.json", id, 1))
                            conn.commit()
                            send_log("账号信息已保存到数据库")
                        
                        send_log("登录流程完成！")
                        status_queue.put("200")
                    else:
                        send_log("Cookie验证失败，登录可能未完全成功")
                        status_queue.put("500")
                except Exception as e:
                    send_log(f"保存Cookie时出错: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    status_queue.put("500")
            else:
                send_log("登录未成功")
                status_queue.put("500")

        except Exception as e:
            send_log(f"登录过程发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
            status_queue.put("500")
        finally:
            try:
                await page.close()
                await context.close()
                await browser.close()
                send_log("浏览器已关闭")
            except:
                pass

# a = asyncio.run(xiaohongshu_cookie_gen(4,None))
# print(a)
