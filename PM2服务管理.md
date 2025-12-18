# PM2 服务管理指南

## 服务状态

✅ **后端服务**: sau-backend (PM2 管理)  
✅ **前端服务**: sau-frontend (PM2 管理)  
✅ **开机自启动**: 已配置

## PM2 常用命令

### 查看服务状态

```bash
# 设置 PATH（每次新终端需要执行）
export PATH=~/.npm-global/bin:$PATH

# 查看所有服务
pm2 list

# 查看详细信息
pm2 info sau-backend
pm2 info sau-frontend
```

### 查看日志

```bash
# 查看所有服务日志
pm2 logs

# 查看特定服务日志
pm2 logs sau-backend
pm2 logs sau-frontend

# 查看最近 100 行日志
pm2 logs --lines 100

# 实时查看日志
pm2 logs --lines 50
```

### 服务控制

```bash
# 重启服务
pm2 restart sau-backend      # 重启后端
pm2 restart sau-frontend    # 重启前端
pm2 restart all              # 重启所有服务

# 停止服务
pm2 stop sau-backend
pm2 stop sau-frontend
pm2 stop all

# 启动服务
pm2 start sau-backend
pm2 start sau-frontend
pm2 start all

# 删除服务（从 PM2 中移除）
pm2 delete sau-backend
pm2 delete sau-frontend
pm2 delete all
```

### 监控和管理

```bash
# 实时监控
pm2 monit

# 查看服务详细信息
pm2 show sau-backend
pm2 show sau-frontend

# 重新加载配置（零停机重启）
pm2 reload all

# 保存当前进程列表
pm2 save

# 清除所有日志
pm2 flush
```

## 开机自启动

开机自启动已通过 systemd 配置，服务会在服务器重启后自动启动。

### 验证开机自启动

```bash
# 检查 systemd 服务状态
sudo systemctl status pm2-ubuntu

# 检查是否启用
sudo systemctl is-enabled pm2-ubuntu
```

### 管理开机自启动

```bash
# 启用开机自启动（已配置）
sudo systemctl enable pm2-ubuntu

# 禁用开机自启动
sudo systemctl disable pm2-ubuntu

# 手动启动 PM2
sudo systemctl start pm2-ubuntu

# 停止 PM2
sudo systemctl stop pm2-ubuntu
```

## 服务配置

配置文件位置: `~/social-auto-upload/ecosystem.config.cjs`

### 修改配置后重启

```bash
cd ~/social-auto-upload
# 修改 ecosystem.config.cjs 后
pm2 delete all
pm2 start ecosystem.config.cjs
pm2 save
```

## 故障排查

### 服务无法启动

1. **查看错误日志**:
```bash
pm2 logs sau-backend --err --lines 50
pm2 logs sau-frontend --err --lines 50
```

2. **检查服务状态**:
```bash
pm2 list
pm2 show sau-backend
```

3. **手动测试启动**:
```bash
# 后端
cd ~/social-auto-upload
source ~/miniconda3/etc/profile.d/conda.sh
conda activate social-auto-upload
python sau_backend.py

# 前端
cd ~/social-auto-upload/sau_frontend
npm run dev
```

### 服务频繁重启

```bash
# 查看重启次数
pm2 list

# 查看重启原因
pm2 logs sau-backend --lines 100
```

### 端口被占用

```bash
# 检查端口占用
netstat -tuln | grep -E "5173|5409"
ss -tuln | grep -E "5173|5409"

# 杀死占用进程
sudo lsof -ti:5409 | xargs kill -9
sudo lsof -ti:5173 | xargs kill -9
```

## 性能监控

```bash
# 实时监控 CPU 和内存
pm2 monit

# 查看资源使用情况
pm2 list
```

## 日志管理

日志文件位置:
- 后端: `~/social-auto-upload/logs/backend-out.log` 和 `backend-error.log`
- 前端: `~/social-auto-upload/logs/frontend-out.log` 和 `frontend-error.log`

### 日志轮转

PM2 会自动管理日志，也可以配置日志轮转：

```bash
# 安装日志轮转模块
pm2 install pm2-logrotate

# 配置日志轮转
pm2 set pm2-logrotate:max_size 10M
pm2 set pm2-logrotate:retain 7
```

## 快速参考

```bash
# 完整服务管理脚本
#!/bin/bash
export PATH=~/.npm-global/bin:$PATH
cd ~/social-auto-upload

case "$1" in
    start)
        pm2 start ecosystem.config.cjs
        pm2 save
        ;;
    stop)
        pm2 stop all
        ;;
    restart)
        pm2 restart all
        ;;
    status)
        pm2 list
        ;;
    logs)
        pm2 logs --lines 50
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status|logs}"
        exit 1
        ;;
esac
```

## 访问地址

- **前端界面**: http://150.107.38.113:5173
- **后端 API**: http://150.107.38.113:5409

## 注意事项

1. **每次新开终端**，需要先设置 PATH:
   ```bash
   export PATH=~/.npm-global/bin:$PATH
   ```

2. **修改配置后**，记得执行 `pm2 save` 保存配置

3. **服务器重启后**，PM2 会自动恢复服务（通过 systemd）

4. **查看日志**时，使用 `pm2 logs` 比直接查看日志文件更方便

