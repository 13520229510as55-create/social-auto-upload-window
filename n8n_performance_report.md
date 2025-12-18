# n8n 性能排查报告

## 排查时间
2025-11-30 04:34

## 发现的问题

### 1. n8n 内存占用过高 ⚠️
- **主进程内存占用**: 25.2% (约 987MB)
- **服务器总内存**: 3.8GB
- **影响**: n8n 占用约 1/4 内存，导致系统内存紧张，可能影响性能

### 2. 僵尸进程过多 ⚠️
- **僵尸进程数量**: 29 个
- **影响**: 可能影响系统性能，占用进程表资源

### 3. 未配置 Swap 空间 ⚠️
- **当前状态**: 无 Swap 空间
- **影响**: 内存不足时可能导致 OOM (Out of Memory) 错误

### 4. n8n 响应时间正常 ✅
- **健康检查响应时间**: 0.002 秒
- **说明**: n8n 本身响应不慢，问题主要在内存占用

## 系统资源概览

- **系统负载**: 0.14, 0.12, 0.07 (正常)
- **CPU使用率**: 0.0% (正常)
- **内存使用**: 2.1Gi/3.8Gi (55.26%)
- **磁盘使用**: 44G/77G (57%)
- **n8n进程数**: 2 个
  - 主进程: PID 2795, 内存 987MB, CPU 0.4%
  - 任务运行器: PID 2866, 内存 93MB, CPU 0.1%

## 优化建议

### 立即执行
1. **重启 n8n 服务** - 释放内存
   ```bash
   sudo systemctl restart n8n
   # 或
   pkill -f n8n && n8n start
   ```

2. **配置 Swap 空间** - 防止 OOM
   ```bash
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   echo "/swapfile none swap sw 0 0" | sudo tee -a /etc/fstab
   ```

3. **限制 n8n 内存使用**
   - 创建或编辑 `~/.n8n/config` 文件
   - 添加: `NODE_OPTIONS=--max-old-space-size=512`
   - 或在 systemd 服务文件中添加:
     ```
     [Service]
     MemoryMax=1G
     Environment="NODE_OPTIONS=--max-old-space-size=512"
     ```

### 长期优化
1. **升级服务器内存** - 从 3.8GB 升级到至少 8GB
2. **清理僵尸进程** - 找到并重启僵尸进程的父进程
3. **优化 n8n 工作流** - 减少不必要的节点和数据处理
4. **监控内存使用** - 设置内存告警

## 执行优化

运行优化脚本:
```bash
./optimize_n8n_performance.sh
```

## 验证优化效果

优化后检查:
```bash
# 检查内存使用
free -h

# 检查 Swap
swapon --show

# 检查 n8n 进程
ps aux | grep n8n

# 测试 n8n 响应
time curl http://localhost:5678/healthz
```

