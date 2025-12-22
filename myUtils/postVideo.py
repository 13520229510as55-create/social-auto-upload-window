import asyncio
from pathlib import Path

from conf import BASE_DIR
from uploader.douyin_uploader.main import DouYinVideo
from uploader.ks_uploader.main import KSVideo
from uploader.tencent_uploader.main import TencentVideo
from uploader.xiaohongshu_uploader.main import XiaoHongShuVideo
from utils.constant import TencentZoneTypes
from utils.files_times import generate_schedule_time_next_day


def post_video_tencent(title,files,tags,account_file,category=TencentZoneTypes.LIFESTYLE.value,enableTimer=False,videos_per_day = 1, daily_times=None,start_days = 0, is_draft=False):
    # 生成文件的完整路径
    account_file = [Path(BASE_DIR / "cookiesFile" / file) for file in account_file]
    files = [Path(BASE_DIR / "videoFile" / file) for file in files]
    if enableTimer:
        publish_datetimes = generate_schedule_time_next_day(len(files), videos_per_day, daily_times,start_days)
    else:
        publish_datetimes = [0 for i in range(len(files))]
    for index, file in enumerate(files):
        for cookie in account_file:
            print(f"文件路径{str(file)}")
            # 打印视频文件名、标题和 hashtag
            print(f"视频文件名：{file}")
            print(f"标题：{title}")
            print(f"Hashtag：{tags}")
            app = TencentVideo(title, str(file), tags, publish_datetimes[index], cookie, category, is_draft)
            asyncio.run(app.main(), debug=False)


def post_video_DouYin(title,files,tags,account_file,category=TencentZoneTypes.LIFESTYLE.value,enableTimer=False,videos_per_day = 1, daily_times=None,start_days = 0,
                      thumbnail_path = '',
                      productLink = '', productTitle = ''):
    # 生成文件的完整路径
    account_file = [Path(BASE_DIR / "cookiesFile" / file) for file in account_file]
    files = [Path(BASE_DIR / "videoFile" / file) for file in files]
    if enableTimer:
        publish_datetimes = generate_schedule_time_next_day(len(files), videos_per_day, daily_times,start_days)
    else:
        publish_datetimes = [0 for i in range(len(files))]
    for index, file in enumerate(files):
        for cookie in account_file:
            print(f"文件路径{str(file)}")
            # 打印视频文件名、标题和 hashtag
            print(f"视频文件名：{file}")
            print(f"标题：{title}")
            print(f"Hashtag：{tags}")
            app = DouYinVideo(title, str(file), tags, publish_datetimes[index], cookie, thumbnail_path, productLink, productTitle)
            asyncio.run(app.main(), debug=False)


def post_video_ks(title,files,tags,account_file,category=TencentZoneTypes.LIFESTYLE.value,enableTimer=False,videos_per_day = 1, daily_times=None,start_days = 0):
    # 生成文件的完整路径
    account_file = [Path(BASE_DIR / "cookiesFile" / file) for file in account_file]
    files = [Path(BASE_DIR / "videoFile" / file) for file in files]
    if enableTimer:
        publish_datetimes = generate_schedule_time_next_day(len(files), videos_per_day, daily_times,start_days)
    else:
        publish_datetimes = [0 for i in range(len(files))]
    for index, file in enumerate(files):
        for cookie in account_file:
            print(f"文件路径{str(file)}")
            # 打印视频文件名、标题和 hashtag
            print(f"视频文件名：{file}")
            print(f"标题：{title}")
            print(f"Hashtag：{tags}")
            app = KSVideo(title, str(file), tags, publish_datetimes[index], cookie)
            asyncio.run(app.main(), debug=False)

def post_video_xhs(title,files,tags,account_file,category=TencentZoneTypes.LIFESTYLE.value,enableTimer=False,videos_per_day = 1, daily_times=None,start_days = 0, content=None):
    """
    发布小红书视频
    Args:
        title: 视频标题
        files: 视频文件列表
        tags: 标签列表
        account_file: 账号文件列表
        category: 分类（兼容参数，小红书视频发布不使用）
        enableTimer: 是否启用定时发布
        videos_per_day: 每天发布视频数
        daily_times: 每日发布时间列表
        start_days: 开始天数
        content: 视频描述内容（可选，如果有值会合并到标题中）
    """
    # 生成文件的完整路径
    account_file = [Path(BASE_DIR / "cookiesFile" / file) for file in account_file]
    files = [Path(BASE_DIR / "videoFile" / file) for file in files]
    file_num = len(files)
    if enableTimer:
        publish_datetimes = generate_schedule_time_next_day(file_num, videos_per_day, daily_times,start_days)
    else:
        publish_datetimes = 0
    
    # 如果有 content 参数且不为空，将其合并到标题中（保持兼容性）
    final_title = title
    if content and content.strip():
        # 将 content 追加到标题后面，用换行符或空格分隔
        final_title = f"{title}\n{content}" if len(title) + len(content) < 1000 else title
        print(f"📝 检测到 content 参数，已合并到标题中")
    
    for index, file in enumerate(files):
        for cookie in account_file:
            # 打印视频文件名、标题和 hashtag
            print(f"视频文件名：{file}")
            print(f"标题：{final_title}")
            print(f"Hashtag：{tags}")
            app = XiaoHongShuVideo(final_title, file, tags, publish_datetimes, cookie)
            asyncio.run(app.main(), debug=False)


def post_image_text_xhs(
    title,
    content,
    image_files,
    tags,
    account_file,
    enableTimer=False,
    images_per_day=1,
    daily_times=None,
    start_days=0,
):
    """
    小红书图文发布占位函数。

    注意：
    - 当前本地仓库缺少完整的图文发布实现代码（参考文档 `URL图片支持修复说明.md`）。
    - 此函数仅为保证后端能够正常启动而提供占位实现。
    - 如果需要在本地环境使用小红书图文发布，请根据服务器上的实现或文档补全此函数逻辑。
    """
    raise NotImplementedError(
        "post_image_text_xhs 尚未在本地实现，请参考 `URL图片支持修复说明.md` 与服务器版本的 myUtils/postVideo.py。"
    )


# post_video("333",["demo.mp4"],"d","d")
# post_video_DouYin("333",["demo.mp4"],"d","d")