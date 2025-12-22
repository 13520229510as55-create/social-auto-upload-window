# -*- coding: utf-8 -*-
"""
混合应用：FastAPI + Flask
- 爬虫管理模块使用 FastAPI（与 MediaCrawler 保持一致）
- 制作中心、发布中心等其他模块保持 Flask（向后兼容）
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware

# 导入爬虫管理 FastAPI 应用（与 MediaCrawler 保持一致）
from crawler_fastapi import crawler_app

# 导入 Flask 应用（延迟导入，避免循环依赖）
def get_flask_app():
    """获取 Flask 应用实例（禁用爬虫蓝图）"""
    import os
    # 设置环境变量，告诉 Flask 不要注册爬虫蓝图
    os.environ['USE_FASTAPI_FOR_CRAWLER'] = '1'
    from sau_backend import app as flask_app
    return flask_app

# 创建主 FastAPI 应用
main_app = FastAPI(
    title="Social Auto Upload API",
    description="混合应用：FastAPI（爬虫管理）+ Flask（制作中心、发布中心等）",
    version="2.0.0"
)

# 配置 CORS
main_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载爬虫管理 FastAPI 应用（与 MediaCrawler 保持一致）
main_app.mount("/api/crawler", crawler_app)

# 获取 Flask 应用（处理其他所有路由）
flask_app = get_flask_app()

# 挂载 Flask 应用到根路径（处理所有非爬虫路由）
# 注意：FastAPI 路由优先级高于挂载的 WSGI 应用
# 所以 /api/crawler/* 会先匹配 FastAPI 路由
# 其他路由（/api/production/*, /api/publish/* 等）会转发到 Flask 应用
main_app.mount("/", WSGIMiddleware(flask_app))

# ==================== 主应用 ====================

# 导出主应用（用于 uvicorn）
app = main_app

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🚀 启动混合应用：FastAPI + Flask")
    print("=" * 60)
    print("📡 FastAPI 路由: /api/crawler/* (爬虫管理，与 MediaCrawler 保持一致)")
    print("📡 Flask 路由: 其他所有路由 (制作中心、发布中心等)")
    print("=" * 60)
    uvicorn.run(
        "hybrid_app:app",
        host="0.0.0.0",
        port=5409,
        reload=False,
        log_level="info"
    )

