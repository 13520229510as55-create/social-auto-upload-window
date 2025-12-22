# -*- coding: utf-8 -*-
"""
混合应用：FastAPI + Flask
- 爬虫功能使用 FastAPI（直接异步，性能更好）
- 其他功能保持 Flask（向后兼容）
"""
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware
from starlette.responses import JSONResponse
import asyncio

# 添加 MediaCrawler 路径
MEDIACRAWLER_PATH = Path(__file__).parent / 'MediaCrawler'
if MEDIACRAWLER_PATH.exists():
    sys.path.insert(0, str(MEDIACRAWLER_PATH))
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
            sys.path.insert(0, str(MEDIACRAWLER_PATH))
            print(f"✓ 使用备用 MediaCrawler 路径: {MEDIACRAWLER_PATH}")
            break

# 导入 Flask 应用（延迟导入，避免循环依赖）
def get_flask_app():
    """获取 Flask 应用实例"""
    from sau_backend import app as flask_app
    return flask_app

# 创建 FastAPI 应用
fastapi_app = FastAPI(
    title="Social Auto Upload API",
    description="混合应用：FastAPI（爬虫）+ Flask（其他功能）",
    version="2.0.0"
)

# 配置 CORS
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 尝试导入 MediaCrawler 服务
MEDIACRAWLER_AVAILABLE = False
login_service = None
wechat_service = None

try:
    from admin_api.login_service import login_service
    if login_service is None:
        from admin_api.login_service import LoginService
        login_service = LoginService()
    print("✓ login_service 导入成功")
    MEDIACRAWLER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ login_service 导入失败: {e}")
    login_service = None
except Exception as e:
    print(f"⚠️ login_service 导入出错: {e}")
    login_service = None

try:
    from admin_api.wechat_service import wechat_service
    if wechat_service is None:
        from admin_api.wechat_service import WechatService
        wechat_service = WechatService()
    print("✓ wechat_service 导入成功")
    MEDIACRAWLER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ wechat_service 导入失败: {e}")
    wechat_service = None
except Exception as e:
    print(f"⚠️ wechat_service 导入出错: {e}")
    wechat_service = None

# ==================== FastAPI 路由（爬虫功能）====================

@fastapi_app.get("/api/crawler/login/status/{qrcode_id}")
async def check_login_status(qrcode_id: str):
    """
    检查登录状态 - 直接使用 FastAPI 异步
    无需 async_to_sync 转换，性能更好
    """
    from datetime import datetime
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [FastAPI] 检查登录状态: {qrcode_id}")
    
    if not MEDIACRAWLER_AVAILABLE or not login_service:
        raise HTTPException(status_code=503, detail="登录服务未启用")
    
    try:
        result = await asyncio.wait_for(
            login_service.check_login_status(qrcode_id),
            timeout=30.0
        )
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [FastAPI] ✓ 登录状态: {result.get('status', 'unknown')}")
        return result
    except asyncio.TimeoutError:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [FastAPI] ⏱️ 检查登录状态超时")
        return {"status": "pending", "message": "正在等待扫码，请稍后重试"}
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [FastAPI] ✗ 错误: {e}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@fastapi_app.post("/api/crawler/login/qrcode")
async def get_qrcode(platform: str, force: bool = False):
    """
    获取登录二维码 - 直接使用 FastAPI 异步
    """
    from datetime import datetime
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [FastAPI] 获取二维码: {platform}")
    
    if not MEDIACRAWLER_AVAILABLE or not login_service:
        raise HTTPException(status_code=503, detail="登录服务未启用")
    
    try:
        result = await login_service.get_qrcode(platform, force=force)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [FastAPI] ✓ 二维码获取成功")
        return result
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [FastAPI] ✗ 错误: {e}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@fastapi_app.get("/api/crawler/login/cookie/{platform}")
async def get_cookie(platform: str):
    """
    获取保存的 Cookie - 直接使用 FastAPI 异步
    """
    if not MEDIACRAWLER_AVAILABLE or not login_service:
        raise HTTPException(status_code=503, detail="登录服务未启用")
    
    try:
        cookie = await login_service.load_cookie(platform)
        if cookie:
            return {
                "has_cookie": True,
                "cookie": cookie
            }
        else:
            return {
                "has_cookie": False,
                "cookie": None
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@fastapi_app.delete("/api/crawler/login/cookie/{platform}")
async def delete_cookie(platform: str):
    """
    删除 Cookie - 直接使用 FastAPI 异步
    """
    if not MEDIACRAWLER_AVAILABLE or not login_service:
        raise HTTPException(status_code=503, detail="登录服务未启用")
    
    try:
        await login_service.delete_cookie(platform)
        return {"success": True, "message": "Cookie 已删除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 挂载 Flask 应用 ====================

# 获取 Flask 应用
flask_app = get_flask_app()

# 注意：FastAPI 的路由优先级高于挂载的 WSGI 应用
# 所以 /api/crawler/* 会先匹配 FastAPI 路由
# 其他路由会转发到 Flask 应用

# 挂载 Flask 应用到根路径（处理所有非 FastAPI 路由）
fastapi_app.mount("/", WSGIMiddleware(flask_app))

# 或者更精确的控制（只挂载特定路径）
# fastapi_app.mount("/api", WSGIMiddleware(flask_app))  # 只挂载 /api 下的非 crawler 路由

# ==================== 主应用 ====================

# 导出主应用（用于 uvicorn）
app = fastapi_app

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🚀 启动混合应用：FastAPI + Flask")
    print("=" * 60)
    print("📡 FastAPI 路由: /api/crawler/* (异步，性能更好)")
    print("📡 Flask 路由: 其他所有路由 (向后兼容)")
    print("=" * 60)
    uvicorn.run(
        "hybrid_app:app",
        host="0.0.0.0",
        port=5409,
        reload=False,
        log_level="info"
    )

