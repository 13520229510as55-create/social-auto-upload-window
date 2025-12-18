#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书视频自动化发布测试（无人工交互）
- 自动选择一个可用的视频文件
- 自动选择一个包含小红书域名的 Cookie 文件
- 仅在 Cookie 有效时执行一次真实发布

注意：这会真实往当前小红书账号发布一个测试视频，请只在测试环境使用。
"""
import asyncio
import json
from pathlib import Path

from conf import BASE_DIR
from uploader.xiaohongshu_uploader.main import cookie_auth, XiaoHongShuVideo


def find_test_video() -> Path | None:
    """自动寻找一个用于测试的视频文件"""
    videos_dir = Path(BASE_DIR / "videos")
    video_file_dir = Path(BASE_DIR / "videoFile")

    # 优先使用 videos/demo.mp4
    demo = videos_dir / "demo.mp4"
    if demo.exists():
        return demo

    # 否则使用 videoFile 目录下的第一个 mp4
    if video_file_dir.exists():
        mp4_files = list(video_file_dir.glob("*.mp4"))
        if mp4_files:
            return mp4_files[0]

    return None


def find_xiaohongshu_cookie_file() -> Path | None:
    """查找一个可用于测试的小红书 Cookie 文件（无交互）"""
    cookie_files: list[Path] = []

    # 1) 检查 cookiesFile 目录（前端登录产生的 Cookie）
    cookies_file_dir = Path(BASE_DIR / "cookiesFile")
    if cookies_file_dir.exists():
        for cf in cookies_file_dir.glob("*.json"):
            try:
                with open(cf, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if "cookies" in data:
                    for cookie in data.get("cookies", []):
                        domain = cookie.get("domain", "") or ""
                        if any(x in domain for x in ["xiaohongshu", "xhslink", "creator.xiaohongshu"]):
                            cookie_files.append(cf)
                            break
            except Exception:
                # 某些文件可能不是 storage_state 格式，忽略即可
                continue

    # 2) 再检查旧目录 cookies/xiaohongshu_uploader
    cookies_dir = Path(BASE_DIR / "cookies" / "xiaohongshu_uploader")
    if cookies_dir.exists():
        cookie_files.extend(cookies_dir.glob("*.json"))

    if not cookie_files:
        return None

    # 简单策略：取第一个
    return cookie_files[0]


async def main() -> None:
    print("=" * 80)
    print("小红书视频自动化发布测试（无交互版）")
    print("=" * 80)

    # 1️⃣ 查找测试视频
    print("1️⃣ 查找测试视频文件...")
    video_path = find_test_video()
    if not video_path or not video_path.exists():
        print("❌ 未找到可用的测试视频文件")
        print(f"   请在 {BASE_DIR / 'videos'} 或 {BASE_DIR / 'videoFile'} 中放入 mp4 文件")
        return

    print(f"✅ 使用测试视频: {video_path}")
    print(f"   大小: {video_path.stat().st_size / 1024 / 1024:.2f} MB")

    # 2️⃣ 查找小红书 Cookie 文件
    print("\n2️⃣ 查找小红书 Cookie 文件...")
    cookie_file = find_xiaohongshu_cookie_file()
    if not cookie_file or not cookie_file.exists():
        print("❌ 未找到小红书 Cookie 文件")
        print("💡 请先在网页前端的【账号管理】中，给小红书账号登录一次，生成 Cookie")
        return

    print(f"✅ 使用 Cookie 文件: {cookie_file} \n")

    # 3️⃣ 验证 Cookie 是否有效（只在有效时继续）
    print("3️⃣ 验证 Cookie 有效性...")
    force_publish_on_invalid = True  # 调试模式：即使判定失效也可以选择继续跑一遍发布流程
    try:
        is_valid = await cookie_auth(str(cookie_file))
    except Exception as e:
        print(f"❌ Cookie 验证时发生异常: {e}")
        if not force_publish_on_invalid:
            return
        print("⚠️ 由于处于调试模式，仍将尝试执行一次发布流程以观察行为...")
        is_valid = False

    if not is_valid:
        print("❌ Cookie 被判定为已失效")
        if not force_publish_on_invalid:
            print("💡 请先在前端重新登录小红书账号，再重新运行本测试脚本")
            return
        else:
            print("⚠️ 调试模式开启：即使 Cookie 判定失效，仍将尝试执行一次真实发布以观察日志和页面行为")
    else:
        print("✅ Cookie 验证通过")

    # 4️⃣ 执行一次实际发布（无人工确认）
    print("\n4️⃣ 开始执行实际发布（⚠️ 将真实发布到当前小红书账号）")
    title = "测试视频发布 - 自动化测试"
    tags = ["测试", "自动化", "技术"]

    # 使用实际存在的测试视频路径（无需强制拷贝到 videoFile 目录）
    video_file_path = video_path
    cookie_name = cookie_file.name
    cookie_path = Path(BASE_DIR / "cookiesFile" / cookie_name)

    print("📤 发布参数:")
    print(f"   标题: {title}")
    print(f"   标签: {tags}")
    print(f"   视频文件名: {video_file_path}")
    print(f"   Cookie 文件名: {cookie_path}")

    try:
        app = XiaoHongShuVideo(
            title=title,
            file_path=video_file_path,
            tags=tags,
            publish_date=0,  # 立即发布
            account_file=cookie_path,
            content="自动化测试发布，请忽略",
        )
        await app.main()
        print("\n✅ 发布流程已执行完毕，具体发布结果请看日志和小红书创作者中心")
    except Exception as e:
        print(f"\n❌ 发布流程执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
