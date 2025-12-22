# -*- coding: utf-8 -*-
"""
爬虫管理 FastAPI 应用
与 MediaCrawler 保持完全一致的框架和实现
只处理 /api/crawler/* 路由（添加 /crawler 前缀以区分 Flask 路由）
"""
import sys
import os
import asyncio
import sqlite3
import json
from pathlib import Path
from typing import Optional, List, Dict, Union
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 获取 BASE_DIR（项目根目录）
try:
    from conf import BASE_DIR
except ImportError:
    BASE_DIR = Path(__file__).parent.resolve()

# 数据库路径
DB_PATH = BASE_DIR / "db" / "database.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# 添加 MediaCrawler 路径
MEDIACRAWLER_PATH = Path(__file__).parent / 'MediaCrawler'
if MEDIACRAWLER_PATH.exists():
    sys.path.insert(0, str(MEDIACRAWLER_PATH))
    project_root = MEDIACRAWLER_PATH
    print(f"✓ MediaCrawler 路径: {MEDIACRAWLER_PATH}")
else:
    # 尝试备用路径
    possible_paths = [
        Path(__file__).parent.parent / 'MediaCrawler',
        Path('/Users/a58/MediaCrawler'),
    ]
    for path in possible_paths:
        if path.exists():
            MEDIACRAWLER_PATH = path
            project_root = MEDIACRAWLER_PATH
            sys.path.insert(0, str(MEDIACRAWLER_PATH))
            print(f"✓ 使用备用 MediaCrawler 路径: {MEDIACRAWLER_PATH}")
            break
    else:
        project_root = Path(__file__).parent / 'MediaCrawler'

# 创建 FastAPI 应用（与 MediaCrawler 保持一致）
crawler_app = FastAPI(
    title="MediaCrawler Admin API",
    description="爬虫管理 API - 与 MediaCrawler 保持一致",
    version="1.0.0"
)

# 配置 CORS（与 MediaCrawler 保持一致）
crawler_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 存储运行中的任务（与 MediaCrawler 保持一致）
running_tasks: Dict[str, asyncio.Task] = {}
task_status: Dict[str, Dict] = {}

# ==================== 数据模型（与 MediaCrawler 保持一致）====================

class PlatformConfig(BaseModel):
    """平台配置模型 - 与 MediaCrawler 保持一致"""
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
    platform_specific: Optional[Dict] = {}
    force_relogin: bool = False
    
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
    """任务请求模型 - 与 MediaCrawler 保持一致"""
    platform: str
    config: PlatformConfig


# ==================== 导入 MediaCrawler 服务 ====================

# 尝试导入 MediaCrawler 模块
CRAWLER_AVAILABLE = False
CrawlerFactory = None
login_service = None
wechat_service = None

try:
    # 导入项目主模块
    import importlib.util
    main_module_path = project_root / "main.py"
    if main_module_path.exists():
        spec = importlib.util.spec_from_file_location("mediacrawler_main", main_module_path)
        mediacrawler_main = importlib.util.module_from_spec(spec)
        try:
            original_cwd = os.getcwd()
            try:
                os.chdir(str(project_root))
                spec.loader.exec_module(mediacrawler_main)
                CrawlerFactory = mediacrawler_main.CrawlerFactory
                print(f"✓ MediaCrawler主模块导入成功，CrawlerFactory: {CrawlerFactory}")
            finally:
                os.chdir(original_cwd)
        except Exception as e:
            print(f"警告: MediaCrawler主模块导入失败: {e}")
            CrawlerFactory = None
    else:
        CrawlerFactory = None
    
    import config
    CRAWLER_AVAILABLE = True
    print(f"✓ CRAWLER_AVAILABLE = {CRAWLER_AVAILABLE}")
except ImportError as e:
    print(f"警告: MediaCrawler模块导入失败: {e}")
    CrawlerFactory = None
    import config
    CRAWLER_AVAILABLE = False

# 尝试导入登录服务
try:
    from admin_api.login_service import login_service
    if login_service is None:
        from admin_api.login_service import LoginService
        login_service = LoginService()
    print("✓ login_service 导入成功")
    MEDIACRAWLER_AVAILABLE = True
except ImportError as e:
    print(f"警告: login_service 导入失败: {e}")
    login_service = None
    # 创建 mock
    class MockLoginService:
        async def get_qrcode(self, platform, force=False): 
            return {
                "qrcode_id": "", 
                "qrcode_base64": "", 
                "expires_in": 120,
                "error": "登录服务未正确加载，请检查依赖"
            }
        async def check_login_status(self, qrcode_id): return {"status": "pending"}
        async def has_valid_cookie(self, platform): return False
        async def load_cookie(self, platform): return None
        async def delete_cookie(self, platform): return True
    login_service = MockLoginService()
except Exception as e:
    print(f"警告: login_service 导入出错: {e}")
    login_service = None

# 尝试导入微信公众号服务
try:
    from admin_api.wechat_service import wechat_service
    if wechat_service is None:
        from admin_api.wechat_service import WechatService
        wechat_service = WechatService()
    print("✓ wechat_service 导入成功")
except ImportError as e:
    print(f"警告: wechat_service 导入失败: {e}")
    wechat_service = None
except Exception as e:
    print(f"警告: wechat_service 导入出错: {e}")
    wechat_service = None

MEDIACRAWLER_AVAILABLE = login_service is not None or wechat_service is not None

# ==================== 内部函数（与 MediaCrawler 保持一致）====================

async def save_platform_config_internal(platform: str, config_data: PlatformConfig):
    """内部保存配置函数 - 与 MediaCrawler 保持一致"""
    from datetime import datetime
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [save_platform_config_internal] 开始更新配置...")
    config.PLATFORM = platform
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [save_platform_config_internal] 设置平台: {platform}")
    
    # 处理keywords，支持数组或字符串格式
    if isinstance(config_data.keywords, list):
        config.KEYWORDS = ",".join(config_data.keywords)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [save_platform_config_internal] 关键词(列表): {config.KEYWORDS}")
    else:
        config.KEYWORDS = config_data.keywords or ""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [save_platform_config_internal] 关键词(字符串): {config.KEYWORDS}")
    
    config.LOGIN_TYPE = config_data.login_type
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [save_platform_config_internal] 登录类型: {config.LOGIN_TYPE}")
    
    config.CRAWLER_TYPE = config_data.crawler_type
    config.START_PAGE = config_data.start_page
    config.CRAWLER_MAX_NOTES_COUNT = config_data.max_notes_count
    config.ENABLE_GET_COMMENTS = config_data.enable_get_comments
    config.CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES = config_data.max_comments_count
    config.ENABLE_GET_MEIDAS = config_data.enable_get_medias
    config.HEADLESS = config_data.headless
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [save_platform_config_internal] 爬虫类型: {config.CRAWLER_TYPE}, 起始页: {config.START_PAGE}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [save_platform_config_internal] 最大笔记数: {config.CRAWLER_MAX_NOTES_COUNT}, 无头模式: {config.HEADLESS}")
    
    # 确保CDP模式被禁用，使用标准模式
    if hasattr(config, 'ENABLE_CDP_MODE'):
        config.ENABLE_CDP_MODE = False
    if hasattr(config, 'CDP_HEADLESS'):
        config.CDP_HEADLESS = config_data.headless
    config.SAVE_DATA_OPTION = config_data.save_data_option
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [save_platform_config_internal] 数据保存方式: {config.SAVE_DATA_OPTION}")
    
    # 保存平台特定配置
    if platform == "xhs":
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [save_platform_config_internal] 处理小红书特定配置...")
        if config_data.platform_specific and "sort_type" in config_data.platform_specific:
            config.SORT_TYPE = config_data.platform_specific["sort_type"]
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [save_platform_config_internal] 排序类型: {config.SORT_TYPE}")
        if config_data.specified_urls:
            config.XHS_SPECIFIED_NOTE_URL_LIST = config_data.specified_urls
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [save_platform_config_internal] 指定URL数量: {len(config.XHS_SPECIFIED_NOTE_URL_LIST)}")
        if config_data.creator_ids:
            config.XHS_CREATOR_ID_LIST = config_data.creator_ids
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [save_platform_config_internal] 创作者ID数量: {len(config.XHS_CREATOR_ID_LIST)}")
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [save_platform_config_internal] ✓ 配置更新完成")


# ==================== 根路径 ====================

@crawler_app.get("/")
async def root():
    """根路径"""
    return {"message": "MediaCrawler Admin API", "version": "1.0.0"}


# ==================== 平台列表 ====================

@crawler_app.get("/platforms")
async def get_platforms():
    """获取支持的平台列表 - 与 MediaCrawler 保持一致"""
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


# ==================== 配置管理 ====================

@crawler_app.get("/config/{platform}")
async def get_platform_config(platform: str):
    """获取平台配置 - 与 MediaCrawler 保持一致"""
    try:
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


@crawler_app.post("/config/{platform}")
async def save_platform_config(platform: str, config_data: PlatformConfig):
    """保存平台配置 - 与 MediaCrawler 保持一致"""
    try:
        from datetime import datetime
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [save_platform_config] ========== 开始保存平台配置 ==========")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [save_platform_config] 平台: {platform}")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [save_platform_config] 配置数据: {config_data.model_dump() if hasattr(config_data, 'model_dump') else config_data}")
        
        # 更新配置到config模块
        await save_platform_config_internal(platform, config_data)
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [save_platform_config] ✓ 配置保存成功，平台: {platform}")
        return {"message": "配置保存成功", "platform": platform}
    except Exception as e:
        from datetime import datetime
        import traceback
        error_msg = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [save_platform_config] ✗ 保存配置失败: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 登录相关路由（与 MediaCrawler 完全一致）====================

@crawler_app.post("/login/qrcode")
async def get_qrcode(
    platform: str = Query(..., description="平台名称"),
    force: bool = Query(False, description="是否强制重新登录")
):
    """
    获取登录二维码 - 与 MediaCrawler 完全一致
    Args:
        platform: 平台名称
        force: 是否强制重新登录（忽略已有cookie）
    """
    try:
        if not MEDIACRAWLER_AVAILABLE or not login_service:
            raise HTTPException(status_code=503, detail="登录服务未启用")
        
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
        # 注意：login_service.get_qrcode() 不接受 force 参数
        # force 参数在前端逻辑中处理（检查 cookie）
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


@crawler_app.get("/login/status/{qrcode_id}")
async def check_login_status(qrcode_id: str):
    """检查登录状态 - 与 MediaCrawler 保持一致"""
    try:
        if not MEDIACRAWLER_AVAILABLE or not login_service:
            raise HTTPException(status_code=503, detail="登录服务未启用")
        result = await login_service.check_login_status(qrcode_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@crawler_app.get("/login/cookie/{platform}")
async def get_cookie(platform: str):
    """获取保存的cookie - 与 MediaCrawler 保持一致"""
    try:
        if not MEDIACRAWLER_AVAILABLE or not login_service:
            raise HTTPException(status_code=503, detail="登录服务未启用")
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


@crawler_app.delete("/login/cookie/{platform}")
async def delete_cookie(platform: str):
    """删除保存的cookie - 与 MediaCrawler 保持一致"""
    try:
        if not MEDIACRAWLER_AVAILABLE or not login_service:
            raise HTTPException(status_code=503, detail="登录服务未启用")
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


# ==================== 任务管理（与 MediaCrawler 保持一致）====================

def ensure_crawler_tasks_table():
    """确保爬虫任务记录表存在"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS crawler_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT UNIQUE NOT NULL,
                    platform TEXT NOT NULL,
                    crawler_type TEXT,
                    keywords TEXT,
                    login_type TEXT,
                    status TEXT DEFAULT 'running',
                    progress INTEGER DEFAULT 0,
                    message TEXT,
                    config_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
            ''')
            conn.commit()
            print(f"[ensure_crawler_tasks_table] ✓ 爬虫任务表已创建或已存在")
    except Exception as e:
        print(f"[ensure_crawler_tasks_table] ✗ 创建任务表失败: {e}")
        import traceback
        traceback.print_exc()

def save_task_to_db(task_id: str, platform: str, task_request: TaskRequest, status: str = "running", progress: int = 0, message: str = "任务启动中..."):
    """保存任务记录到数据库"""
    try:
        ensure_crawler_tasks_table()
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            # 准备配置信息
            config_dict = {
                "crawler_type": task_request.config.crawler_type if hasattr(task_request.config, 'crawler_type') else None,
                "keywords": task_request.config.keywords if hasattr(task_request.config, 'keywords') else None,
                "login_type": task_request.config.login_type if hasattr(task_request.config, 'login_type') else None,
                "headless": task_request.config.headless if hasattr(task_request.config, 'headless') else None,
                "max_notes_count": task_request.config.max_notes_count if hasattr(task_request.config, 'max_notes_count') else None,
            }
            config_json = json.dumps(config_dict, ensure_ascii=False)
            
            # 提取关键词（如果是列表，转换为字符串）
            keywords_str = None
            if hasattr(task_request.config, 'keywords') and task_request.config.keywords:
                if isinstance(task_request.config.keywords, list):
                    keywords_str = ", ".join(task_request.config.keywords)
                else:
                    keywords_str = str(task_request.config.keywords)
            
            # 插入或更新任务记录
            cursor.execute('''
                INSERT OR REPLACE INTO crawler_tasks 
                (task_id, platform, crawler_type, keywords, login_type, status, progress, message, config_json, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                task_id,
                platform,
                task_request.config.crawler_type if hasattr(task_request.config, 'crawler_type') else None,
                keywords_str,
                task_request.config.login_type if hasattr(task_request.config, 'login_type') else None,
                status,
                progress,
                message,
                config_json
            ))
            conn.commit()
            print(f"[save_task_to_db] ✓ 任务记录已保存到数据库: {task_id}")
    except Exception as e:
        print(f"[save_task_to_db] ✗ 保存任务记录失败: {e}")
        import traceback
        traceback.print_exc()

def update_task_status(task_id: str, status: str, progress: int = None, message: str = None):
    """更新任务状态"""
    try:
        ensure_crawler_tasks_table()  # 确保表存在
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            update_fields = ["status = ?", "updated_at = CURRENT_TIMESTAMP"]
            update_values = [status]
            
            if progress is not None:
                update_fields.append("progress = ?")
                update_values.append(progress)
            
            if message is not None:
                update_fields.append("message = ?")
                update_values.append(message)
            
            if status in ["completed", "failed"]:
                update_fields.append("completed_at = CURRENT_TIMESTAMP")
            
            update_values.append(task_id)
            
            cursor.execute(f'''
                UPDATE crawler_tasks 
                SET {", ".join(update_fields)}
                WHERE task_id = ?
            ''', update_values)
            conn.commit()
            print(f"[update_task_status] ✓ 任务状态已更新: {task_id} -> {status}")
    except Exception as e:
        print(f"[update_task_status] ✗ 更新任务状态失败: {e}")
        import traceback
        traceback.print_exc()

@crawler_app.post("/tasks/start")
async def start_crawler_task(task_request: TaskRequest, background_tasks: BackgroundTasks):
    """启动爬虫任务 - 与 MediaCrawler 保持一致"""
    try:
        task_id = f"{task_request.platform}_{int(asyncio.get_event_loop().time())}"
        
        # 保存任务记录到数据库（使用 asyncio.to_thread 确保在异步上下文中正确执行）
        try:
            await asyncio.to_thread(save_task_to_db, task_id, task_request.platform, task_request, "running", 0, "任务启动中...")
            print(f"[start_crawler_task] ✓ 任务记录已保存到数据库: {task_id}")
        except Exception as save_error:
            print(f"[start_crawler_task] ⚠️ 保存任务记录失败: {save_error}")
            import traceback
            traceback.print_exc()
            # 即使保存失败，也继续执行任务
        
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
                    print(f"[start_crawler_task] 用户选择强制重新登录，将使用qrcode登录方式")
                    task_request.config.login_type = 'qrcode'
                else:
                    # 自动检测cookie并验证有效性
                    has_cookie = False
                    cookie_value = None
                    cookie_valid = False
                    try:
                        cookie = await login_service.load_cookie(task_request.platform)
                        if cookie:
                            cookie_value = cookie
                            has_cookie = True
                            print(f"[start_crawler_task] 检测到已保存的cookie，长度: {len(cookie)} 字符")
                            
                            # 验证Cookie有效性
                            print(f"[start_crawler_task] 正在验证Cookie有效性...")
                            try:
                                cookie_valid = await login_service.verify_cookie_validity(task_request.platform, cookie)
                                if cookie_valid:
                                    print(f"[start_crawler_task] ✓ Cookie验证成功，可以使用")
                                else:
                                    print(f"[start_crawler_task] ⚠️ Cookie验证失败，已过期或无效，需要重新登录")
                            except Exception as verify_error:
                                print(f"[start_crawler_task] ⚠️ Cookie验证过程出错: {verify_error}，将要求重新登录")
                                cookie_valid = False
                    except Exception as e:
                        print(f"[start_crawler_task] 加载cookie失败: {e}")
                        pass

                    if has_cookie and cookie_valid:
                        task_request.config.login_type = 'cookie'
                        print(f"[start_crawler_task] 已设置登录类型为cookie，将使用已验证的有效cookie")
                    else:
                        if has_cookie and not cookie_valid:
                            print(f"[start_crawler_task] Cookie已过期，将使用二维码登录方式")
                        else:
                            print(f"[start_crawler_task] 未检测到cookie，将使用登录类型: {task_request.config.login_type}")
                        # Cookie无效或不存在，强制使用二维码登录
                        task_request.config.login_type = 'qrcode'
                
                await save_platform_config_internal(task_request.platform, task_request.config)
                
                # 设置Cookie到config（仅当Cookie有效时）
                if has_cookie and cookie_valid and cookie_value:
                    config.COOKIES = cookie_value
                    print(f"[start_crawler_task] ✓ 已验证的有效Cookie已设置到config.COOKIES，长度: {len(cookie_value)} 字符")
                else:
                    if has_cookie and not cookie_valid:
                        print(f"[start_crawler_task] ⚠️ Cookie已过期，未设置到config，将使用二维码登录")
                    else:
                        print(f"[start_crawler_task] ⚠️  未设置Cookie，config.COOKIES = '{config.COOKIES}'")
                
                # 打印关键配置信息
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
                
                # 更新数据库中的任务状态（使用 asyncio.to_thread 确保在异步上下文中正确执行）
                try:
                    await asyncio.to_thread(update_task_status, task_id, "running", 0, "任务启动中...")
                except Exception as update_error:
                    print(f"[start_crawler_task] ⚠️ 更新任务状态失败: {update_error}")
                
                # 切换到项目根目录执行爬虫
                original_cwd = os.getcwd()
                try:
                    os.chdir(str(project_root))
                    import sys
                    print(f"[start_crawler_task] 开始执行爬虫任务，平台: {task_request.platform}")
                    print(f"[start_crawler_task] 当前工作目录: {os.getcwd()}")
                    sys.stdout.flush()
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
                
                # 更新数据库中的任务状态（使用 asyncio.to_thread 确保在异步上下文中正确执行）
                try:
                    await asyncio.to_thread(update_task_status, task_id, "completed", 100, "任务完成")
                except Exception as update_error:
                    print(f"[start_crawler_task] ⚠️ 更新任务状态失败: {update_error}")
            except Exception as e:
                import traceback
                error_detail = str(e)
                task_status[task_id] = {
                    "status": "failed",
                    "platform": task_request.platform,
                    "progress": 0,
                    "message": error_detail
                }
                
                # 更新数据库中的任务状态（使用 asyncio.to_thread 确保在异步上下文中正确执行）
                try:
                    await asyncio.to_thread(update_task_status, task_id, "failed", 0, error_detail)
                except Exception as update_error:
                    print(f"[start_crawler_task] ⚠️ 更新任务状态失败: {update_error}")
                
                print(f"[start_crawler_task] 任务执行失败: {error_detail}")
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


@crawler_app.get("/tasks")
async def get_tasks():
    """获取任务列表 - 与 MediaCrawler 保持一致"""
    return {
        "tasks": [
            {
                "task_id": task_id,
                **status
            }
            for task_id, status in task_status.items()
        ]
    }


@crawler_app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """获取任务状态 - 与 MediaCrawler 保持一致"""
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task_status[task_id]


@crawler_app.delete("/tasks/{task_id}")
async def stop_task(task_id: str):
    """停止/删除任务 - 与 MediaCrawler 保持一致"""
    if task_id in running_tasks:
        running_tasks[task_id].cancel()
        del running_tasks[task_id]
    if task_id in task_status:
        del task_status[task_id]
    return {"message": "任务已删除"}
    raise HTTPException(status_code=404, detail="任务不存在")


# ==================== 总览统计（与 MediaCrawler 保持一致）====================

@crawler_app.get("/dashboard/stats")
async def get_dashboard_stats():
    """获取总览统计数据 - 与 MediaCrawler 保持一致"""
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


# ==================== 数据管理（与 MediaCrawler 保持一致）====================
# 由于数据管理模块代码较长，这里先实现核心功能
# 完整实现需要参考 MediaCrawler/admin_api/main.py 的 get_crawled_data 函数

@crawler_app.get("/data/{platform}")
async def get_crawled_data(
    platform: str, 
    page: int = 1, 
    page_size: int = 20, 
    keyword: str = "", 
    source_keyword: str = "", 
    crawler_type: str = "", 
    note_type: str = "", 
    sort_field: str = "", 
    sort_order: str = "desc"
):
    """获取爬取的数据列表 - 与 MediaCrawler 保持一致"""
    try:
        import json
        
        # 数据文件在 data/{platform}/json/ 目录下
        # 快手使用"kuaishou"作为目录名，但API使用"ks"
        # 抖音使用"douyin"作为目录名，但API使用"dy"
        if platform == "ks":
            platform_dir = "kuaishou"
        elif platform == "dy":
            platform_dir = "douyin"
        else:
            platform_dir = platform
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
        
        # 转换为前端需要的格式（完整实现，与 MediaCrawler 保持一致）
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


@crawler_app.get("/data/{platform}/comments/{item_id}")
async def get_note_comments(platform: str, item_id: str, page: int = 1, page_size: int = 50):
    """获取某个笔记的评论列表 - 与 MediaCrawler 保持一致"""
    try:
        import json
        from datetime import datetime
        
        # 数据文件在 data/{platform}/json/ 目录下
        # 快手使用"kuaishou"作为目录名，但API使用"ks"
        # 抖音使用"douyin"作为目录名，但API使用"dy"
        if platform == "ks":
            platform_dir = "kuaishou"
        elif platform == "dy":
            platform_dir = "douyin"
        else:
            platform_dir = platform
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


@crawler_app.get("/data/{platform}/filter-options")
async def get_filter_options(platform: str):
    """获取筛选选项（关键词列表等） - 与 MediaCrawler 保持一致"""
    try:
        import json
        
        # 快手使用"kuaishou"作为目录名，但API使用"ks"
        # 抖音使用"douyin"作为目录名，但API使用"dy"
        if platform == "ks":
            platform_dir = "kuaishou"
        elif platform == "dy":
            platform_dir = "douyin"
        else:
            platform_dir = platform
        data_dir = project_root / "data" / platform_dir / "json"
        
        if not data_dir.exists():
            return {"keywords": [], "crawler_types": []}
        
        json_files = sorted(data_dir.glob("*contents*.json"), reverse=True)
        keywords_set = set()
        crawler_types_set = set()
        
        for json_file in json_files[:10]:  # 只读取最近10个文件
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)
                    if isinstance(file_data, list):
                        for item in file_data:
                            if item.get("source_keyword"):
                                keywords_set.add(item.get("source_keyword"))
                            if item.get("crawler_type"):
                                crawler_types_set.add(item.get("crawler_type"))
            except:
                continue
        
        return {
            "keywords": sorted(list(keywords_set)),
            "crawler_types": sorted(list(crawler_types_set))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 微信公众号相关 API（与 MediaCrawler 保持一致）====================

class WechatAccountRequest(BaseModel):
    """微信读书账号请求模型"""
    account_id: str
    name: str
    token: str
    status: int = 1


class WechatStatusRequest(BaseModel):
    """状态更新请求模型"""
    status: int


class WechatFeedRequest(BaseModel):
    """公众号订阅源请求模型"""
    feed_id: str
    mp_name: str
    mp_cover: str
    mp_intro: str
    update_time: int
    status: int = 1


class WechatMpInfoRequest(BaseModel):
    """公众号信息请求模型"""
    wxs_link: str


@crawler_app.post("/wechat/login/create-url")
async def create_wechat_login_url():
    """创建微信读书登录URL - 与 MediaCrawler 保持一致"""
    if not wechat_service:
        raise HTTPException(status_code=503, detail="微信公众号服务未启用")
    try:
        result = await wechat_service.create_login_url()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@crawler_app.get("/wechat/login/result/{uuid}")
async def get_wechat_login_result(uuid: str):
    """获取微信读书登录结果 - 与 MediaCrawler 保持一致"""
    if not wechat_service:
        raise HTTPException(status_code=503, detail="微信公众号服务未启用")
    try:
        result = await wechat_service.get_login_result(uuid)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@crawler_app.post("/wechat/accounts")
async def add_wechat_account(request: WechatAccountRequest):
    """添加微信读书账号 - 与 MediaCrawler 保持一致"""
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


@crawler_app.get("/wechat/accounts")
async def list_wechat_accounts():
    """获取微信读书账号列表 - 与 MediaCrawler 保持一致"""
    if not wechat_service:
        raise HTTPException(status_code=503, detail="微信公众号服务未启用")
    try:
        accounts = await wechat_service.list_accounts()
        return {"accounts": accounts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@crawler_app.put("/wechat/accounts/{account_id}/status")
async def update_wechat_account_status(account_id: str, request: WechatStatusRequest):
    """更新账号状态 - 与 MediaCrawler 保持一致"""
    if not wechat_service:
        raise HTTPException(status_code=503, detail="微信公众号服务未启用")
    try:
        await wechat_service.update_account_status(account_id, request.status)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@crawler_app.delete("/wechat/accounts/{account_id}")
async def delete_wechat_account(account_id: str):
    """删除账号 - 与 MediaCrawler 保持一致"""
    if not wechat_service:
        raise HTTPException(status_code=503, detail="微信公众号服务未启用")
    try:
        await wechat_service.delete_account(account_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@crawler_app.post("/wechat/feeds")
async def add_wechat_feed(request: WechatFeedRequest):
    """添加公众号订阅源 - 与 MediaCrawler 保持一致"""
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


@crawler_app.get("/wechat/feeds")
async def list_wechat_feeds():
    """获取公众号订阅源列表 - 与 MediaCrawler 保持一致"""
    if not wechat_service:
        raise HTTPException(status_code=503, detail="微信公众号服务未启用")
    try:
        feeds = await wechat_service.list_feeds()
        return {"feeds": feeds}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@crawler_app.post("/wechat/feeds/{feed_id}/refresh")
async def refresh_wechat_feed(feed_id: str):
    """刷新公众号文章 - 与 MediaCrawler 保持一致"""
    if not wechat_service:
        raise HTTPException(status_code=503, detail="微信公众号服务未启用")
    try:
        result = await wechat_service.refresh_mp_articles(feed_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@crawler_app.put("/wechat/feeds/{feed_id}/status")
async def update_wechat_feed_status(feed_id: str, request: WechatStatusRequest):
    """更新订阅源状态 - 与 MediaCrawler 保持一致"""
    if not wechat_service:
        raise HTTPException(status_code=503, detail="微信公众号服务未启用")
    try:
        await wechat_service.update_feed_status(feed_id, request.status)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@crawler_app.delete("/wechat/feeds/{feed_id}")
async def delete_wechat_feed(feed_id: str):
    """删除订阅源 - 与 MediaCrawler 保持一致"""
    if not wechat_service:
        raise HTTPException(status_code=503, detail="微信公众号服务未启用")
    try:
        await wechat_service.delete_feed(feed_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@crawler_app.post("/wechat/mp/info")
async def get_wechat_mp_info(request: WechatMpInfoRequest):
    """通过分享链接获取公众号信息 - 与 MediaCrawler 保持一致"""
    if not wechat_service:
        raise HTTPException(status_code=503, detail="微信公众号服务未启用")
    try:
        result = await wechat_service.get_mp_info(request.wxs_link)
        return {"mp_info": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@crawler_app.get("/wechat/articles")
async def list_wechat_articles(mp_id: Optional[str] = None, limit: int = 20, offset: int = 0):
    """获取公众号文章列表 - 与 MediaCrawler 保持一致"""
    if not wechat_service:
        raise HTTPException(status_code=503, detail="微信公众号服务未启用")
    try:
        articles = await wechat_service.list_articles(mp_id, limit, offset)
        return {"articles": articles, "total": len(articles)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@crawler_app.post("/wechat/feeds/{feed_id}/history")
async def get_wechat_history_articles(feed_id: str):
    """获取公众号历史文章 - 与 MediaCrawler 保持一致"""
    if not wechat_service:
        raise HTTPException(status_code=503, detail="微信公众号服务未启用")
    try:
        result = await wechat_service.get_history_mp_articles(feed_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@crawler_app.get("/wechat/feeds/history/progress")
async def get_wechat_history_progress():
    """获取正在获取历史文章的公众号信息 - 与 MediaCrawler 保持一致"""
    if not wechat_service:
        raise HTTPException(status_code=503, detail="微信公众号服务未启用")
    try:
        progress = wechat_service.get_in_progress_history_mp()
        return progress
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🚀 爬虫管理 FastAPI 服务")
    print("=" * 60)
    print("📡 路由前缀: /api/crawler/*")
    print("=" * 60)
    # 初始化数据库表
    ensure_crawler_tasks_table()
    uvicorn.run(
        "crawler_fastapi:crawler_app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    )
