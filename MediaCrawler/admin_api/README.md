# MediaCrawler 管理后台

这是 MediaCrawler 项目的 Web 管理后台，提供可视化的配置管理、任务管理和数据查看功能。

## 功能特性

- 📊 **总览面板**: 查看各平台数据统计和任务状态
- ⚙️ **配置管理**: 为每个平台单独配置爬虫参数
- 🔐 **二维码登录**: 支持各平台的二维码登录，自动保存 Cookie
- 🚀 **任务管理**: 启动、停止和监控爬虫任务
- 📋 **数据列表**: 查看和管理爬取的数据

## 安装和运行

### 后端服务

```bash
# 进入后端目录
cd admin_api

# 安装依赖
pip install -r requirements.txt

# 运行服务
python main.py
```

后端服务将在 `http://localhost:8000` 启动

### 前端服务

```bash
# 进入前端目录
cd admin_api/frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 `http://localhost:3000` 启动

## 使用说明

### 1. 配置平台

1. 进入"配置管理"页面
2. 选择要配置的平台（小红书、抖音等）
3. 设置爬取参数：
   - 爬取类型（搜索/详情/创作者）
   - 关键词
   - 爬取数量
   - 是否爬取评论等
4. 点击"保存配置"

### 2. 登录平台

1. 在配置页面点击"登录"按钮
2. 扫描弹出的二维码
3. 登录成功后，Cookie 会自动保存
4. 下次爬取时无需重新登录

### 3. 启动任务

1. 进入"任务管理"页面
2. 点击"启动新任务"
3. 选择平台和爬取类型
4. 设置参数后启动
5. 在任务列表中查看任务状态

### 4. 查看数据

1. 进入"数据列表"页面
2. 选择平台查看爬取的数据
3. 支持搜索和分页

## API 接口

### 平台相关
- `GET /api/platforms` - 获取支持的平台列表
- `GET /api/config/{platform}` - 获取平台配置
- `POST /api/config/{platform}` - 保存平台配置

### 登录相关
- `POST /api/login/qrcode?platform={platform}` - 获取登录二维码
- `GET /api/login/status/{qrcode_id}` - 检查登录状态
- `GET /api/login/cookie/{platform}` - 获取保存的 Cookie

### 任务相关
- `POST /api/tasks/start` - 启动爬虫任务
- `GET /api/tasks` - 获取任务列表
- `GET /api/tasks/{task_id}` - 获取任务状态
- `DELETE /api/tasks/{task_id}` - 停止任务

### 数据相关
- `GET /api/data/{platform}` - 获取爬取的数据

### 统计相关
- `GET /api/dashboard/stats` - 获取总览统计数据

## 注意事项

1. 首次使用需要先配置平台参数
2. 某些平台需要先登录才能爬取
3. Cookie 保存在 `cookies/` 目录下
4. 爬取的数据保存在 `output/` 目录下

## 技术栈

- **后端**: FastAPI + Python
- **前端**: React + Ant Design + Vite
- **状态管理**: React Hooks
- **HTTP 客户端**: Axios

