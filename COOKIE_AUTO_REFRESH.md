# Cookie 自动刷新功能说明

## 功能概述

系统已实现 Cookie 自动刷新功能，每 **2 小时**自动刷新所有有效账号的 Cookie，以保持登录状态。

## 实现原理

1. **定时任务**：使用 `schedule` 库实现定时任务，每 2 小时执行一次
2. **后台线程**：在 Flask 应用启动时，自动启动一个后台守护线程运行定时任务
3. **并发刷新**：使用 `asyncio.gather` 并发刷新所有账号的 Cookie，提高效率
4. **智能检测**：访问平台页面时，自动检测 Cookie 是否有效，如果已失效则不保存

## 支持的平台

- ✅ 小红书 (type=1)
- ✅ 视频号 (type=2)
- ✅ 抖音 (type=3)
- ✅ 快手 (type=4)
- ✅ 百家号 (type=5)
- ✅ TikTok (type=6)

## 工作流程

1. **定时触发**：每 2 小时自动触发一次刷新任务
2. **查询账号**：从数据库查询所有 `status=1`（有效）的账号
3. **并发刷新**：为每个账号创建刷新任务，并发执行
4. **访问页面**：访问对应平台的主页/创作页面以刷新 Cookie
5. **保存 Cookie**：如果 Cookie 仍然有效，保存更新后的 Cookie 到文件
6. **记录日志**：记录刷新结果到对应的平台日志文件

## 日志记录

刷新过程会记录到各平台的日志文件中：
- 小红书：`logs/xiaohongshu.log`
- 视频号：`logs/tencent.log`
- 抖音：`logs/douyin.log`
- 快手：`logs/kuaishou.log`
- 百家号：`logs/baijiahao.log`
- TikTok：`logs/tiktok.log`

日志格式示例：
```
[Cookie刷新] 账号名称 (cookie文件.json) - 刷新成功
[Cookie刷新] 账号名称 (cookie文件.json) - 刷新失败（可能 cookie 已失效）
```

## 启动方式

定时任务会在 Flask 应用启动时自动启动，无需手动操作。

启动日志示例：
```
🔄 [2025-12-16 11:00:00] Cookie 自动刷新定时任务已启动（每 2 小时执行一次）
✅ Cookie 刷新定时任务线程已启动
```

## 刷新执行日志

每次刷新执行时，会在控制台输出：
```
🔄 [2025-12-16 11:00:00] 开始自动刷新所有账号的 Cookie...
  📋 找到 5 个有效账号，开始刷新...
  ✅ Cookie 刷新完成: 4 个成功, 1 个失败
```

## 配置说明

### 修改刷新间隔

如果需要修改刷新间隔，编辑 `sau_backend.py` 中的以下代码：

```python
# 每 2 小时执行一次
schedule.every(2).hours.do(run_cookie_refresh_task)
```

可以修改为：
- `schedule.every(1).hours.do(...)` - 每 1 小时
- `schedule.every(30).minutes.do(...)` - 每 30 分钟
- `schedule.every(3).hours.do(...)` - 每 3 小时

### 立即执行测试

如果需要立即测试刷新功能，可以在 `sau_backend.py` 的 `start_cookie_refresh_scheduler()` 函数中添加：

```python
# 立即执行一次（用于测试）
run_cookie_refresh_task()
```

## 注意事项

1. **Cookie 失效处理**：如果检测到 Cookie 已失效（跳转到登录页），不会保存无效的 Cookie
2. **并发执行**：所有账号的刷新是并发执行的，不会阻塞主应用
3. **后台运行**：定时任务在后台守护线程中运行，不会影响主应用性能
4. **错误处理**：即使某个账号刷新失败，也不会影响其他账号的刷新

## 故障排查

### 定时任务未启动

检查启动日志是否包含：
```
🔄 [时间] Cookie 自动刷新定时任务已启动（每 2 小时执行一次）
✅ Cookie 刷新定时任务线程已启动
```

如果没有，检查：
1. `schedule` 库是否已安装：`pip install schedule`
2. 是否有导入错误
3. 查看应用启动日志中的错误信息

### Cookie 刷新失败

1. 检查对应平台的日志文件
2. 检查 Cookie 文件是否存在
3. 检查网络连接是否正常
4. 检查平台页面是否可以正常访问

## 技术实现

- **模块位置**：`myUtils/cookie_refresh.py`
- **启动位置**：`sau_backend.py` 应用初始化时
- **依赖库**：`schedule`（已在 requirements.txt 中）

## 更新历史

- **2025-12-16**：初始实现，每 2 小时自动刷新一次

