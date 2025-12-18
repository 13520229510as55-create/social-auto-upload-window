# WeWe RSS 部署说明

## 项目简介

WeWe RSS 是一个更优雅的微信公众号订阅方式，支持私有化部署、微信公众号RSS生成（基于微信读书）。

项目地址: https://github.com/cooderl/wewe-rss

## 部署信息

- **服务器IP**: 150.107.38.113
- **服务器用户**: ubuntu
- **部署方式**: Docker + MySQL
- **访问端口**: 4000

## 快速部署

### 前置要求

1. 本地需要安装 `sshpass`:
   ```bash
   # macOS
   brew install hudochenkov/sshpass/sshpass
   
   # Ubuntu/Debian
   sudo apt-get install sshpass
   ```

2. 确保服务器已安装 Docker（脚本会自动安装）

### 部署步骤

1. **修改配置**（可选）:
   
   编辑 `deploy_wewe_rss.sh` 文件，修改以下配置：
   ```bash
   MYSQL_ROOT_PASSWORD="wewe_rss_123456"  # MySQL root 密码
   AUTH_CODE="wewe_rss_auth_123456"       # API 授权码
   ```

2. **执行部署**:
   ```bash
   ./deploy_wewe_rss.sh
   ```

3. **访问服务**:
   
   部署完成后，访问: http://150.107.38.113:4000

## 使用说明

### 首次使用

1. **登录微信读书账号**:
   - 进入"账号管理"
   - 点击"添加账号"
   - 微信扫码登录微信读书账号
   - **注意**: 不要勾选"24小时后自动退出"

2. **订阅微信公众号**:
   - 进入"公众号源"
   - 点击"添加"
   - 提交微信公众号分享链接
   - **注意**: 添加频率过高容易被封控，建议间隔24小时

### RSS 订阅

部署完成后，可以通过以下方式获取 RSS:

- 所有订阅源: `http://150.107.38.113:4000/feeds/all.rss`
- 单个订阅源: `http://150.107.38.113:4000/feeds/{feed_id}.rss`
- JSON 格式: `http://150.107.38.113:4000/feeds/all.json`
- Atom 格式: `http://150.107.38.113:4000/feeds/all.atom`

### 高级功能

#### 标题过滤

```
# 包含特定标题
http://150.107.38.113:4000/feeds/all.atom?title_include=张三

# 排除特定标题
http://150.107.38.113:4000/feeds/MP_WXS_123.json?limit=30&title_include=张三|李四|王五&title_exclude=张三丰|赵六
```

#### 手动更新

```
http://150.107.38.113:4000/feeds/MP_WXS_123.rss?update=true
```

## 容器管理

### 查看日志

```bash
# WeWe RSS 日志
docker logs -f wewe-rss

# MySQL 日志
docker logs -f wewe-rss-db
```

### 停止服务

```bash
docker stop wewe-rss wewe-rss-db
```

### 启动服务

```bash
docker start wewe-rss-db wewe-rss
```

### 重启服务

```bash
docker restart wewe-rss wewe-rss-db
```

### 删除服务（数据会保留在 volume 中）

```bash
docker stop wewe-rss wewe-rss-db
docker rm wewe-rss wewe-rss-db
```

### 完全删除（包括数据）

```bash
docker stop wewe-rss wewe-rss-db
docker rm wewe-rss wewe-rss-db
docker volume rm wewe_rss_db_data
```

## 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| DATABASE_URL | 数据库连接地址 | 自动生成 |
| AUTH_CODE | API 授权码 | wewe_rss_auth_123456 |
| SERVER_ORIGIN_URL | 服务端访问地址 | http://150.107.38.113:4000 |
| MAX_REQUEST_PER_MINUTE | 每分钟最大请求次数 | 60 |
| FEED_MODE | 输出模式（fulltext 全文） | - |
| CRON_EXPRESSION | 定时更新 Cron 表达式 | 35 5,17 * * * |
| UPDATE_DELAY_TIME | 连续更新延迟时间 | 60s |
| ENABLE_CLEAN_HTML | 是否开启正文 HTML 清理 | false |
| PLATFORM_URL | 基础服务 URL | https://weread.111965.xyz |

## 账号状态说明

| 状态 | 说明 |
|------|------|
| 今日小黑屋 | 账号被封控，等一天恢复。账号正常时可通过重启服务/容器清除小黑屋记录 |
| 禁用 | 不使用该账号 |
| 失效 | 账号登录状态失效，需要重新登录 |

## 故障排查

### 1. 无法访问服务

- 检查防火墙是否开放 4000 端口
- 检查容器是否运行: `docker ps`
- 查看容器日志: `docker logs wewe-rss`

### 2. MySQL 连接失败

- 检查 MySQL 容器是否运行: `docker ps | grep wewe-rss-db`
- 检查 MySQL 日志: `docker logs wewe-rss-db`
- 等待 MySQL 完全启动（可能需要30-60秒）

### 3. 账号被封控

- 等待24小时后自动恢复
- 或重启容器清除小黑屋记录: `docker restart wewe-rss`

### 4. RSS 无法更新

- 检查账号状态是否为"失效"
- 检查定时任务是否正常运行
- 手动触发更新: `http://150.107.38.113:4000/feeds/{feed_id}.rss?update=true`

## 数据备份

### 备份 MySQL 数据

```bash
docker exec wewe-rss-db mysqldump -u root -p$MYSQL_ROOT_PASSWORD wewe-rss > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 恢复 MySQL 数据

```bash
docker exec -i wewe-rss-db mysql -u root -p$MYSQL_ROOT_PASSWORD wewe-rss < backup.sql
```

## 安全建议

1. **修改默认密码**: 修改脚本中的 `MYSQL_ROOT_PASSWORD` 和 `AUTH_CODE`
2. **配置防火墙**: 只允许必要的 IP 访问 4000 端口
3. **定期备份**: 定期备份 MySQL 数据
4. **监控日志**: 定期查看容器日志，及时发现异常

## 参考链接

- 项目 GitHub: https://github.com/cooderl/wewe-rss
- Docker Hub: https://hub.docker.com/r/cooderl/wewe-rss

