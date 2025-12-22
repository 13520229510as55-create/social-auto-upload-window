# 迁移到 FastAPI 指南

## 🎯 目标

将爬虫功能从 Flask 蓝图迁移到 FastAPI，提升性能并简化代码。

## 📊 对比

### 当前架构（Flask 蓝图）

```python
# crawler_api.py
@crawler_bp.route('/login/status/<qrcode_id>', methods=['GET'])
def check_login_status(qrcode_id):
    @async_to_sync  # ❌ 需要转换，有性能开销
    async def check_status():
        result = await login_service.check_login_status(qrcode_id)
        return result
    return jsonify(check_status())
```

**问题：**
- ❌ 需要 `async_to_sync` 转换
- ❌ 性能开销（异步转同步）
- ❌ 代码复杂（嵌套函数）

### 新架构（FastAPI）

```python
# hybrid_app.py
@fastapi_app.get("/api/crawler/login/status/{qrcode_id}")
async def check_login_status(qrcode_id: str):  # ✅ 直接异步
    result = await login_service.check_login_status(qrcode_id)
    return result  # ✅ 自动 JSON 序列化
```

**优势：**
- ✅ 直接异步，无转换开销
- ✅ 代码简洁
- ✅ 自动 API 文档生成
- ✅ 类型提示和验证

## 🚀 迁移步骤

### 步骤 1：安装依赖

```bash
pip install fastapi uvicorn[standard]
```

### 步骤 2：修改启动方式

#### 选项 A：使用混合应用（推荐）

**修改启动脚本：**

```bash
# 之前
python sau_backend.py

# 之后
python hybrid_app.py
# 或
uvicorn hybrid_app:app --host 0.0.0.0 --port 5409
```

#### 选项 B：修改 `sau_backend.py`（不推荐，改动大）

需要大量修改现有代码，风险较高。

### 步骤 3：禁用 Flask 蓝图中的爬虫路由

在 `sau_backend.py` 中注释掉蓝图注册：

```python
# 注册 MediaCrawler 爬虫管理蓝图
# try:
#     from crawler_api import crawler_bp
#     app.register_blueprint(crawler_bp)
#     print("✓ MediaCrawler 爬虫管理蓝图已注册")
# except ImportError as e:
#     print(f"⚠️ MediaCrawler 爬虫管理蓝图注册失败: {e}")
```

**或者**在 `crawler_api.py` 中条件注册：

```python
# 如果通过 FastAPI 运行，不注册蓝图
if not os.getenv('USE_FASTAPI'):
    app.register_blueprint(crawler_bp)
```

### 步骤 4：测试

1. **启动服务**
   ```bash
   python hybrid_app.py
   ```

2. **测试爬虫接口**
   ```bash
   curl http://localhost:5409/api/crawler/login/status/xhs_12345
   ```

3. **测试 Flask 接口**
   ```bash
   curl http://localhost:5409/api/getAccounts
   ```

4. **查看 API 文档**
   ```
   http://localhost:5409/docs  # Swagger UI
   http://localhost:5409/redoc  # ReDoc
   ```

## 📝 需要迁移的路由

从 `crawler_api.py` 迁移到 `hybrid_app.py`：

- ✅ `/api/crawler/login/status/{qrcode_id}` - 已迁移
- ✅ `/api/crawler/login/qrcode` - 已迁移
- ✅ `/api/crawler/login/cookie/{platform}` - 已迁移
- ✅ `/api/crawler/login/cookie/{platform}` (DELETE) - 已迁移
- ⏳ `/api/crawler/dashboard/stats` - 待迁移
- ⏳ `/api/crawler/platforms` - 待迁移
- ⏳ `/api/crawler/config/{platform}` - 待迁移
- ⏳ `/api/crawler/tasks/*` - 待迁移
- ⏳ `/api/crawler/data/*` - 待迁移
- ⏳ `/api/crawler/wechat/*` - 待迁移

## 🔄 回滚方案

如果遇到问题，可以快速回滚：

1. **恢复 Flask 蓝图注册**
   ```python
   from crawler_api import crawler_bp
   app.register_blueprint(crawler_bp)
   ```

2. **使用原启动方式**
   ```bash
   python sau_backend.py
   ```

## ⚠️ 注意事项

1. **路由优先级**
   - FastAPI 路由优先于挂载的 Flask 应用
   - 确保 `/api/crawler/*` 路由在 FastAPI 中定义

2. **CORS 配置**
   - FastAPI 和 Flask 都需要配置 CORS
   - 确保配置一致

3. **错误处理**
   - FastAPI 使用 `HTTPException`
   - Flask 使用 `jsonify` 和状态码
   - 确保错误响应格式一致

4. **会话和状态**
   - Flask 和 FastAPI 的会话可能不共享
   - 如果使用会话，需要统一管理

## 📈 性能对比

| 指标 | Flask 蓝图 | FastAPI |
|------|-----------|---------|
| 异步转换开销 | 有 | 无 |
| 并发处理能力 | 中等 | 高 |
| 响应时间 | 较慢 | 更快 |
| 代码复杂度 | 高（嵌套） | 低（直接） |

## ✅ 迁移检查清单

- [ ] 安装 FastAPI 依赖
- [ ] 创建 `hybrid_app.py`
- [ ] 迁移爬虫路由到 FastAPI
- [ ] 禁用 Flask 蓝图中的爬虫路由
- [ ] 测试所有爬虫接口
- [ ] 测试 Flask 接口（确保不受影响）
- [ ] 更新启动脚本
- [ ] 更新部署文档
- [ ] 性能测试和对比

## 🎉 完成后的收益

1. **性能提升**：爬虫功能直接使用异步，无转换开销
2. **代码简化**：移除 `async_to_sync` 包装器
3. **自动文档**：FastAPI 自动生成 API 文档
4. **类型安全**：使用 Pydantic 进行数据验证
5. **更好的开发体验**：IDE 支持更好，类型提示更完善

