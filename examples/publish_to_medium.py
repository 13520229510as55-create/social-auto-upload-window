#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Medium 发布示例
演示如何使用 Medium 自动化发布脚本
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from uploader.medium_uploader import post_article_to_medium, medium_setup
from conf import BASE_DIR
from datetime import datetime, timedelta


async def example_immediate_publish():
    """示例：立即发布文章"""
    print("=" * 60)
    print("示例1: 立即发布文章")
    print("=" * 60)
    
    account_file = BASE_DIR / "cookiesFile" / "medium_account.json"
    
    # 确保账号已设置
    await medium_setup(str(account_file), handle=True)
    
    # 发布文章
    await post_article_to_medium(
        title="My First Automated Medium Article",
        content="""
        <h2>Introduction</h2>
        <p>This is my first article published via automation.</p>
        <p>The automation script makes it easy to publish content to Medium.</p>
        
        <h2>Features</h2>
        <ul>
            <li>Automated publishing</li>
            <li>Tag management</li>
            <li>HTML content support</li>
        </ul>
        
        <h2>Conclusion</h2>
        <p>Thank you for reading!</p>
        """,
        tags=["automation", "python", "medium"],
        account_file=str(account_file),
        subtitle="A subtitle for the article",
        publish_status="public"
    )
    
    print("✅ 文章已发布！")


async def example_scheduled_publish():
    """示例：定时发布文章"""
    print("=" * 60)
    print("示例2: 定时发布文章")
    print("=" * 60)
    
    account_file = BASE_DIR / "cookiesFile" / "medium_account.json"
    
    # 设置明天下午3点发布
    publish_time = datetime.now() + timedelta(days=1)
    publish_time = publish_time.replace(hour=15, minute=0, second=0, microsecond=0)
    
    print(f"定时发布时间: {publish_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    await post_article_to_medium(
        title="Scheduled Article - Tomorrow at 3 PM",
        content="""
        <h2>Scheduled Publishing</h2>
        <p>This article is scheduled to be published tomorrow at 3 PM.</p>
        <p>The automation script supports scheduled publishing.</p>
        """,
        tags=["scheduled", "automation"],
        account_file=str(account_file),
        publish_date=publish_time
    )
    
    print(f"✅ 文章已设置为定时发布: {publish_time}")


async def example_unlisted_publish():
    """示例：发布未列出的文章"""
    print("=" * 60)
    print("示例3: 发布未列出的文章")
    print("=" * 60)
    
    account_file = BASE_DIR / "cookiesFile" / "medium_account.json"
    
    await post_article_to_medium(
        title="Unlisted Article",
        content="""
        <h2>Unlisted Article</h2>
        <p>This article is published as unlisted.</p>
        <p>It won't appear in your public profile but can be accessed via direct link.</p>
        """,
        tags=["unlisted", "private"],
        account_file=str(account_file),
        publish_status="unlisted"
    )
    
    print("✅ 未列出文章已发布！")


async def example_with_canonical_url():
    """示例：发布带规范URL的文章（用于SEO）"""
    print("=" * 60)
    print("示例4: 发布带规范URL的文章")
    print("=" * 60)
    
    account_file = BASE_DIR / "cookiesFile" / "medium_account.json"
    
    await post_article_to_medium(
        title="Article with Canonical URL",
        content="""
        <h2>Canonical URL</h2>
        <p>This article includes a canonical URL for SEO purposes.</p>
        <p>The canonical URL points to the original source.</p>
        """,
        tags=["seo", "canonical"],
        account_file=str(account_file),
        canonical_url="https://example.com/original-post",
        publish_status="public"
    )
    
    print("✅ 带规范URL的文章已发布！")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        example_name = sys.argv[1]
        if example_name == "1":
            asyncio.run(example_immediate_publish())
        elif example_name == "2":
            asyncio.run(example_scheduled_publish())
        elif example_name == "3":
            asyncio.run(example_unlisted_publish())
        elif example_name == "4":
            asyncio.run(example_with_canonical_url())
        else:
            print("用法: python publish_to_medium.py [1|2|3|4]")
            print("  1: 立即发布")
            print("  2: 定时发布")
            print("  3: 未列出发布")
            print("  4: 带规范URL发布")
    else:
        # 运行所有示例
        print("运行所有示例...")
        asyncio.run(example_immediate_publish())
        print("\n")
        # asyncio.run(example_scheduled_publish())  # 取消注释以测试定时发布
        # asyncio.run(example_unlisted_publish())  # 取消注释以测试未列出发布
        # asyncio.run(example_with_canonical_url())  # 取消注释以测试规范URL

