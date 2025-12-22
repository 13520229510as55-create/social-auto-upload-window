# 爬虫管理 FastAPI 使用说明

## 📋 架构说明

### 设计原则
- ✅ **爬虫管理模块**：使用 FastAPI（与 `/Users/a58/MediaCrawler` 保持一致）
- ✅ **制作中心、发布中心等**：保持 Flask（向后兼容）

### 架构图

```
┌─────────────────────────────────────────┐
│     混合应用 (hybrid_app.py)             │
│     Port: 5409                           │
├─────────────────────────────────────────┤
│  FastAPI (爬虫管理)                      │
│  /api/crawler/*                          │
│  - 与 MediaCrawler 保持一致               │
│  - 直接异步，性能更好                     │
├─────────────────────────────────────────┤
│  Flask (其他功能)                         │
│  /api/production/* (制作中心)             │
│  /api/publish/* (发布中心)                │
│  /api/getAccounts, /api/postVideo 等     │
└─────────────────────────────────────────┘
```

## 🚀 启动方式

### 方式1：使用混合应用（推荐）

```bash
# 安装依赖
pip install fastapi uvicorn[standard]

# 启动混合应用
python hybrid_app.py
```

### 方式2：使用 uvicorn

```bash
uvicorn hybrid_app:app --host 0.0.0.0 --port 5409
```

### 方式3：继续使用 Flask（向后兼容）

```bash
# 不设置环境变量，继续使用 Flask 蓝图
python sau_backend.py
```

## 📁 文件说明

### `crawler_fastapi.py`
- **作用**：爬虫管理 FastAPI 应用
- **路由前缀**：`/api/crawler/*`
- **特点**：与 MediaCrawler 的 FastAPI 实现保持一致

### `hybrid_app.py`
- **作用**：混合应用主入口
- **功能**：
  - 挂载 `crawler_fastapi.py` 处理爬虫管理
  - 挂载 Flask 应用处理其他功能

### `sau_backend.py`
- **修改**：添加环境变量检查，如果使用 FastAPI 则不注册 Flask 蓝图
- **保持**：制作中心、发布中心等功能不变

## 🔄 路由映射

### FastAPI 路由（爬虫管理）

| 路由 | 方法 | 说明 |
|------|------|------|
| `/api/crawler/login/qrcode` | POST | 获取登录二维码 |
| `/api/crawler/login/status/{qrcode_id}` | GET | 检查登录状态 |
| `/api/crawler/login/cookie/{platform}` | GET | 获取 Cookie |
| `/api/crawler/login/cookie/{platform}` | DELETE | 删除 Cookie |
| `/api/crawler/platforms` | GET | 获取平台列表 |
| `/api/crawler/dashboard/stats` | GET | 获取统计信息 |
| `/api/crawler/config/{platform}` | GET | 获取配置 |
| `/api/crawler/config/{platform}` | POST | 保存配置 |

### Flask 路由（其他功能）

| 路由 | 方法 | 说明 |
|------|------|------|
| `/api/production/*` | - | 制作中心 |
| `/api/publish/*` | - | 发布中心 |
| `/api/getAccounts` | GET | 获取账号列表 |
| `/api/postVideo` | POST | 发布视频 |
| `/api/postImageText` | POST | 发布图文 |
| ... | ... | 其他功能保持不变 |

## ✅ 优势

### 1. 与 MediaCrawler 保持一致
- ✅ 使用相同的 FastAPI 框架
- ✅ 相同的路由结构和参数
- ✅ 相同的错误处理方式
- ✅ 便于同步 MediaCrawler 的更新

### 2. 性能提升
- ✅ 直接异步，无需 `async_to_sync` 转换
- ✅ 减少性能开销
- ✅ 更好的并发处理能力

### 3. 代码简化
- ✅ 移除 `async_to_sync` 包装器
- ✅ 代码更简洁，易于维护
- ✅ 自动生成 API 文档（`/docs`）

### 4. 向后兼容
- ✅ 制作中心、发布中心等功能保持不变
- ✅ 前端无需改动
- ✅ 可以逐步迁移其他功能

## 📝 迁移检查清单

- [x] 创建 `crawler_fastapi.py`（爬虫管理 FastAPI 应用）
- [x] 创建 `hybrid_app.py`（混合应用主入口）
- [x] 修改 `sau_backend.py`（添加环境变量检查）
- [ ] 测试爬虫管理接口
- [ ] 测试制作中心、发布中心接口
- [ ] 更新启动脚本
- [ ] 更新部署文档

## 🔍 测试

### 测试爬虫管理接口（FastAPI）

```bash
# 获取二维码
curl -X POST "http://localhost:5409/api/crawler/login/qrcode?platform=xhs&force=false"

# 检查登录状态
curl "http://localhost:5409/api/crawler/login/status/xhs_12345"

# 获取 Cookie
curl "http://localhost:5409/api/crawler/login/cookie/xhs"
```

### 测试其他接口（Flask）

```bash
# 获取账号列表
curl "http://localhost:5409/api/getAccounts"

# 发布视频
curl -X POST "http://localhost:5409/api/postVideo" \
  -H "Content-Type: application/json" \
  -d '{"type": 1, "title": "测试", ...}'
```

### 查看 API 文档

```
http://localhost:5409/docs  # Swagger UI（只显示 FastAPI 路由）
```

## ⚠️ 注意事项

1. **路由优先级**
   - FastAPI 路由优先于挂载的 Flask 应用
   - `/api/crawler/*` 会先匹配 FastAPI 路由
   - 其他路由会转发到 Flask 应用

2. **环境变量**
   - 使用 `hybrid_app.py` 时，会自动设置 `USE_FASTAPI_FOR_CRAWLER=1`
   - 使用 `sau_backend.py` 时，不设置该变量，使用 Flask 蓝图

3. **CORS 配置**
   - FastAPI 和 Flask 都需要配置 CORS
   - 确保配置一致

4. **错误处理**
   - FastAPI 使用 `HTTPException`
   - Flask 使用 `jsonify` 和状态码
   - 确保错误响应格式一致（前端兼容）

## 🎯 下一步

1. **逐步迁移其他爬虫路由**
   - 任务管理（`/api/crawler/tasks/*`）
   - 数据管理（`/api/crawler/data/*`）
   - 微信公众号（`/api/crawler/wechat/*`）

2. **性能优化**
   - 监控 FastAPI 路由性能
   - 对比 Flask 蓝图和 FastAPI 的性能差异

3. **文档完善**
   - 更新 API 文档
   - 添加使用示例

