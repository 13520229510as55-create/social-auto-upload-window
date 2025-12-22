# -*- coding: utf-8 -*-
"""
MediaCrawler 管理后台 API 服务
提供配置管理、任务管理、登录等功能
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 尝试导入MediaCrawler模块，如果失败则使用mock
try:
    # 导入项目主模块
    import importlib.util
    main_module_path = project_root / "main.py"
    if main_module_path.exists():
        spec = importlib.util.spec_from_file_location("mediacrawler_main", main_module_path)
        mediacrawler_main = importlib.util.module_from_spec(spec)
        try:
            # 切换到项目根目录，确保相对路径（如libs/）能正确解析
            original_cwd = os.getcwd()
            try:
                os.chdir(str(project_root))
                spec.loader.exec_module(mediacrawler_main)
                CrawlerFactory = mediacrawler_main.CrawlerFactory
                print(f"[main] ✓ MediaCrawler主模块导入成功，CrawlerFactory: {CrawlerFactory}")
            finally:
                os.chdir(original_cwd)
        except Exception as e:
            print(f"警告: MediaCrawler主模块导入失败: {e}")
            import traceback
            traceback.print_exc()
            CrawlerFactory = None
    else:
        CrawlerFactory = None
    
    import config
    try:
        from cmd_arg.arg import PlatformEnum, LoginTypeEnum, CrawlerTypeEnum
        print(f"[main] ✓ PlatformEnum等导入成功")
    except ImportError:
        PlatformEnum = LoginTypeEnum = CrawlerTypeEnum = None
    CRAWLER_AVAILABLE = True
    print(f"[main] ✓ CRAWLER_AVAILABLE = {CRAWLER_AVAILABLE}, CrawlerFactory是否为None: {CrawlerFactory is None if 'CrawlerFactory' in locals() else '未定义'}")
except ImportError as e:
    print(f"警告: MediaCrawler模块导入失败: {e}")
    print("API服务将以受限模式运行（部分功能不可用）")
    CrawlerFactory = None
    import config
    PlatformEnum = LoginTypeEnum = CrawlerTypeEnum = None
    CRAWLER_AVAILABLE = False
    CRAWLER_AVAILABLE = False
    # 创建mock对象
    class MockCrawlerFactory:
        @staticmethod
        def create_crawler(platform):
            raise Exception("MediaCrawler模块未正确导入，无法创建爬虫")
    CrawlerFactory = MockCrawlerFactory()
    # 创建简单的config对象
    class MockConfig:
        PLATFORM = "xhs"
        KEYWORDS = ""
        LOGIN_TYPE = "qrcode"
        CRAWLER_TYPE = "search"
        START_PAGE = 1
        CRAWLER_MAX_NOTES_COUNT = 15
        ENABLE_GET_COMMENTS = True
        CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES = 10
        ENABLE_GET_MEIDAS = False
        HEADLESS = False
        ENABLE_CDP_MODE = False  # 禁用CDP模式，使用标准模式
        CDP_HEADLESS = False  # CDP模式下的headless配置（如果启用CDP模式）
        SAVE_DATA_OPTION = "json"
        COOKIES = ""
        SORT_TYPE = "popularity_descending"
        XHS_SPECIFIED_NOTE_URL_LIST = []
        XHS_CREATOR_ID_LIST = []
    config = MockConfig()

app = FastAPI(title="MediaCrawler Admin API", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 存储运行中的任务
running_tasks: Dict[str, asyncio.Task] = {}
task_status: Dict[str, Dict] = {}


class PlatformConfig(BaseModel):
    """平台配置模型"""
    platform: str
    keywords: Union[str, List[str], None] = ""  # 支持字符串或数组格式
    login_type: str = "qrcode"
    crawler_type: str = "search"
    start_page: int = 1
    max_notes_count: int = 15
    enable_get_comments: bool = True
    max_comments_count: int = 10
    enable_get_medias: bool = False
    headless: bool = False
    save_data_option: str = "json"
    specified_urls: Optional[List[str]] = []
    creator_ids: Optional[List[str]] = []
    # 平台特定配置
    platform_specific: Optional[Dict] = {}
    # 强制重新登录标志
    force_relogin: bool = False
    
    @field_validator('keywords', mode='before')
    @classmethod
    def parse_keywords(cls, v):
        """解析keywords，支持字符串或数组格式"""
        if isinstance(v, list):
            return ",".join(v)
        elif isinstance(v, str):
            return v
        else:
            return ""


class TaskRequest(BaseModel):
    """任务请求模型"""
    platform: str
    config: PlatformConfig


class QRCodeResponse(BaseModel):
    """二维码响应模型"""
    qrcode_id: str
    qrcode_base64: str
    expires_in: int = 120


@app.get("/")
async def root():
    """根路径"""
    return {"message": "MediaCrawler Admin API", "version": "1.0.0"}


@app.get("/api/platforms")
async def get_platforms():
    """获取支持的平台列表"""
    platforms = [
        {"value": "xhs", "label": "小红书"},
        {"value": "dy", "label": "抖音"},
        {"value": "ks", "label": "快手"},
        {"value": "bili", "label": "B站"},
        {"value": "wb", "label": "微博"},
        {"value": "tieba", "label": "百度贴吧"},
        {"value": "zhihu", "label": "知乎"},
        {"value": "juejin", "label": "掘金"},
        {"value": "medium", "label": "Medium"},
    ]
    return {"platforms": platforms}


@app.get("/api/config/{platform}")
async def get_platform_config(platform: str):
    """获取平台配置"""
    try:
        # 读取配置文件
        config_file = project_root / "config" / f"{platform}_config.py"
        base_config_file = project_root / "config" / "base_config.py"
        
        # 这里应该读取实际的配置，简化处理
        config_data = {
            "platform": platform,
            "keywords": getattr(config, "KEYWORDS", ""),
            "login_type": getattr(config, "LOGIN_TYPE", "qrcode"),
            "crawler_type": getattr(config, "CRAWLER_TYPE", "search"),
            "start_page": getattr(config, "START_PAGE", 1),
            "max_notes_count": getattr(config, "CRAWLER_MAX_NOTES_COUNT", 15),
            "enable_get_comments": getattr(config, "ENABLE_GET_COMMENTS", True),
            "max_comments_count": getattr(config, "CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES", 10),
            "enable_get_medias": getattr(config, "ENABLE_GET_MEIDAS", False),
            "headless": getattr(config, "HEADLESS", False),
            "save_data_option": getattr(config, "SAVE_DATA_OPTION", "json"),
            "specified_urls": [],
            "creator_ids": [],
        }
        
        # 根据平台获取特定配置
        if platform == "xhs":
            config_data["specified_urls"] = getattr(config, "XHS_SPECIFIED_NOTE_URL_LIST", [])
            config_data["creator_ids"] = getattr(config, "XHS_CREATOR_ID_LIST", [])
            config_data["platform_specific"] = {
                "sort_type": getattr(config, "SORT_TYPE", "popularity_descending")
            }
        
        return config_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/config/{platform}")
async def save_platform_config(platform: str, config_data: PlatformConfig):
    """保存平台配置"""
    try:
        # 更新配置到config模块
        await save_platform_config_internal(platform, config_data)
        
        return {"message": "配置保存成功", "platform": platform}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


try:
    from login_service import login_service
    print("✓ 登录服务模块加载成功")
except ImportError as e:
    # 如果导入失败，创建一个简单的mock
    print(f"警告: 登录服务模块导入失败: {e}")
    class MockLoginService:
        async def get_qrcode(self, platform): 
            return {
                "qrcode_id": "", 
                "qrcode_base64": "", 
                "expires_in": 120,
                "error": "登录服务未正确加载，请检查依赖"
            }
        async def check_login_status(self, qrcode_id): return {"status": "pending"}
        async def has_valid_cookie(self, platform): return False
        async def load_cookie(self, platform): return None
    login_service = MockLoginService()

@app.post("/api/login/qrcode")
async def get_qrcode(platform: str = Query(..., description="平台名称"), force: bool = Query(False, description="是否强制重新登录")):
    """获取登录二维码
    Args:
        platform: 平台名称
        force: 是否强制重新登录（忽略已有cookie）
    """
    try:
        # 如果force=True，允许重新登录（忽略已有cookie）
        if not force:
            # 检查是否已有有效cookie
            has_cookie = await login_service.has_valid_cookie(platform)
            if has_cookie:
                return {
                    "has_cookie": True,
                    "message": "已有登录状态，无需重新登录。如需重新登录，请先清除cookie"
                }
        
        # 使用asyncio.wait_for设置超时时间为120秒（2分钟）
        import asyncio
        result = await asyncio.wait_for(
            login_service.get_qrcode(platform),
            timeout=120.0
        )
        return result
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="获取二维码超时，请稍后重试")
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"[get_qrcode] 错误详情: {error_detail}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/login/status/{qrcode_id}")
async def check_login_status(qrcode_id: str):
    """检查登录状态"""
    try:
        result = await login_service.check_login_status(qrcode_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/login/cookie/{platform}")
async def get_cookie(platform: str):
    """获取保存的cookie"""
    try:
        cookie = await login_service.load_cookie(platform)
        if cookie:
            return {
                "has_cookie": True,
                "cookie": cookie
            }
        return {
            "has_cookie": False,
            "message": "未找到保存的cookie"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/login/cookie/{platform}")
async def delete_cookie(platform: str):
    """删除保存的cookie"""
    try:
        success = await login_service.delete_cookie(platform)
        if success:
            return {
                "success": True,
                "message": "Cookie已删除"
            }
        return {
            "success": False,
            "message": "Cookie不存在或删除失败"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def save_platform_config_internal(platform: str, config_data: PlatformConfig):
    """内部保存配置函数"""
    config.PLATFORM = platform
    # 处理keywords，支持数组或字符串格式
    if isinstance(config_data.keywords, list):
        config.KEYWORDS = ",".join(config_data.keywords)
    else:
        config.KEYWORDS = config_data.keywords or ""
    config.LOGIN_TYPE = config_data.login_type
    config.CRAWLER_TYPE = config_data.crawler_type
    config.START_PAGE = config_data.start_page
    config.CRAWLER_MAX_NOTES_COUNT = config_data.max_notes_count
    config.ENABLE_GET_COMMENTS = config_data.enable_get_comments
    config.CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES = config_data.max_comments_count
    config.ENABLE_GET_MEIDAS = config_data.enable_get_medias
    config.HEADLESS = config_data.headless
    # 确保CDP模式被禁用，使用标准模式（这样HEADLESS配置才会生效）
    if hasattr(config, 'ENABLE_CDP_MODE'):
        config.ENABLE_CDP_MODE = False
    # 如果启用了CDP模式，也需要设置CDP_HEADLESS
    if hasattr(config, 'CDP_HEADLESS'):
        config.CDP_HEADLESS = config_data.headless
    config.SAVE_DATA_OPTION = config_data.save_data_option
    
    # 保存平台特定配置
    if platform == "xhs" and config_data.platform_specific:
        if "sort_type" in config_data.platform_specific:
            config.SORT_TYPE = config_data.platform_specific["sort_type"]
        if config_data.specified_urls:
            config.XHS_SPECIFIED_NOTE_URL_LIST = config_data.specified_urls
        if config_data.creator_ids:
            config.XHS_CREATOR_ID_LIST = config_data.creator_ids

@app.post("/api/tasks/start")
async def start_crawler_task(task_request: TaskRequest, background_tasks: BackgroundTasks):
    """启动爬虫任务"""
    try:
        task_id = f"{task_request.platform}_{int(asyncio.get_event_loop().time())}"
        
        # 启动爬虫任务
        async def run_crawler():
            try:
                if not CRAWLER_AVAILABLE:
                    raise Exception("MediaCrawler模块未正确导入，请检查依赖安装")
                
                if CrawlerFactory is None:
                    raise Exception("CrawlerFactory未初始化，MediaCrawler模块导入失败。请检查依赖：pip install -r requirements.txt")
                
                # 检查是否强制重新登录
                force_relogin = getattr(task_request.config, 'force_relogin', False)

                if force_relogin:
                    # 强制重新登录，跳过cookie检测，直接使用qrcode登录
                    print(f"[start_crawler_task] 用户选择强制重新登录，将使用qrcode登录方式")
                    task_request.config.login_type = 'qrcode'
                else:
                    # 自动检测cookie（原有逻辑）
                    # 先检查并加载cookie（如果有cookie，优先使用cookie登录）
                    has_cookie = False
                    cookie_value = None
                    try:
                        cookie = await login_service.load_cookie(task_request.platform)
                        if cookie:
                            cookie_value = cookie
                            has_cookie = True
                            print(f"[start_crawler_task] 检测到已保存的cookie，长度: {len(cookie)} 字符")
                    except Exception as e:
                        print(f"[start_crawler_task] 加载cookie失败: {e}")
                        pass  # 如果没有cookie，使用配置中的登录方式

                    # 更新配置（如果有cookie，覆盖登录类型为cookie）
                    if has_cookie:
                        # 如果有cookie，强制使用cookie登录
                        task_request.config.login_type = 'cookie'
                        print(f"[start_crawler_task] 已设置登录类型为cookie，将使用已保存的cookie")
                    else:
                        # 如果没有cookie，使用前端传过来的登录类型（或默认值qrcode）
                        print(f"[start_crawler_task] 未检测到cookie，将使用登录类型: {task_request.config.login_type}")
                
                await save_platform_config_internal(task_request.platform, task_request.config)
                
                # 在保存配置之后，确保COOKIES被正确设置（因为save_platform_config_internal不会覆盖COOKIES）
                if has_cookie and cookie_value:
                    config.COOKIES = cookie_value
                    print(f"[start_crawler_task] ✓ Cookie已设置到config.COOKIES，长度: {len(cookie_value)} 字符")
                    print(f"[start_crawler_task] Cookie前50字符: {cookie_value[:50]}...")
                else:
                    print(f"[start_crawler_task] ⚠️  未设置Cookie，config.COOKIES = '{config.COOKIES}'")
                
                # 打印关键配置信息，用于调试
                print(f"[start_crawler_task] 配置信息:")
                print(f"  - PLATFORM: {config.PLATFORM}")
                print(f"  - KEYWORDS: {config.KEYWORDS}")
                print(f"  - LOGIN_TYPE: {config.LOGIN_TYPE}")
                print(f"  - CRAWLER_TYPE: {config.CRAWLER_TYPE}")
                print(f"  - HEADLESS: {config.HEADLESS}")
                print(f"  - CRAWLER_MAX_NOTES_COUNT: {config.CRAWLER_MAX_NOTES_COUNT}")
                
                crawler = CrawlerFactory.create_crawler(platform=task_request.platform)
                task_status[task_id] = {
                    "status": "running",
                    "platform": task_request.platform,
                    "progress": 0,
                    "message": "任务启动中..."
                }
                # 切换到项目根目录执行爬虫，确保相对路径（如libs/）能正确解析
                original_cwd = os.getcwd()
                try:
                    os.chdir(str(project_root))
                    import sys
                    print(f"[start_crawler_task] 开始执行爬虫任务，平台: {task_request.platform}")
                    print(f"[start_crawler_task] 当前工作目录: {os.getcwd()}")
                    sys.stdout.flush()
                    # 配置日志实时输出
                    import logging
                    # 获取所有logger并设置实时输出
                    for handler in logging.root.handlers[:]:
                        if hasattr(handler, 'stream') and handler.stream:
                            handler.stream.flush()
                    await crawler.start()
                    print(f"[start_crawler_task] ✓ 爬虫任务执行完成")
                    sys.stdout.flush()
                finally:
                    os.chdir(original_cwd)
                task_status[task_id] = {
                    "status": "completed",
                    "platform": task_request.platform,
                    "progress": 100,
                    "message": "任务完成"
                }
            except Exception as e:
                import traceback
                error_detail = str(e)
                # 尝试获取更详细的错误信息
                if hasattr(e, '__cause__') and e.__cause__:
                    error_detail += f" | 原因: {str(e.__cause__)}"
                # 如果是RetryError，尝试获取原始错误
                if "RetryError" in str(type(e)):
                    if hasattr(e, 'last_attempt') and hasattr(e.last_attempt, 'exception'):
                        error_detail += f" | 原始错误: {str(e.last_attempt.exception)}"
                task_status[task_id] = {
                    "status": "failed",
                    "platform": task_request.platform,
                    "progress": 0,
                    "message": error_detail
                }
                print(f"[start_crawler_task] 任务执行失败: {error_detail}")
                import traceback
                print(f"[start_crawler_task] 错误堆栈:\n{traceback.format_exc()}")
        
        task = asyncio.create_task(run_crawler())
        running_tasks[task_id] = task
        
        return {
            "task_id": task_id,
            "status": "started",
            "message": "任务已启动"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tasks")
async def get_tasks():
    """获取任务列表"""
    return {
        "tasks": [
            {
                "task_id": task_id,
                **status
            }
            for task_id, status in task_status.items()
        ]
    }


@app.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str):
    """获取任务状态"""
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task_status[task_id]


@app.delete("/api/tasks/{task_id}")
async def stop_task(task_id: str):
    """停止任务"""
    if task_id in running_tasks:
        running_tasks[task_id].cancel()
        task_status[task_id]["status"] = "cancelled"
        return {"message": "任务已停止"}
    raise HTTPException(status_code=404, detail="任务不存在")


@app.get("/api/data/{platform}/comments/{note_id}")
async def get_note_comments(platform: str, note_id: str, page: int = 1, page_size: int = 20):
    """获取某个笔记的评论列表"""
    try:
        import json
        from datetime import datetime
        
        # 数据文件在 data/{platform}/json/ 目录下
        data_dir = project_root / "data" / platform / "json"
        print(f"[get_note_comments] platform={platform}, note_id={note_id}, data_dir={data_dir}")
        
        if not data_dir.exists():
            return {
                "comments": [],
                "total": 0,
                "page": page,
                "page_size": page_size
            }
        
        # 读取所有 comments 相关的 JSON 文件
        json_files = sorted(data_dir.glob("*comments*.json"), reverse=True)
        print(f"[get_note_comments] 找到 {len(json_files)} 个评论JSON文件")
        
        all_comments = []
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)
                    if isinstance(file_data, list):
                        # 过滤出当前笔记的评论
                        # 抖音使用aweme_id，其他平台使用note_id
                        if platform == "dy":
                            note_comments = [c for c in file_data if c.get("aweme_id") == note_id]
                        elif platform == "juejin":
                            note_comments = [c for c in file_data if c.get("article_id") == note_id]
                        elif platform == "medium":
                            note_comments = [c for c in file_data if c.get("article_id") == note_id]
                        else:
                            note_comments = [c for c in file_data if c.get("note_id") == note_id]
                        all_comments.extend(note_comments)
            except Exception as e:
                print(f"[get_note_comments] 读取文件 {json_file} 失败: {e}")
                continue
        
        # 转换为前端需要的格式
        formatted_comments = []
        for comment in all_comments:
            # 处理时间戳转换为可读时间
            time_value = comment.get("create_time") or 0
            create_time = ""
            if time_value:
                try:
                    if isinstance(time_value, (int, float)) and time_value > 0:
                        create_time = datetime.fromtimestamp(time_value / 1000 if time_value > 1000000000000 else time_value).strftime("%Y-%m-%d %H:%M:%S")
                except:
                    pass
            
            formatted_comment = {
                "id": comment.get("comment_id", ""),
                "content": comment.get("content", ""),
                "author": comment.get("nickname", ""),
                "avatar": comment.get("avatar", ""),
                "create_time": create_time,
                "like_count": comment.get("like_count", 0),
                "sub_comment_count": comment.get("sub_comment_count", 0),
                "ip_location": comment.get("ip_location", ""),
                "parent_comment_id": comment.get("parent_comment_id"),
            }
            formatted_comments.append(formatted_comment)
        
        # 去重（基于comment_id）
        seen_ids = set()
        unique_comments = []
        for comment in formatted_comments:
            if comment["id"] and comment["id"] not in seen_ids:
                seen_ids.add(comment["id"])
                unique_comments.append(comment)
        
        # 按时间倒序排序（最新的在前）
        unique_comments.sort(key=lambda x: x.get("create_time", ""), reverse=True)
        
        print(f"[get_note_comments] item_id={item_id}, 总评论数: {len(unique_comments)}")
        
        # 分页
        total = len(unique_comments)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_comments = unique_comments[start:end]
        
        return {
            "comments": paginated_comments,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    except Exception as e:
        import traceback
        print(f"[get_note_comments] 错误: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/data/{platform}")
async def get_crawled_data(platform: str, page: int = 1, page_size: int = 20, keyword: str = "", source_keyword: str = "", crawler_type: str = "", note_type: str = "", sort_field: str = "", sort_order: str = "desc"):
    """获取爬取的数据列表"""
    try:
        import json
        from datetime import datetime
        
        # 数据文件在 data/{platform}/json/ 目录下
        # 快手使用"kuaishou"作为目录名，但API使用"ks"
        platform_dir = "kuaishou" if platform == "ks" else platform
        data_dir = project_root / "data" / platform_dir / "json"
        print(f"[get_crawled_data] platform={platform}, data_dir={data_dir}, exists={data_dir.exists()}")
        
        if not data_dir.exists():
            print(f"[get_crawled_data] 数据目录不存在: {data_dir}")
            return {
                "data": [],
                "total": 0,
                "page": page,
                "page_size": page_size
            }
        
        # 读取所有 contents 相关的 JSON 文件（包括所有爬取类型：search、detail、creator等）
        # 确保包含所有类型的爬取数据
        if crawler_type:
            # 如果指定了爬取类型，则只读取对应类型的文件
            pattern = f"*{crawler_type}_contents*.json"
            json_files = sorted(data_dir.glob(pattern), reverse=True)
        else:
            # 读取所有contents文件（包括search_contents、detail_contents、creator_contents等）
            json_files = sorted(data_dir.glob("*contents*.json"), reverse=True)
        print(f"[get_crawled_data] 找到 {len(json_files)} 个JSON文件（包含所有爬取类型）: {[f.name for f in json_files[:5]]}")
        
        all_data = []
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)
                    if isinstance(file_data, list):
                        all_data.extend(file_data)
                    elif isinstance(file_data, dict):
                        all_data.append(file_data)
            except Exception as e:
                print(f"[get_crawled_data] 读取文件 {json_file} 失败: {e}")
                continue
        
        # 转换为前端需要的格式
        formatted_data = []
        for item in all_data:
            # 处理时间戳转换为可读时间
            time_value = item.get("time") or item.get("create_time") or item.get("last_update_time") or 0
            publish_time = ""
            if time_value:
                try:
                    from datetime import datetime
                    if isinstance(time_value, (int, float)) and time_value > 0:
                        publish_time = datetime.fromtimestamp(time_value / 1000 if time_value > 1000000000000 else time_value).strftime("%Y-%m-%d %H:%M:%S")
                except:
                    pass
            
            # 根据不同平台映射字段名（快手使用video_id，抖音使用aweme_id，小红书使用note_id）
            if platform == "ks":
                # 快手字段映射
                formatted_item = {
                    "id": item.get("video_id", ""),
                    "title": item.get("title", ""),
                    "author": item.get("nickname", ""),
                    "publish_time": publish_time,
                    "liked_count": item.get("liked_count", "0"),
                    "comment_count": item.get("comment_count", "0"),
                    "collected_count": item.get("viewd_count", "0"),  # 快手用viewd_count
                    "share_count": "0",  # 快手可能没有share_count
                    "desc": item.get("desc", ""),
                    "note_url": item.get("video_url", ""),  # 快手用video_url
                    "type": "video" if item.get("video_type") == "video" else "normal",  # 快手用video_type
                    "source_keyword": item.get("source_keyword", ""),
                }
            elif platform == "dy":
                # 抖音字段映射
                aweme_type = item.get("aweme_type", "")
                # 抖音aweme_type: 2=图片, 4=视频, 68=图文
                type_mapping = {
                    "2": "normal",  # 图片
                    "4": "video",   # 视频
                    "68": "normal"  # 图文
                }
                formatted_item = {
                    "id": item.get("aweme_id", ""),
                    "title": item.get("title", ""),
                    "author": item.get("nickname", ""),
                    "publish_time": publish_time,
                    "liked_count": item.get("liked_count", "0"),
                    "comment_count": item.get("comment_count", "0"),
                    "collected_count": item.get("collected_count", "0"),
                    "share_count": item.get("share_count", "0"),
                    "desc": item.get("desc", ""),
                    "note_url": item.get("aweme_url", ""),  # 抖音用aweme_url
                    "type": type_mapping.get(str(aweme_type), "video" if aweme_type else "normal"),  # 抖音用aweme_type判断
                    "source_keyword": item.get("source_keyword", ""),
                }
            elif platform == "juejin":
                # 掘金字段映射
                formatted_item = {
                    "id": item.get("article_id", ""),
                    "title": item.get("title", ""),
                    "author": item.get("nickname", ""),
                    "publish_time": publish_time,
                    "liked_count": item.get("liked_count", "0"),
                    "comment_count": item.get("comment_count", "0"),
                    "collected_count": item.get("collect_count", "0"),
                    "share_count": item.get("share_count", "0"),
                    "desc": item.get("desc", ""),
                    "note_url": item.get("article_url", ""),
                    "type": "article",
                    "source_keyword": item.get("source_keyword", ""),
                }
            elif platform == "medium":
                # Medium字段映射
                formatted_item = {
                    "id": item.get("article_id", ""),
                    "title": item.get("title", ""),
                    "author": item.get("nickname", ""),
                    "publish_time": publish_time,
                    "liked_count": item.get("liked_count", "0"),
                    "comment_count": item.get("comment_count", "0"),
                    "collected_count": "0",  # Medium可能没有收藏数
                    "share_count": item.get("share_count", "0"),
                    "desc": item.get("desc", ""),
                    "note_url": item.get("article_url", ""),
                    "type": "article",
                    "source_keyword": item.get("source_keyword", ""),
                }
            else:
                # 小红书等其他平台字段映射（默认）
                formatted_item = {
                    "id": item.get("note_id", ""),
                    "title": item.get("title", ""),
                    "author": item.get("nickname", ""),
                    "publish_time": publish_time,
                    "liked_count": item.get("liked_count", "0"),
                    "comment_count": item.get("comment_count", "0"),
                    "collected_count": item.get("collected_count", "0"),
                    "share_count": item.get("share_count", "0"),
                    "desc": item.get("desc", ""),
                    "note_url": item.get("note_url", ""),
                    "type": item.get("type", "normal"),
                    "source_keyword": item.get("source_keyword", ""),
                }
            formatted_data.append(formatted_item)
        
        # 去重（基于note_id）
        seen_ids = set()
        unique_data = []
        for item in formatted_data:
            if item["id"] and item["id"] not in seen_ids:
                seen_ids.add(item["id"])
                unique_data.append(item)
        
        print(f"[get_crawled_data] 格式化后数据: {len(formatted_data)}, 去重后: {len(unique_data)}")
        
        # 根据source_keyword筛选
        if source_keyword:
            unique_data = [
                item for item in unique_data
                if item.get("source_keyword", "") == source_keyword
            ]
            print(f"[get_crawled_data] 根据source_keyword='{source_keyword}'筛选后: {len(unique_data)}条")
        
        # 根据note_type筛选
        if note_type:
            # 将前端的中文类型转换为数据中的类型值
            type_mapping = {
                "图文": "normal",
                "视频": "video",
                "文章": "normal"  # 文章也映射为normal，因为数据中只有normal和video
            }
            target_type = type_mapping.get(note_type, note_type)
            unique_data = [
                item for item in unique_data
                if item.get("type", "") == target_type
            ]
            print(f"[get_crawled_data] 根据note_type='{note_type}'筛选后: {len(unique_data)}条")
        
        # 搜索过滤（如果有关键词，在标题、作者、描述中搜索）
        if keyword:
            keyword_lower = keyword.lower()
            unique_data = [
                item for item in unique_data
                if keyword_lower in item.get("title", "").lower() 
                or keyword_lower in item.get("author", "").lower()
                or keyword_lower in item.get("desc", "").lower()
            ]
            print(f"[get_crawled_data] 根据keyword='{keyword}'筛选后: {len(unique_data)}条")
        
        # 排序处理
        if sort_field and sort_order:
            def parse_count(count_str):
                """将点赞数、评论数、收藏数转换为数字用于排序"""
                if not count_str or count_str == '-':
                    return 0
                count_str = str(count_str).strip()
                try:
                    # 处理"13.2万"这样的格式
                    if '万' in count_str:
                        num = float(count_str.replace('万', ''))
                        return int(num * 10000)
                    elif '千' in count_str:
                        num = float(count_str.replace('千', ''))
                        return int(num * 1000)
                    else:
                        return int(float(count_str))
                except:
                    return 0
            
            reverse = sort_order.lower() == "desc"
            if sort_field in ["liked_count", "comment_count", "collected_count"]:
                unique_data.sort(key=lambda x: parse_count(x.get(sort_field, "0")), reverse=reverse)
                print(f"[get_crawled_data] 根据{sort_field} {sort_order}排序")
        
        # 分页
        total = len(unique_data)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_data = unique_data[start:end]
        
        print(f"[get_crawled_data] 返回数据: total={total}, page={page}, page_size={page_size}, 当前页数据量={len(paginated_data)}")
        
        return {
            "data": paginated_data,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    except Exception as e:
        import traceback
        print(f"[get_crawled_data] 错误: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/data/{platform}/filter-options")
async def get_filter_options(platform: str):
    """获取筛选选项（关键词列表等）"""
    try:
        import json
        
        # 数据文件在 data/{platform}/json/ 目录下
        # 快手使用"kuaishou"作为目录名，但API使用"ks"
        platform_dir = "kuaishou" if platform == "ks" else platform
        data_dir = project_root / "data" / platform_dir / "json"
        
        if not data_dir.exists():
            return {
                "keywords": [],
                "crawler_types": []
            }
        
        # 读取所有 contents 相关的 JSON 文件
        json_files = sorted(data_dir.glob("*contents*.json"), reverse=True)
        
        keywords_set = set()
        crawler_types_set = set()
        
        for json_file in json_files:
            try:
                # 从文件名提取crawler_type（例如：search_contents_2025-12-20.json -> search）
                file_name = json_file.name
                if '_contents_' in file_name:
                    crawler_type = file_name.split('_contents_')[0]
                    crawler_types_set.add(crawler_type)
                
                with open(json_file, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)
                    if isinstance(file_data, list):
                        for item in file_data:
                            source_keyword = item.get("source_keyword", "")
                            if source_keyword:
                                keywords_set.add(source_keyword)
            except Exception as e:
                print(f"[get_filter_options] 读取文件 {json_file} 失败: {e}")
                continue
        
        return {
            "keywords": sorted(list(keywords_set)),
            "crawler_types": sorted(list(crawler_types_set))
        }
    except Exception as e:
        import traceback
        print(f"[get_filter_options] 错误: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/data/{platform}/comments/{item_id}")
async def get_note_comments(platform: str, item_id: str, page: int = 1, page_size: int = 50):
    """获取某个笔记的评论列表"""
    try:
        import json
        from datetime import datetime
        
        # 数据文件在 data/{platform}/json/ 目录下
        # 快手使用"kuaishou"作为目录名，但API使用"ks"
        platform_dir = "kuaishou" if platform == "ks" else platform
        data_dir = project_root / "data" / platform_dir / "json"
        print(f"[get_note_comments] platform={platform}, item_id={item_id}")
        
        if not data_dir.exists():
            return {
                "comments": [],
                "total": 0,
                "page": page,
                "page_size": page_size
            }
        
        # 读取所有 comments 相关的 JSON 文件
        json_files = sorted(data_dir.glob("*comments*.json"), reverse=True)
        print(f"[get_note_comments] 找到 {len(json_files)} 个评论JSON文件")
        
        # 根据不同平台使用不同的字段名来过滤评论
        if platform == "ks":
            id_field = "video_id"
        elif platform == "juejin" or platform == "medium":
            id_field = "article_id"
        else:
            id_field = "note_id"
        
        all_comments = []
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)
                    if isinstance(file_data, list):
                        # 过滤出当前笔记/视频的评论
                        filtered_comments = [c for c in file_data if c.get(id_field) == item_id]
                        all_comments.extend(filtered_comments)
            except Exception as e:
                print(f"[get_note_comments] 读取文件 {json_file} 失败: {e}")
                continue
        
        # 转换为前端需要的格式
        formatted_comments = []
        for comment in all_comments:
            # 处理时间戳转换为可读时间
            time_value = comment.get("create_time") or 0
            create_time = ""
            if time_value:
                try:
                    if isinstance(time_value, (int, float)) and time_value > 0:
                        create_time = datetime.fromtimestamp(time_value / 1000 if time_value > 1000000000000 else time_value).strftime("%Y-%m-%d %H:%M:%S")
                except:
                    pass
            
            formatted_comment = {
                "id": comment.get("comment_id", ""),
                "content": comment.get("content", ""),
                "author": comment.get("nickname", ""),
                "avatar": comment.get("avatar", ""),
                "create_time": create_time,
                "like_count": comment.get("like_count", 0),
                "sub_comment_count": comment.get("sub_comment_count", 0),
                "ip_location": comment.get("ip_location", ""),
                "parent_comment_id": comment.get("parent_comment_id"),
            }
            formatted_comments.append(formatted_comment)
        
        # 去重（基于comment_id）
        seen_ids = set()
        unique_comments = []
        for comment in formatted_comments:
            if comment["id"] and comment["id"] not in seen_ids:
                seen_ids.add(comment["id"])
                unique_comments.append(comment)
        
        # 按时间倒序排序（最新的在前）
        unique_comments.sort(key=lambda x: x.get("create_time", ""), reverse=True)
        
        print(f"[get_note_comments] item_id={item_id}, 总评论数: {len(unique_comments)}")
        
        # 分页
        total = len(unique_comments)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_comments = unique_comments[start:end]
        
        return {
            "comments": paginated_comments,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    except Exception as e:
        import traceback
        print(f"[get_note_comments] 错误: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """获取总览统计数据"""
    try:
        output_dir = project_root / "output"
        stats = {}
        
        for platform in ["xhs", "dy", "ks", "bili", "wb", "tieba", "zhihu"]:
            platform_dir = output_dir / platform
            if platform_dir.exists():
                file_count = len(list(platform_dir.glob("*")))
                stats[platform] = {
                    "name": platform,
                    "data_count": file_count,
                    "last_crawl_time": None  # TODO: 获取最后爬取时间
                }
            else:
                stats[platform] = {
                    "name": platform,
                    "data_count": 0,
                    "last_crawl_time": None
                }
        
        return {
            "stats": stats,
            "total_tasks": len(task_status),
            "running_tasks": len([t for t in task_status.values() if t.get("status") == "running"])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 微信公众号相关 API ====================

try:
    from wechat_service import wechat_service
    print("✓ 微信公众号服务模块加载成功")
except ImportError as e:
    print(f"警告: 微信公众号服务模块导入失败: {e}")
    wechat_service = None


@app.post("/api/wechat/login/create-url")
async def create_wechat_login_url():
    """创建微信读书登录URL"""
    if not wechat_service:
        raise HTTPException(status_code=503, detail="微信公众号服务未启用")
    try:
        result = await wechat_service.create_login_url()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/wechat/login/result/{uuid}")
async def get_wechat_login_result(uuid: str):
    """获取微信读书登录结果"""
    if not wechat_service:
        raise HTTPException(status_code=503, detail="微信公众号服务未启用")
    try:
        result = await wechat_service.get_login_result(uuid)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class WechatAccountRequest(BaseModel):
    """微信读书账号请求模型"""
    account_id: str
    name: str
    token: str
    status: int = 1


@app.post("/api/wechat/accounts")
async def add_wechat_account(request: WechatAccountRequest):
    """添加微信读书账号"""
    if not wechat_service:
        raise HTTPException(status_code=503, detail="微信公众号服务未启用")
    try:
        account = await wechat_service.add_account(
            request.account_id, request.name, request.token, request.status
        )
        return {
            "id": account.id,
            "name": account.name,
            "status": account.status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/wechat/accounts")
async def list_wechat_accounts():
    """获取微信读书账号列表"""
    if not wechat_service:
        raise HTTPException(status_code=503, detail="微信公众号服务未启用")
    try:
        accounts = await wechat_service.list_accounts()
        return {"accounts": accounts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class WechatStatusRequest(BaseModel):
    """状态更新请求模型"""
    status: int


@app.put("/api/wechat/accounts/{account_id}/status")
async def update_wechat_account_status(account_id: str, request: WechatStatusRequest):
    """更新账号状态"""
    if not wechat_service:
        raise HTTPException(status_code=503, detail="微信公众号服务未启用")
    try:
        await wechat_service.update_account_status(account_id, request.status)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/wechat/accounts/{account_id}")
async def delete_wechat_account(account_id: str):
    """删除账号"""
    if not wechat_service:
        raise HTTPException(status_code=503, detail="微信公众号服务未启用")
    try:
        await wechat_service.delete_account(account_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class WechatFeedRequest(BaseModel):
    """公众号订阅源请求模型"""
    feed_id: str
    mp_name: str
    mp_cover: str
    mp_intro: str
    update_time: int
    status: int = 1


@app.post("/api/wechat/feeds")
async def add_wechat_feed(request: WechatFeedRequest):
    """添加公众号订阅源"""
    if not wechat_service:
        raise HTTPException(status_code=503, detail="微信公众号服务未启用")
    try:
        feed = await wechat_service.add_feed(
            request.feed_id, request.mp_name, request.mp_cover, 
            request.mp_intro, request.update_time, request.status
        )
        return {
            "id": feed.id,
            "mp_name": feed.mp_name,
            "status": feed.status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/wechat/feeds")
async def list_wechat_feeds():
    """获取公众号订阅源列表"""
    if not wechat_service:
        raise HTTPException(status_code=503, detail="微信公众号服务未启用")
    try:
        feeds = await wechat_service.list_feeds()
        return {"feeds": feeds}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/wechat/feeds/{feed_id}/refresh")
async def refresh_wechat_feed(feed_id: str):
    """刷新公众号文章"""
    if not wechat_service:
        raise HTTPException(status_code=503, detail="微信公众号服务未启用")
    try:
        result = await wechat_service.refresh_mp_articles(feed_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/wechat/feeds/{feed_id}/status")
async def update_wechat_feed_status(feed_id: str, request: WechatStatusRequest):
    """更新订阅源状态"""
    if not wechat_service:
        raise HTTPException(status_code=503, detail="微信公众号服务未启用")
    try:
        await wechat_service.update_feed_status(feed_id, request.status)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/wechat/feeds/{feed_id}")
async def delete_wechat_feed(feed_id: str):
    """删除订阅源"""
    if not wechat_service:
        raise HTTPException(status_code=503, detail="微信公众号服务未启用")
    try:
        await wechat_service.delete_feed(feed_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class WechatMpInfoRequest(BaseModel):
    """公众号信息请求模型"""
    wxs_link: str


@app.post("/api/wechat/mp/info")
async def get_wechat_mp_info(request: WechatMpInfoRequest):
    """通过分享链接获取公众号信息"""
    if not wechat_service:
        raise HTTPException(status_code=503, detail="微信公众号服务未启用")
    try:
        result = await wechat_service.get_mp_info(request.wxs_link)
        return {"mp_info": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/wechat/articles")
async def list_wechat_articles(mp_id: Optional[str] = None, limit: int = 20, offset: int = 0):
    """获取公众号文章列表"""
    if not wechat_service:
        raise HTTPException(status_code=503, detail="微信公众号服务未启用")
    try:
        articles = await wechat_service.list_articles(mp_id, limit, offset)
        return {"articles": articles, "total": len(articles)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/wechat/feeds/{feed_id}/history")
async def get_wechat_history_articles(feed_id: str):
    """获取公众号历史文章"""
    if not wechat_service:
        raise HTTPException(status_code=503, detail="微信公众号服务未启用")
    try:
        result = await wechat_service.get_history_mp_articles(feed_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/wechat/feeds/history/progress")
async def get_wechat_history_progress():
    """获取正在获取历史文章的公众号信息"""
    if not wechat_service:
        raise HTTPException(status_code=503, detail="微信公众号服务未启用")
    try:
        progress = wechat_service.get_in_progress_history_mp()
        return progress
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

