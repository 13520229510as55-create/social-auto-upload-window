#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
调试脚本：检查页面状态并截图
"""
import sys
import os
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

# 添加项目路径到sys.path
BASE_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(BASE_DIR))

try:
    from conf import LOCAL_CHROME_PATH, LOCAL_CHROME_HEADLESS
except:
    LOCAL_CHROME_PATH = None
    LOCAL_CHROME_HEADLESS = True

try:
    from tools.set_init_script import set_init_script
except:
    async def set_init_script(context):
        return context

async def debug_page():
    """调试页面状态"""
    
    print("=" * 60)
    print("开始调试页面状态")
    print("=" * 60)
    
    account_file = BASE_DIR / "cookiesFile" / "38fa9e5a-e0c2-11f0-8f26-cea02fcca853.json"
    
    if not account_file.exists():
        print(f"[ERROR] Cookie文件不存在: {account_file}")
        return
    
    print(f"\n使用Cookie文件: {account_file}")
    print("启动浏览器...")
    
    async with async_playwright() as playwright:
        # 使用有头浏览器，可以看到页面
        launch_params = {"headless": False}
        if LOCAL_CHROME_PATH:
            launch_params["executable_path"] = LOCAL_CHROME_PATH
        
        browser = await playwright.chromium.launch(**launch_params)
        context = await browser.new_context(storage_state=str(account_file))
        context = await set_init_script(context)
        
        page = await context.new_page()
        
        # 访问页面
        print("\n访问页面: https://channels.weixin.qq.com/platform/post/create")
        await page.goto("https://channels.weixin.qq.com/platform/post/create")
        
        # 等待一段时间
        await asyncio.sleep(3)
        
        # 检查URL
        current_url = page.url
        print(f"\n当前URL: {current_url}")
        
        # 检查登录页特征
        login_indicator = await page.query_selector('div.title-name:has-text("微信小店")')
        print(f"登录页特征（微信小店）: {'存在' if login_indicator else '不存在'}")
        
        # 检查上传区域（用户提供的元素）
        upload_content = await page.query_selector('div.upload-content')
        if upload_content:
            is_visible = await upload_content.is_visible()
            print(f"\n上传区域 (div.upload-content):")
            print(f"  - 存在: True")
            print(f"  - 可见: {is_visible}")
            
            # 获取上传提示文本
            upload_tip = await upload_content.query_selector('div.upload-tip span')
            if upload_tip:
                tip_text = await upload_tip.inner_text()
                print(f"  - 提示文本: {tip_text}")
        else:
            print("\n上传区域 (div.upload-content): 不存在")
        
        # 检查文件输入框（可能在upload-content内部或外部）
        file_input = await page.query_selector('input[type="file"]')
        if file_input:
            is_visible = await file_input.is_visible()
            is_hidden = await file_input.is_hidden()
            print(f"\n文件输入框 (input[type='file']):")
            print(f"  - 存在: True")
            print(f"  - 可见: {is_visible}")
            print(f"  - 隐藏: {is_hidden}")
            
            # 获取元素的样式
            display = await file_input.evaluate('el => window.getComputedStyle(el).display')
            visibility = await file_input.evaluate('el => window.getComputedStyle(el).visibility')
            opacity = await file_input.evaluate('el => window.getComputedStyle(el).opacity')
            print(f"  - display: {display}")
            print(f"  - visibility: {visibility}")
            print(f"  - opacity: {opacity}")
            
            # 检查文件输入框是否在upload-content内部
            parent = await file_input.evaluate_handle('el => el.parentElement')
            if parent:
                parent_class = await parent.evaluate('el => el.className')
                print(f"  - 父元素class: {parent_class}")
        else:
            print("\n文件输入框 (input[type='file']): 不存在")
        
        # 查找所有文件上传相关的元素
        print("\n查找所有文件上传相关元素...")
        upload_buttons = await page.query_selector_all('button:has-text("上传"), button:has-text("选择文件"), div:has-text("上传视频"), div:has-text("选择视频"), div.upload-content')
        print(f"找到 {len(upload_buttons)} 个上传相关元素")
        for i, btn in enumerate(upload_buttons):
            try:
                text = await btn.inner_text()
                is_visible = await btn.is_visible()
                tag_name = await btn.evaluate('el => el.tagName')
                class_name = await btn.evaluate('el => el.className')
                print(f"  [{i+1}] 标签: {tag_name}, class: {class_name}, 文本: {text[:50] if text else 'N/A'}, 可见: {is_visible}")
            except:
                print(f"  [{i+1}] 无法获取信息")
        
        # 尝试点击上传区域，看看会发生什么
        if upload_content:
            print("\n尝试点击上传区域...")
            try:
                await upload_content.click()
                await asyncio.sleep(2)
                print("点击成功，等待2秒后检查文件输入框状态...")
                
                # 再次检查文件输入框
                file_input_after = await page.query_selector('input[type="file"]')
                if file_input_after:
                    is_visible_after = await file_input_after.is_visible()
                    print(f"点击后文件输入框可见: {is_visible_after}")
            except Exception as e:
                print(f"点击失败: {str(e)}")
        
        # 截图
        screenshot_path = BASE_DIR / "debug_page.png"
        await page.screenshot(path=str(screenshot_path), full_page=True)
        print(f"\n页面截图已保存: {screenshot_path}")
        
        # 获取页面HTML（部分）
        print("\n获取页面HTML...")
        html_content = await page.content()
        html_file = BASE_DIR / "debug_page.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"页面HTML已保存: {html_file}")
        
        print("\n\n调试完成！浏览器将保持打开状态60秒，请查看页面...")
        print("按Ctrl+C可以提前结束")
        await asyncio.sleep(60)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_page())

