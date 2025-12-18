# 版本历史

## 版本 1.1.0 (2025-11-30)

### 🎉 主要更新

#### 1. UI样式优化
- **制作中心和发布中心**: 标题、摘要、正文三列最多显示3行，超出省略
- **Tooltip优化**: 统一tooltip最大宽度为200px，支持多行显示
- **图片/媒资链接列**: 优化显示样式，支持多行显示，清爽高级
- **发布中心列宽**: 统一所有Tab的列宽，保持一致

#### 2. 时区问题修复
- **统一时区**: 所有时间显示统一使用中国时区(UTC+8)
- **数据库时间**: 修复创建时间存储问题，确保时区正确
- **前端显示**: 优化时间显示格式

#### 3. 账号管理优化
- **筛选选项**: 优化平台筛选选项加载逻辑
- **内容类型标签**: 修复"图文内容生成器"显示为"图文"
- **默认值**: 确保筛选选项始终有默认值

#### 4. 素材管理优化
- **Tab分类**: 恢复三个Tab（本地上传素材、谷歌上传素材、生成素材）
- **搜索栏**: 优化搜索栏位置和样式

#### 5. n8n性能优化
- **内存限制**: 添加内存限制配置（1.5GB）
- **性能排查**: 添加性能排查和优化脚本
- **配置备份**: 添加配置备份脚本

#### 6. 部署和工具脚本
- 添加多个部署脚本
- 添加服务器检查脚本
- 添加数据库备份脚本

### 🐛 Bug 修复
- 修复时区显示不正确的问题
- 修复内容类型标签显示问题
- 修复制作中心列表显示问题
- 修复发布中心列宽不一致问题

### 🔧 技术改进
- 优化CSS样式，使用line-clamp实现多行省略
- 统一tooltip样式，使用全局样式
- 优化时间处理逻辑

## 版本 11-27 (2025-11-27)

### 🎉 主要更新

#### 1. API 地址 localhost 问题彻底修复
- **问题**: 前端 API 请求多次出现调用 `http://localhost:5409` 的问题
- **根本原因**: 多处直接使用环境变量 `VITE_API_BASE_URL`，未统一过滤 localhost
- **修复范围**:
  - `sau_frontend/src/utils/request.js` - 核心请求工具，添加 localhost 检测和过滤
  - `sau_frontend/src/views/AccountManagement.vue` - 修复 3 处直接使用环境变量的地方（下载Cookie、上传Cookie、SSE登录连接）
  - `sau_frontend/src/views/ProductionCenter.vue` - 修复 API URL 构建逻辑
  - `sau_frontend/src/views/PublishCenter.vue` - 修复 API URL 构建逻辑
  - `sau_frontend/src/api/material.js` - 修复素材 API URL 构建
  - `sau_frontend/src/views/request.js` - 修复旧文件中的问题
  - `sau_frontend/src/views/material.js` - 修复旧文件中的问题
- **三层保护机制**:
  1. **构建时检查**: 环境变量包含 localhost 时强制使用相对路径
  2. **运行时检查**: 请求拦截器中再次检查并修正
  3. **兜底保护**: 所有直接使用环境变量的地方都有 localhost 检查
- **结果**: 所有 API 请求现在都使用相对路径（`/api/xxx`），自动适配当前域名，不再出现 localhost 地址

#### 2. 视频号发布功能优化
- **Google Storage 文件支持**: 支持从 Google Storage URI 下载视频文件后上传
- **文件上传超时优化**: 增加文件上传超时时间到 60 秒
- **文件输入框等待优化**: 优化文件输入框的等待逻辑，移除对 `visible` 状态的依赖（文件输入框通常是隐藏的）

#### 3. 素材管理功能增强
- **Google Storage 集成**: 支持上传素材到 Google Storage
- **素材来源标识**: 数据库记录素材来源（本地上传/谷歌存储上传）
- **URI 存储**: 存储 Google Storage 文件的 URI，支持后续下载和发布

### 🐛 Bug 修复
- 修复前端 API 请求多次调用 localhost:5409 的问题
- 修复 Google Storage 视频文件发布时未先下载到本地的问题
- 修复视频号文件上传超时问题
- 修复文件输入框等待逻辑错误（文件输入框通常是隐藏的，不应等待 visible 状态）

### 🔧 技术改进
- 统一 API URL 构建逻辑，所有位置都经过 localhost 过滤
- 增强错误处理和重试机制
- 优化文件上传流程

### 🚀 部署信息
- 服务器: 101.126.158.155
- 部署目录: `/opt/social-auto-upload`
- 后端端口: 5409
- 部署时间: 2025-11-27 17:08

---

## 版本 11-19 (2025-11-19)

### 🎉 主要更新

#### 1. 视频号登录与发布功能修复
- **问题**: 添加视频号账号时，扫码登录成功但账号信息未保存到数据库
- **原因**: Cookie 验证逻辑过于严格，将跳转到 `/platform` 主页的情况误判为 Cookie 失效
- **修复**: 
  - 修改 `myUtils/auth.py` 中的 `cookie_auth_tencent` 函数
  - 将跳转到 `/platform` 主页的情况视为有效登录
  - 只有跳转到 `/login` 页面才视为 Cookie 失效
- **结果**: 账号添加成功，视频上传和发布功能正常

#### 2. Xvfb 虚拟显示支持
- **新增**: `utils/xvfb_helper.py` 模块
- **功能**: 在无头服务器上支持非 headless 浏览器模式
- **特性**:
  - 自动查找可用的显示编号（从 99 开始）
  - 自动清理旧的锁文件
  - 支持在主线程和子线程中启动
  - 进程退出时自动清理
- **集成**:
  - `myUtils/auth.py`: Cookie 验证（强制使用 headless 模式以提高速度）
  - `myUtils/login.py`: 账号登录（支持非 headless 模式，DISPLAY 环境变量正确传递）
  - `uploader/tencent_uploader/main.py`: 视频上传（支持非 headless 模式）

#### 3. 登录 API 性能优化
- **页面加载优化**: 使用 `domcontentloaded` 替代 `load` 事件，加快页面加载速度
- **元素等待优化**: 增加超时时间和重试逻辑，提高稳定性
- **DISPLAY 环境变量**: 修复子线程中 DISPLAY 未正确传递的问题
- **Signal 处理**: 修复 `signal only works in main thread` 错误

#### 4. 部署与服务管理
- **新增**: `deploy_conda.sh` - 使用 Conda 的自动化部署脚本
- **新增**: `ecosystem.config.js` - PM2 进程管理配置
- **新增**: 多个部署和服务管理相关文档
- **功能**: 支持一键部署、自动启动、进程监控

#### 5. 文档完善
- **新增文档**:
  - `启动指南.md`: 详细的本地和服务器启动指南
  - `PM2服务管理.md`: PM2 使用和管理文档
  - `Xvfb配置说明.md`: Xvfb 安装和配置指南
  - `登录API性能优化说明.md`: 登录 API 优化记录
  - `登录API问题修复说明.md`: 登录 API 问题修复记录
  - `视频号发布修复说明.md`: 视频号发布问题修复记录
  - `部署说明.md`: 服务器部署详细文档

### 🐛 Bug 修复
- 修复 Python 3.9 兼容性问题（`match/case` 语句替换为 `if/elif`）
- 修复视频文件上传目录不存在的问题
- 修复 Vite 前端服务外网无法访问的问题
- 修复视频号 Cookie 验证逻辑错误
- 修复非 headless 模式下 DISPLAY 环境变量传递问题
- 修复 Xvfb 在子线程中启动时的 signal 注册问题

### 🔧 技术改进
- 前端服务绑定到 `0.0.0.0`，支持外网访问
- Cookie 验证统一使用 headless 模式，提高速度和稳定性
- 优化页面加载和元素等待策略
- 增强错误处理和日志记录

### 📝 配置变更
- `sau_frontend/vite.config.js`: 添加 `host: '0.0.0.0'`
- `conf.py`: 支持 `LOCAL_CHROME_PATH` 和 `LOCAL_CHROME_HEADLESS` 配置

### 🚀 部署信息
- 服务器: 150.107.38.113
- 部署目录: `/home/ubuntu/social-auto-upload`
- Python 环境: Conda (`social-auto-upload`)
- 进程管理: PM2
- 后端端口: 5409
- 前端端口: 5173

---

## 历史版本

*(后续版本更新请在此处追加)*

