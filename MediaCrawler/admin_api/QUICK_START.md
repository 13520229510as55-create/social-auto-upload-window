# 快速开始指南

## 1. 安装依赖

### 后端依赖
```bash
cd admin_api
pip install -r requirements.txt
```

### 前端依赖
```bash
cd admin_api/frontend
npm install
```

## 2. 启动服务

### 方式一：分别启动（推荐用于开发）

**终端1 - 启动后端：**
```bash
cd admin_api
python main.py
```

**终端2 - 启动前端：**
```bash
cd admin_api/frontend
npm run dev
```

### 方式二：使用启动脚本
```bash
cd admin_api
./start.sh
```

## 3. 访问管理后台

打开浏览器访问：http://localhost:3000

## 4. 使用流程

### 第一步：配置平台
1. 点击左侧菜单"配置管理"
2. 选择要配置的平台（如：小红书）
3. 设置爬取参数：
   - 爬取类型：选择"关键词搜索"、"指定帖子详情"或"创作者主页"
   - 关键词：输入要搜索的关键词（多个用逗号分隔）
   - 最大爬取数量：设置要爬取的数量
   - 其他参数根据需要调整
4. 点击"保存配置"

### 第二步：登录平台
1. 在配置页面点击"登录"按钮
2. 扫描弹出的二维码
3. 等待登录成功（Cookie会自动保存）

### 第三步：启动任务
1. 点击左侧菜单"任务管理"
2. 点击"启动新任务"按钮
3. 选择平台和爬取类型
4. 设置参数后点击"确定"
5. 在任务列表中查看任务状态

### 第四步：查看数据
1. 点击左侧菜单"数据列表"
2. 选择平台查看爬取的数据
3. 支持搜索和分页浏览

## 5. 测试API

```bash
cd admin_api
python test_api.py
```

## 6. 常见问题

### Q: 后端启动失败？
A: 确保已安装所有依赖，并且Python版本 >= 3.8

### Q: 前端启动失败？
A: 确保已安装Node.js (>= 16.0.0)，并运行 `npm install`

### Q: 二维码登录失败？
A: 确保已安装playwright浏览器驱动：`playwright install`

### Q: Cookie保存位置？
A: Cookie保存在 `admin_api/cookies/` 目录下

### Q: 爬取的数据在哪里？
A: 数据保存在项目根目录的 `output/` 目录下，根据保存格式（JSON/CSV/Excel）分别存储

## 7. 平台支持

- ✅ 小红书 (xhs)
- ✅ 抖音 (dy)
- ✅ 快手 (ks)
- ✅ B站 (bili)
- ✅ 微博 (wb)
- ✅ 百度贴吧 (tieba)
- ✅ 知乎 (zhihu)

