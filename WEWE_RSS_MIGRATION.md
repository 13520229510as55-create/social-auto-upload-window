# wewe-rss 服务迁移说明

## 📋 问题背景

**wewe-rss** 服务最初使用 **Docker** 管理，但在运行过程中遇到了严重问题：

### 问题描述
- **症状**: 服务崩溃重启循环，CPU 占用 60%+
- **重启次数**: 653 次
- **根本原因**: 
  1. 缺少 `DATABASE_URL` 环境变量
  2. Prisma 无法连接数据库
  3. 服务启动失败 → PM2/Docker 自动重启 → 再次失败 → 循环

### Docker 容器信息
- **容器名称**: wewe-rss
- **镜像**: cooderl/wewe-rss:latest
- **创建时间**: 2025-12-10
- **最后启动**: 2025-12-16 07:18:20
- **状态**: Exited (1) - 已停止
- **重启策略**: unless-stopped

---

## 🔧 解决方案

### 迁移到 PM2 管理

**时间**: 2025-12-16

**步骤**:
1. ✅ 创建 `.env` 文件，配置 `DATABASE_URL`
2. ✅ 修改 `schema.prisma` 使用 SQLite（更简单，无需 MySQL 配置）
3. ✅ 修复 schema 语法错误
4. ✅ 重新生成 Prisma Client
5. ✅ 创建 SQLite 数据库迁移
6. ✅ 使用 PM2 直接运行源代码

### PM2 配置

**启动命令**:
```bash
cd /home/ubuntu/wewe-rss && /home/ubuntu/.local/share/pnpm/pnpm --filter server start:prod
```

**工作目录**: `/home/ubuntu/wewe-rss`

**端口**: 4000

**状态**: ✅ 正常运行中

---

## 📊 迁移前后对比

| 项目 | Docker 管理 | PM2 管理 |
|------|------------|---------|
| **部署方式** | 容器化 | 直接运行源代码 |
| **环境变量** | 容器环境 | `.env` 文件 |
| **数据库** | MySQL（需要配置） | SQLite（更简单） |
| **状态** | ❌ 崩溃重启循环 | ✅ 正常运行 |
| **CPU 占用** | 60%+ | 正常 |
| **重启次数** | 653 次 | 0 次 |
| **管理方式** | `docker` 命令 | `pm2` 命令 |

---

## 🗑️ 清理建议

### 删除 Docker 容器

由于 wewe-rss 已迁移到 PM2 管理，Docker 容器可以删除：

```bash
# 删除已停止的容器
docker rm wewe-rss

# 或者如果容器还在运行，先停止再删除
docker stop wewe-rss
docker rm wewe-rss
```

### 保留 Docker 镜像（可选）

如果需要保留 Docker 镜像以备将来使用：
```bash
# 不删除镜像，只删除容器
docker rm wewe-rss
```

---

## ✅ 当前状态

- ✅ **PM2 服务**: 正常运行中（端口 4000）
- ✅ **数据库**: SQLite（`/home/ubuntu/wewe-rss/data/wewe-rss.db`）
- ✅ **开机启动**: 已配置（通过 PM2 systemd 服务）
- ❌ **Docker 容器**: 已停止（可以删除）

---

## 📝 总结

**wewe-rss 并不是同时用 Docker 和 PM2 管理**，而是：

1. **最初**（2025-12-10）: 使用 Docker 管理
2. **出现问题**（2025-12-16）: Docker 容器崩溃重启循环
3. **迁移**（2025-12-16）: 改用 PM2 直接运行源代码
4. **现在**: PM2 服务正常运行，Docker 容器已停止但未删除

**建议**: 删除已停止的 Docker 容器，避免混淆。

---

**文档生成时间**: 2025-12-16

