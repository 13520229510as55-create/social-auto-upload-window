# 服务器服务总结报告

**生成时间**: 2025-12-16  
**服务器**: 150.107.38.113

---

## 📊 服务概览

### 一、PM2 管理的服务（5个）

| 服务名称 | 状态 | PID | 运行时间 | 重启次数 | 内存占用 | 开机启动 |
|---------|------|-----|---------|---------|---------|---------|
| **sau-frontend** | online | 1662 | 3h | 0 | 26.6MB | ✅ 是 |
| **sau-backend** | online | 524850 | 22m | 13 | 55.6MB | ✅ 是 |
| **garment-calculator** | online | 1732 | 3h | 0 | 3.1MB | ✅ 是 |
| **rsshub** | online | 1758 | 3h | 0 | 15.8MB | ✅ 是 |
| **wewe-rss** | online | 524030 | 42m | 653 | 3.4MB | ✅ 是 |

**PM2 开机启动配置**:
- ✅ 已配置 systemd 服务: `/etc/systemd/system/pm2-ubuntu.service`
- ✅ 所有 PM2 服务均配置为 `autorestart: true`
- ✅ 服务器重启后会自动启动所有 PM2 服务

---

### 二、Docker 管理的容器（5个）

| 容器名称 | 镜像 | 状态 | 端口映射 | 重启策略 | 开机启动 |
|---------|------|------|---------|---------|---------|
| **n8n_926** | n8nio/n8n:latest | Up 4 hours | 0.0.0.0:5678->5678 | `always` | ✅ 是 |
| **html-to-image-service** | html-to-image-service-html-to-image | Up 4 hours | 0.0.0.0:3000->3000 | `always` | ✅ 是 |
| **wewe-rss-db** | mysql:8.3.0 | Up 4 hours | 3306/tcp, 33060/tcp | `always` | ✅ 是 |
| **wewe-rss** | cooderl/wewe-rss:latest | Exited (1) | - | `unless-stopped` | ❌ 已迁移到 PM2* |
| **17d4524f5ede_xiaohongshu-mcp-node** | xiaohongshu-mcp-node:latest | Exited (255) 7周前 | 0.0.0.0:18060->18060 | `unless-stopped` | ⚠️ 已停止* |

**Docker 服务状态**:
- ✅ Docker 服务已启用开机启动 (`docker.service: enabled`)
- ✅ 运行中的容器均配置了自动重启策略
- ⚠️ 部分容器已停止（wewe-rss, xiaohongshu-mcp-node）- 由于 `unless-stopped` 策略，手动停止后不会自动启动
- 📝 存在多个 docker-compose.yml 配置文件

**重启策略说明**:
- `always`: 容器总是重启（即使手动停止也会在 Docker 启动时重启）✅ **推荐用于重要服务**
- `unless-stopped`: 容器自动重启，除非手动停止（手动停止后不会自动启动）

**重要容器重启策略**（2025-12-16 更新）:
- ✅ **n8n_926**: `always` - 已配置开机自启动
- ✅ **html-to-image-service**: `always` - 已配置开机自启动
- ✅ **wewe-rss-db**: `always` - 已配置开机自启动

**Docker Compose 项目位置**:
- `/home/ubuntu/RSSHub/docker-compose.yml`
- `/home/ubuntu/docker-compose.yml`
- `/home/ubuntu/xiaohongshu-mcp/docker/docker-compose.yml`
- `/home/ubuntu/xiaohongshu-mcp/docker-compose.yml`
- `/home/ubuntu/xhs-mcp-v2/docker-compose.yml`

*注：Docker 容器是否开机启动取决于容器的重启策略（RestartPolicy）配置

---

### 三、Systemd 管理的系统服务

#### 3.1 已启用开机启动的服务

| 服务名称 | 状态 | 说明 |
|---------|------|------|
| **docker.service** | active (running) | Docker 容器引擎 |
| **nginx.service** | active (running) | Web 服务器和反向代理 |
| **mysql.service** | active (running) | MySQL 数据库服务器 |
| **pm2-ubuntu.service** | enabled | PM2 进程管理器（用户级别） |
| **containerd.service** | enabled | 容器运行时 |
| **cron.service** | enabled | 定时任务服务 |

#### 3.2 其他系统服务
- `apparmor.service` - 应用安全框架
- `cloud-init.service` - 云初始化服务
- `cron.service` - 定时任务
- 其他系统基础服务...

---

### 四、端口监听情况

| 端口 | 服务/进程 | 说明 |
|------|---------|------|
| **22** | sshd | SSH 服务 |
| **80** | nginx | HTTP 服务 |
| **443** | nginx | HTTPS 服务 |
| **3000** | docker-proxy (html-to-image-service) | HTML转图片服务 |
| **4000** | node (wewe-rss) | WeWe RSS 服务 |
| **5001** | python3 | 未知服务 |
| **5409** | python3 (sau-backend) | 社交自动上传后端 |
| **5410** | python3 | 未知服务 |
| **5678** | docker-proxy (n8n_926) | n8n 工作流服务 |
| **18060** | xiaohongshu-mcp-node (已停止) | 小红书 MCP 服务 |
| **19673** | python3 | 未知服务 |
| **3306** | mysql (容器内) | MySQL 数据库 |

---

## 🔄 开机启动总结

### ✅ 已配置开机启动的服务

1. **PM2 服务** (5个)
   - sau-frontend
   - sau-backend
   - garment-calculator
   - rsshub
   - wewe-rss
   - 通过 systemd 服务 `pm2-ubuntu.service` 管理

2. **Docker 服务**
   - Docker 引擎本身已启用开机启动
   - 容器是否自动启动取决于容器的重启策略

3. **系统服务**
   - nginx (Web 服务器)
   - mysql (数据库)
   - docker (容器引擎)
   - containerd (容器运行时)

### ⚠️ 需要注意的服务

1. **wewe-rss (Docker 容器)**
   - 状态: Exited (1) - 已停止
   - **说明**: 已从 Docker 迁移到 PM2 管理（2025-12-16）
   - **原因**: Docker 容器因缺少 DATABASE_URL 环境变量导致崩溃重启循环
   - **解决方案**: 改用 PM2 直接运行源代码，已修复并正常运行
   - **建议**: 可以删除此 Docker 容器，因为现在由 PM2 管理

2. **xiaohongshu-mcp-node (Docker 容器)**
   - 状态: Exited (255) - 已停止 7 周
   - 可能需要清理或重新配置

---

## 📝 建议

### 1. Docker 容器重启策略检查
建议检查所有 Docker 容器的重启策略，确保重要服务配置为 `always` 或 `unless-stopped`：

```bash
# 检查容器重启策略
docker inspect --format='{{.Name}}: {{.HostConfig.RestartPolicy.Name}}' $(docker ps -aq)

# 设置容器开机启动（示例）
docker update --restart=always <container_name>
```

### 2. 停止的容器处理
- **wewe-rss**: 
  - ✅ 已从 Docker 迁移到 PM2（2025-12-16）
  - ✅ PM2 服务正常运行中
  - 🗑️ **建议删除 Docker 容器**：`docker rm wewe-rss`（因为已不再使用）
- **xiaohongshu-mcp-node**: 如果不再使用，建议删除容器

### 3. 端口服务确认
建议确认以下端口的服务用途：
- 5001 (python3)
- 5410 (python3)
- 19673 (python3)

---

## 📊 服务统计

- **PM2 服务**: 5 个（全部运行中）
- **Docker 容器**: 5 个（3 个运行中，2 个已停止）
- **Systemd 服务**: 多个（核心服务已启用开机启动）
- **总服务数**: 约 15+ 个（包括系统服务）

---

## 🔧 管理命令参考

### PM2 管理
```bash
# 查看所有服务
pm2 list

# 重启服务
pm2 restart <service_name>

# 保存当前进程列表（用于开机启动）
pm2 save

# 查看服务日志
pm2 logs <service_name>
```

### Docker 管理
```bash
# 查看所有容器
docker ps -a

# 启动容器
docker start <container_name>

# 停止容器
docker stop <container_name>

# 设置容器开机启动
docker update --restart=always <container_name>
```

### Systemd 管理
```bash
# 查看服务状态
systemctl status <service_name>

# 启用开机启动
sudo systemctl enable <service_name>

# 禁用开机启动
sudo systemctl disable <service_name>
```

---

**报告生成完成**

