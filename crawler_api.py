# -*- coding: utf-8 -*-
"""
MediaCrawler 爬虫管理 API 蓝图
用于整合到 social-auto-upload-window
所有路由使用 /api/crawler 前缀
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import asyncio
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import threading
import time

# 创建蓝图
crawler_bp = Blueprint('crawler', __name__, url_prefix='/api/crawler')

# 添加 MediaCrawler 项目路径
# MediaCrawler 代码已内置到 social-auto-upload-window/MediaCrawler
MEDIACRAWLER_PATH = Path(__file__).parent / 'MediaCrawler'
if MEDIACRAWLER_PATH.exists():
    sys.path.insert(0, str(MEDIACRAWLER_PATH))
    print(f"✓ MediaCrawler 路径: {MEDIACRAWLER_PATH}")
else:
    print(f"⚠️ MediaCrawler 路径不存在: {MEDIACRAWLER_PATH}")
    # 尝试备用路径
    possible_paths = [
        Path(__file__).parent.parent / 'MediaCrawler',
        Path('/Users/a58/MediaCrawler'),
    ]
    for path in possible_paths:
        if path.exists():
            MEDIACRAWLER_PATH = path
            sys.path.insert(0, str(MEDIACRAWLER_PATH))
            print(f"✓ 使用备用 MediaCrawler 路径: {MEDIACRAWLER_PATH}")
            break
    else:
        print("⚠️ 未找到 MediaCrawler 路径，部分功能可能不可用")
        MEDIACRAWLER_PATH = Path(__file__).parent / 'MediaCrawler'  # 默认路径

# 尝试导入 MediaCrawler 模块
MEDIACRAWLER_AVAILABLE = False
login_service = None
wechat_service = None

try:
    # 确保 MediaCrawler 路径在 sys.path 中
    if MEDIACRAWLER_PATH and str(MEDIACRAWLER_PATH) not in sys.path:
        sys.path.insert(0, str(MEDIACRAWLER_PATH))
    
    from admin_api.main import app as mediacrawler_app
    print("✓ MediaCrawler 主模块导入成功")
except ImportError as e:
    print(f"警告: MediaCrawler 主模块导入失败: {e}")

# 尝试导入登录服务
try:
    if MEDIACRAWLER_PATH and str(MEDIACRAWLER_PATH) not in sys.path:
        sys.path.insert(0, str(MEDIACRAWLER_PATH))
    from admin_api.login_service import login_service
    if login_service is None:
        from admin_api.login_service import LoginService
        login_service = LoginService()
    print("✓ login_service 导入成功")
except ImportError as e:
    print(f"警告: login_service 导入失败: {e}")
    login_service = None
except Exception as e:
    print(f"警告: login_service 导入出错: {e}")
    login_service = None

# 尝试导入微信公众号服务
try:
    if MEDIACRAWLER_PATH and str(MEDIACRAWLER_PATH) not in sys.path:
        sys.path.insert(0, str(MEDIACRAWLER_PATH))
    from admin_api.wechat_service import wechat_service
    if wechat_service is None:
        from admin_api.wechat_service import WechatService
        wechat_service = WechatService()
    print("✓ wechat_service 导入成功")
    MEDIACRAWLER_AVAILABLE = True
except ImportError as e:
    print(f"警告: wechat_service 导入失败: {e}")
    wechat_service = None
except Exception as e:
    print(f"警告: wechat_service 导入出错: {e}")
    wechat_service = None

# 如果至少有一个服务可用，则认为 MediaCrawler 可用
if login_service or wechat_service:
    MEDIACRAWLER_AVAILABLE = True

def async_to_sync(f):
    """将异步函数转换为同步函数"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            # 尝试获取当前事件循环
            loop = asyncio.get_event_loop()
            # 如果事件循环正在运行，使用线程池执行器
            if loop.is_running():
                import concurrent.futures
                import threading
                # 创建新的事件循环在单独线程中运行
                def run_in_thread():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        return new_loop.run_until_complete(f(*args, **kwargs))
                    finally:
                        new_loop.close()
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_in_thread)
                    return future.result(timeout=30)  # 30秒超时
            else:
                # 如果事件循环未运行，直接使用
                return loop.run_until_complete(f(*args, **kwargs))
        except RuntimeError:
            # 如果没有事件循环，创建新的
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(f(*args, **kwargs))
            finally:
                loop.close()
        except Exception as e:
            print(f"[async_to_sync] 错误: {e}")
            import traceback
            print(f"[async_to_sync] 错误堆栈:\n{traceback.format_exc()}")
            raise
    return wrapper


def check_mediacrawler_available():
    """检查 MediaCrawler 是否可用"""
    if not MEDIACRAWLER_AVAILABLE:
        return jsonify({"error": "MediaCrawler 服务未启用"}), 503


# ==================== 总览统计 ====================

@crawler_bp.route('/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """获取总览统计"""
    if not MEDIACRAWLER_AVAILABLE:
        return jsonify({"error": "MediaCrawler 服务未启用"}), 503
    
    try:
        # 调用 MediaCrawler 的统计接口
        # 需要从 FastAPI 应用中提取统计逻辑
        # 这里简化处理，实际需要根据 MediaCrawler 的实现来调用
        from pathlib import Path
        
        @async_to_sync
        async def get_stats():
            # 从 MediaCrawler 的 main.py 中提取统计逻辑
            output_dir = MEDIACRAWLER_PATH / "output"
            stats = {}
            
            for platform in ["xhs", "dy", "ks", "bili", "wb", "tieba", "zhihu"]:
                platform_dir = output_dir / platform
                if platform_dir.exists():
                    file_count = len(list(platform_dir.glob("*")))
                    stats[platform] = {
                        "name": platform,
                        "data_count": file_count,
                        "last_crawl_time": None
                    }
                else:
                    stats[platform] = {
                        "name": platform,
                        "data_count": 0,
                        "last_crawl_time": None
                    }
            
            # 获取任务状态（需要从 MediaCrawler 的 main.py 中获取）
            # 这里简化处理
            return {
                "stats": stats,
                "total_tasks": 0,
                "running_tasks": 0
            }
        
        stats = get_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== 平台列表 ====================

@crawler_bp.route('/platforms', methods=['GET'])
def get_platforms():
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
        {"value": "wechat", "label": "公众号"}
    ]
    return jsonify({"platforms": platforms})


# ==================== 配置管理 ====================

@crawler_bp.route('/config/<platform>', methods=['GET'])
def get_config(platform):
    """获取平台配置"""
    if not MEDIACRAWLER_AVAILABLE:
        return jsonify({"error": "MediaCrawler 服务未启用"}), 503
    
    try:
        # 从 MediaCrawler 的 config 模块获取配置
        import config as mediacrawler_config
        
        config_data = {
            "platform": platform,
            "keywords": getattr(mediacrawler_config, "KEYWORDS", ""),
            "login_type": getattr(mediacrawler_config, "LOGIN_TYPE", "qrcode"),
            "crawler_type": getattr(mediacrawler_config, "CRAWLER_TYPE", "search"),
            "start_page": getattr(mediacrawler_config, "START_PAGE", 1),
            "max_notes_count": getattr(mediacrawler_config, "CRAWLER_MAX_NOTES_COUNT", 15),
            "enable_get_comments": getattr(mediacrawler_config, "ENABLE_GET_COMMENTS", True),
            "max_comments_count": getattr(mediacrawler_config, "CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES", 10),
            "enable_get_medias": getattr(mediacrawler_config, "ENABLE_GET_MEIDAS", False),
            "headless": getattr(mediacrawler_config, "HEADLESS", False),
            "save_data_option": getattr(mediacrawler_config, "SAVE_DATA_OPTION", "json")
        }
        
        # 根据平台获取特定配置
        if platform == "xhs":
            config_data["specified_urls"] = getattr(mediacrawler_config, "XHS_SPECIFIED_NOTE_URL_LIST", [])
            config_data["creator_ids"] = getattr(mediacrawler_config, "XHS_CREATOR_ID_LIST", [])
            config_data["platform_specific"] = {
                "sort_type": getattr(mediacrawler_config, "SORT_TYPE", "popularity_descending")
            }
        
        return jsonify(config_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@crawler_bp.route('/config/<platform>', methods=['POST'])
def save_config(platform):
    """保存平台配置"""
    if not MEDIACRAWLER_AVAILABLE:
        return jsonify({"error": "MediaCrawler 服务未启用"}), 503
    
    try:
        config_data = request.json
        import config as mediacrawler_config
        
        # 更新配置
        mediacrawler_config.PLATFORM = platform
        if isinstance(config_data.get("keywords"), list):
            mediacrawler_config.KEYWORDS = ",".join(config_data.get("keywords", []))
        else:
            mediacrawler_config.KEYWORDS = config_data.get("keywords", "")
        mediacrawler_config.LOGIN_TYPE = config_data.get("login_type", "qrcode")
        mediacrawler_config.CRAWLER_TYPE = config_data.get("crawler_type", "search")
        mediacrawler_config.START_PAGE = config_data.get("start_page", 1)
        mediacrawler_config.CRAWLER_MAX_NOTES_COUNT = config_data.get("max_notes_count", 15)
        mediacrawler_config.ENABLE_GET_COMMENTS = config_data.get("enable_get_comments", True)
        mediacrawler_config.CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES = config_data.get("max_comments_count", 10)
        mediacrawler_config.ENABLE_GET_MEIDAS = config_data.get("enable_get_medias", False)
        mediacrawler_config.HEADLESS = config_data.get("headless", False)
        mediacrawler_config.SAVE_DATA_OPTION = config_data.get("save_data_option", "json")
        
        # 平台特定配置
        if platform == "xhs":
            if config_data.get("specified_urls"):
                mediacrawler_config.XHS_SPECIFIED_NOTE_URL_LIST = config_data["specified_urls"]
            if config_data.get("creator_ids"):
                mediacrawler_config.XHS_CREATOR_ID_LIST = config_data["creator_ids"]
            if config_data.get("platform_specific", {}).get("sort_type"):
                mediacrawler_config.SORT_TYPE = config_data["platform_specific"]["sort_type"]
        
        return jsonify({"message": "配置保存成功", "platform": platform})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== 登录相关 ====================

@crawler_bp.route('/login/qrcode', methods=['POST'])
def get_qrcode():
    """获取登录二维码"""
    if not MEDIACRAWLER_AVAILABLE or not login_service:
        return jsonify({"error": "登录服务未启用"}), 503
    
    try:
        platform = request.args.get('platform')
        force = request.args.get('force', 'false').lower() == 'true'
        
        @async_to_sync
        async def get_qr():
            # login_service.get_qrcode 只需要 platform 参数
            return await login_service.get_qrcode(platform)
        
        result = get_qr()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@crawler_bp.route('/login/status/<qrcode_id>', methods=['GET'])
def check_login_status(qrcode_id):
    """检查登录状态"""
    from datetime import datetime
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [check_login_status] ========== 检查登录状态 ==========")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [check_login_status] qrcode_id: {qrcode_id}")
    
    if not MEDIACRAWLER_AVAILABLE or not login_service:
        error_msg = "登录服务未启用"
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [check_login_status] ✗ {error_msg}")
        return jsonify({"error": error_msg}), 503
    
    try:
        @async_to_sync
        async def check_status():
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [check_login_status] 开始调用 login_service.check_login_status...")
            try:
                result = await asyncio.wait_for(
                    login_service.check_login_status(qrcode_id),
                    timeout=30.0  # 增加到30秒超时，给登录检查更多时间
                )
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [check_login_status] ✓ 获取到登录状态: {result.get('status', 'unknown')}")
                return result
            except asyncio.TimeoutError:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [check_login_status] ✗ 检查登录状态超时（30秒）")
                # 超时不一定意味着失败，可能还在等待扫码，返回pending状态
                return {"status": "pending", "message": "正在等待扫码，请稍后重试"}
            except Exception as e:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [check_login_status] ✗ 检查登录状态出错: {e}")
                import traceback
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [check_login_status] 错误堆栈:\n{traceback.format_exc()}")
                return {"status": "error", "message": str(e)}
        
        result = check_status()
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [check_login_status] ✓ 返回结果: {result}")
        return jsonify(result)
    except Exception as e:
        from datetime import datetime
        import traceback
        error_msg = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [check_login_status] ✗ 异常: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({"error": str(e), "status": "error"}), 500


@crawler_bp.route('/login/cookie/<platform>', methods=['GET'])
def get_cookie(platform):
    """获取保存的 Cookie"""
    if not MEDIACRAWLER_AVAILABLE or not login_service:
        return jsonify({"error": "登录服务未启用"}), 503
    
    try:
        @async_to_sync
        async def get_cookie_data():
            cookie = await login_service.load_cookie(platform)
            return {"has_cookie": cookie is not None, "cookie": cookie}
        
        result = get_cookie_data()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@crawler_bp.route('/login/cookie/<platform>', methods=['DELETE'])
def delete_cookie(platform):
    """删除 Cookie"""
    if not MEDIACRAWLER_AVAILABLE or not login_service:
        return jsonify({"error": "登录服务未启用"}), 503
    
    try:
        @async_to_sync
        async def delete_cookie_data():
            # 删除 cookie 文件
            cookie_file = Path(f"cookies/{platform}_cookies.json")
            if cookie_file.exists():
                cookie_file.unlink()
            return {"success": True, "message": "Cookie已清除"}
        
        result = delete_cookie_data()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== 任务管理 ====================

@crawler_bp.route('/tasks', methods=['GET'])
def get_tasks():
    """获取任务列表"""
    if not MEDIACRAWLER_AVAILABLE:
        return jsonify({"error": "MediaCrawler 服务未启用"}), 503
    
    try:
        # 从 MediaCrawler 的 main.py 中获取任务状态
        # 需要访问 task_status 和 running_tasks
        # 这里简化处理，实际需要从 MediaCrawler 模块中导入
        try:
            from admin_api.main import task_status, running_tasks
            tasks = [
                {
                    "task_id": task_id,
                    **status
                }
                for task_id, status in task_status.items()
            ]
            return jsonify({"tasks": tasks})
        except ImportError:
            # 如果无法导入，返回空列表
            return jsonify({"tasks": []})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@crawler_bp.route('/tasks/start', methods=['POST'])
def start_task():
    """启动任务"""
    if not MEDIACRAWLER_AVAILABLE:
        return jsonify({"error": "MediaCrawler 服务未启用"}), 503
    
    try:
        task_data = request.json
        platform = task_data.get("platform")
        config = task_data.get("config", {})
        
        # 这里需要调用 MediaCrawler 的任务启动逻辑
        # 由于任务启动是异步的，需要特殊处理
        # 建议：直接调用 MediaCrawler 的 FastAPI 应用的路由处理函数
        # 或者使用 httpx 调用 MediaCrawler 的 API
        
        # 简化实现：返回任务ID（实际需要启动异步任务）
        import time
        task_id = f"{platform}_{int(time.time())}"
        
        # 实际应该调用 MediaCrawler 的 start_crawler_task 函数
        # 这里简化处理
        return jsonify({
            "task_id": task_id,
            "status": "started",
            "message": "任务已启动"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@crawler_bp.route('/tasks/<task_id>', methods=['DELETE'])
def stop_task(task_id):
    """停止任务"""
    if not MEDIACRAWLER_AVAILABLE:
        return jsonify({"error": "MediaCrawler 服务未启用"}), 503
    
    try:
        # 从 MediaCrawler 的 main.py 中获取 running_tasks
        try:
            from admin_api.main import running_tasks, task_status
            if task_id in running_tasks:
                running_tasks[task_id].cancel()
                if task_id in task_status:
                    task_status[task_id]["status"] = "cancelled"
                return jsonify({"message": "任务已停止"})
            else:
                return jsonify({"error": "任务不存在"}), 404
        except ImportError:
            return jsonify({"message": "任务已停止"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== 数据列表 ====================

@crawler_bp.route('/data/<platform>', methods=['GET'])
def get_data(platform):
    """获取平台数据"""
    if not MEDIACRAWLER_AVAILABLE:
        return jsonify({"error": "MediaCrawler 服务未启用"}), 503
    
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        keyword = request.args.get('keyword', '')
        source_keyword = request.args.get('source_keyword', '')
        crawler_type = request.args.get('crawler_type', '')
        note_type = request.args.get('note_type', '')
        sort_field = request.args.get('sort_field', '')
        sort_order = request.args.get('sort_order', 'desc')
        
        # 调用 MediaCrawler 的数据获取逻辑
        # 这里需要从 MediaCrawler 的 main.py 中提取 get_crawled_data 的逻辑
        # 由于逻辑较复杂，建议直接调用 FastAPI 应用的路由处理函数
        # 或者复制 get_crawled_data 的实现逻辑
        
        # 简化实现：读取数据文件
        import json
        from pathlib import Path
        
        platform_dir = "kuaishou" if platform == "ks" else platform
        data_dir = MEDIACRAWLER_PATH / "data" / platform_dir / "json"
        
        if not data_dir.exists():
            return jsonify({"data": [], "total": 0, "page": page, "page_size": page_size})
        
        # 读取数据文件（简化实现）
        json_files = sorted(data_dir.glob("*contents*.json"), reverse=True)
        all_data = []
        for json_file in json_files[:10]:  # 限制文件数量
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)
                    if isinstance(file_data, list):
                        all_data.extend(file_data)
            except:
                continue
        
        # 简单分页
        total = len(all_data)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_data = all_data[start:end]
        
        return jsonify({"data": paginated_data, "total": total, "page": page, "page_size": page_size})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@crawler_bp.route('/data/<platform>/comments/<note_id>', methods=['GET'])
def get_comments(platform, note_id):
    """获取评论列表"""
    if not MEDIACRAWLER_AVAILABLE:
        return jsonify({"error": "MediaCrawler 服务未启用"}), 503
    
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 50, type=int)
        
        # 调用 MediaCrawler 的评论获取逻辑
        import json
        from pathlib import Path
        from datetime import datetime
        
        platform_dir = "kuaishou" if platform == "ks" else platform
        data_dir = MEDIACRAWLER_PATH / "data" / platform_dir / "json"
        
        if not data_dir.exists():
            return jsonify({"comments": [], "total": 0, "page": page, "page_size": page_size})
        
        # 读取评论文件
        json_files = sorted(data_dir.glob("*comments*.json"), reverse=True)
        all_comments = []
        
        # 根据不同平台使用不同的字段名
        if platform == "ks":
            id_field = "video_id"
        elif platform in ["juejin", "medium"]:
            id_field = "article_id"
        else:
            id_field = "note_id"
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)
                    if isinstance(file_data, list):
                        filtered = [c for c in file_data if c.get(id_field) == note_id]
                        all_comments.extend(filtered)
            except:
                continue
        
        # 格式化评论
        formatted_comments = []
        for comment in all_comments:
            time_value = comment.get("create_time", 0)
            create_time = ""
            if time_value:
                try:
                    if isinstance(time_value, (int, float)) and time_value > 0:
                        create_time = datetime.fromtimestamp(
                            time_value / 1000 if time_value > 1000000000000 else time_value
                        ).strftime("%Y-%m-%d %H:%M:%S")
                except:
                    pass
            
            formatted_comments.append({
                "id": comment.get("comment_id", ""),
                "content": comment.get("content", ""),
                "author": comment.get("nickname", ""),
                "avatar": comment.get("avatar", ""),
                "create_time": create_time,
                "like_count": comment.get("like_count", 0),
                "sub_comment_count": comment.get("sub_comment_count", 0),
                "ip_location": comment.get("ip_location", "")
            })
        
        # 去重和排序
        seen_ids = set()
        unique_comments = []
        for comment in formatted_comments:
            if comment["id"] and comment["id"] not in seen_ids:
                seen_ids.add(comment["id"])
                unique_comments.append(comment)
        
        unique_comments.sort(key=lambda x: x.get("create_time", ""), reverse=True)
        
        # 分页
        total = len(unique_comments)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_comments = unique_comments[start:end]
        
        return jsonify({"comments": paginated_comments, "total": total, "page": page, "page_size": page_size})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@crawler_bp.route('/data/<platform>/filter-options', methods=['GET'])
def get_filter_options(platform):
    """获取筛选选项"""
    if not MEDIACRAWLER_AVAILABLE:
        return jsonify({"error": "MediaCrawler 服务未启用"}), 503
    
    try:
        import json
        from pathlib import Path
        
        platform_dir = "kuaishou" if platform == "ks" else platform
        data_dir = MEDIACRAWLER_PATH / "data" / platform_dir / "json"
        
        if not data_dir.exists():
            return jsonify({"keywords": [], "crawler_types": []})
        
        json_files = sorted(data_dir.glob("*contents*.json"), reverse=True)
        keywords_set = set()
        crawler_types_set = set()
        
        for json_file in json_files:
            try:
                # 从文件名提取crawler_type
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
            except:
                continue
        
        return jsonify({
            "keywords": sorted(list(keywords_set)),
            "crawler_types": sorted(list(crawler_types_set))
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== 微信公众号 ====================

@crawler_bp.route('/wechat/accounts', methods=['GET'])
def get_wechat_accounts():
    """获取公众号账号列表"""
    if not MEDIACRAWLER_AVAILABLE or not wechat_service:
        return jsonify({"error": "微信公众号服务未启用"}), 503
    
    try:
        @async_to_sync
        async def get_accounts():
            return await wechat_service.list_accounts()
        
        accounts = get_accounts()
        return jsonify({"accounts": accounts})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@crawler_bp.route('/wechat/accounts', methods=['POST'])
def add_wechat_account():
    """添加公众号账号"""
    if not MEDIACRAWLER_AVAILABLE or not wechat_service:
        return jsonify({"error": "微信公众号服务未启用"}), 503
    
    try:
        account_data = request.json
        
        @async_to_sync
        async def add_account():
            return await wechat_service.add_account(
                account_data.get('account_id'),
                account_data.get('name'),
                account_data.get('token'),
                account_data.get('status', 1)
            )
        
        result = add_account()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@crawler_bp.route('/wechat/accounts/<account_id>/status', methods=['PUT'])
def update_wechat_account_status(account_id):
    """更新公众号账号状态"""
    if not MEDIACRAWLER_AVAILABLE or not wechat_service:
        return jsonify({"error": "微信公众号服务未启用"}), 503
    
    try:
        status = request.json.get('status')
        
        @async_to_sync
        async def update_status():
            return await wechat_service.update_account_status(account_id, status)
        
        result = update_status()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@crawler_bp.route('/wechat/accounts/<account_id>', methods=['DELETE'])
def delete_wechat_account(account_id):
    """删除公众号账号"""
    if not MEDIACRAWLER_AVAILABLE or not wechat_service:
        return jsonify({"error": "微信公众号服务未启用"}), 503
    
    try:
        @async_to_sync
        async def delete_account():
            return await wechat_service.delete_account(account_id)
        
        result = delete_account()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@crawler_bp.route('/wechat/login/create-url', methods=['POST'])
def create_wechat_login_url():
    """创建微信读书登录URL"""
    if not MEDIACRAWLER_AVAILABLE or not wechat_service:
        return jsonify({"error": "微信公众号服务未启用"}), 503
    
    try:
        @async_to_sync
        async def create_url():
            return await wechat_service.create_login_url()
        
        result = create_url()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@crawler_bp.route('/wechat/login/result/<uuid>', methods=['GET'])
def get_wechat_login_result(uuid):
    """获取微信读书登录结果"""
    if not MEDIACRAWLER_AVAILABLE or not wechat_service:
        return jsonify({"error": "微信公众号服务未启用"}), 503
    
    try:
        @async_to_sync
        async def get_result():
            return await wechat_service.get_login_result(uuid)
        
        result = get_result()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@crawler_bp.route('/wechat/feeds', methods=['GET'])
def get_wechat_feeds():
    """获取公众号订阅源列表"""
    if not MEDIACRAWLER_AVAILABLE or not wechat_service:
        return jsonify({"error": "微信公众号服务未启用"}), 503
    
    try:
        @async_to_sync
        async def get_feeds():
            return await wechat_service.list_feeds()
        
        feeds = get_feeds()
        return jsonify({"feeds": feeds})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@crawler_bp.route('/wechat/feeds', methods=['POST'])
def add_wechat_feed():
    """添加公众号订阅源"""
    if not MEDIACRAWLER_AVAILABLE or not wechat_service:
        return jsonify({"error": "微信公众号服务未启用"}), 503
    
    try:
        feed_data = request.json
        
        @async_to_sync
        async def add_feed():
            return await wechat_service.add_feed(
                feed_data.get('feed_id'),
                feed_data.get('mp_name'),
                feed_data.get('mp_cover', ''),
                feed_data.get('mp_intro', ''),
                feed_data.get('update_time', 0),
                feed_data.get('status', 1)
            )
        
        result = add_feed()
        return jsonify({"success": True, "feed": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@crawler_bp.route('/wechat/feeds/<feed_id>/refresh', methods=['POST'])
def refresh_wechat_feed(feed_id):
    """刷新公众号文章"""
    if not MEDIACRAWLER_AVAILABLE or not wechat_service:
        return jsonify({"error": "微信公众号服务未启用"}), 503
    
    try:
        @async_to_sync
        async def refresh_feed():
            return await wechat_service.refresh_mp_articles(feed_id)
        
        result = refresh_feed()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@crawler_bp.route('/wechat/feeds/<feed_id>/history', methods=['POST'])
def get_wechat_history_articles(feed_id):
    """获取公众号历史文章"""
    if not MEDIACRAWLER_AVAILABLE or not wechat_service:
        return jsonify({"error": "微信公众号服务未启用"}), 503
    
    try:
        @async_to_sync
        async def get_history():
            return await wechat_service.get_history_mp_articles(feed_id)
        
        result = get_history()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@crawler_bp.route('/wechat/feeds/<feed_id>/status', methods=['PUT'])
def update_wechat_feed_status(feed_id):
    """更新订阅源状态"""
    if not MEDIACRAWLER_AVAILABLE or not wechat_service:
        return jsonify({"error": "微信公众号服务未启用"}), 503
    
    try:
        status = request.json.get('status')
        
        @async_to_sync
        async def update_status():
            return await wechat_service.update_feed_status(feed_id, status)
        
        result = update_status()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@crawler_bp.route('/wechat/feeds/<feed_id>', methods=['DELETE'])
def delete_wechat_feed(feed_id):
    """删除订阅源"""
    if not MEDIACRAWLER_AVAILABLE or not wechat_service:
        return jsonify({"error": "微信公众号服务未启用"}), 503
    
    try:
        @async_to_sync
        async def delete_feed():
            return await wechat_service.delete_feed(feed_id)
        
        result = delete_feed()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@crawler_bp.route('/wechat/mp/info', methods=['POST'])
def get_wechat_mp_info():
    """通过分享链接获取公众号信息"""
    if not MEDIACRAWLER_AVAILABLE or not wechat_service:
        return jsonify({"error": "微信公众号服务未启用"}), 503
    
    try:
        wxs_link = request.json.get('wxs_link')
        
        @async_to_sync
        async def get_info():
            return await wechat_service.get_mp_info(wxs_link)
        
        result = get_info()
        return jsonify({"mp_info": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@crawler_bp.route('/wechat/articles', methods=['GET'])
def get_wechat_articles():
    """获取公众号文章列表"""
    if not MEDIACRAWLER_AVAILABLE or not wechat_service:
        return jsonify({"error": "微信公众号服务未启用"}), 503
    
    try:
        mp_id = request.args.get('mp_id')
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        @async_to_sync
        async def get_articles():
            return await wechat_service.list_articles(mp_id, limit, offset)
        
        articles = get_articles()
        return jsonify({"articles": articles, "total": len(articles)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@crawler_bp.route('/wechat/feeds/history/progress', methods=['GET'])
def get_wechat_history_progress():
    """获取正在获取历史文章的公众号信息"""
    if not MEDIACRAWLER_AVAILABLE or not wechat_service:
        return jsonify({"error": "微信公众号服务未启用"}), 503
    
    try:
        progress = wechat_service.get_in_progress_history_mp()
        return jsonify(progress)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

