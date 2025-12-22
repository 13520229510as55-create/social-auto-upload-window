# MediaCrawler 内置模块

这是 MediaCrawler 的内置版本，已整合到 social-auto-upload-window 项目中。

## 目录结构

- `admin_api/` - 管理后台 API 服务
- `database/` - 数据库模型和会话管理
- `media_platform/` - 各平台爬虫实现
- `config/` - 配置文件
- `cmd_arg/` - 命令行参数处理
- `libs/` - 第三方库和工具

## 使用说明

所有 MediaCrawler 的功能已通过 `crawler_api.py` 蓝图暴露，使用 `/api/crawler` 前缀访问。

## 注意事项

- 确保所有依赖已安装：`pip install -r requirements.txt`
- 数据库配置在 `database/` 目录中
- 配置文件在 `config/` 目录中

