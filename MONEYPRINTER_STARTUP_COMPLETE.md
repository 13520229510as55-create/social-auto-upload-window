# MoneyPrinterTurbo 服务启动完成报告

## ✅ 部署状态

**部署时间**: 2025-12-22  
**服务器**: 150.107.38.113  
**项目位置**: `/home/ubuntu/MoneyPrinterTurbo`

## 🎉 服务已成功启动

### 运行中的容器

1. **moneyprinterturbo-webui** (Web界面)
   - 状态: ✅ 运行中
   - 端口: 8501
   - 访问地址: http://150.107.38.113:8501

2. **moneyprinterturbo-api** (API服务)
   - 状态: ✅ 运行中
   - 端口: 8080
   - 访问地址: http://150.107.38.113:8080

## 📋 服务管理命令

### 查看服务状态
```bash
ssh ubuntu@150.107.38.113
cd ~/MoneyPrinterTurbo
/usr/local/bin/docker-compose ps
```

### 查看服务日志
```bash
# Web界面日志
cd ~/MoneyPrinterTurbo
/usr/local/bin/docker-compose logs -f webui

# API服务日志
/usr/local/bin/docker-compose logs -f api

# 所有服务日志
/usr/local/bin/docker-compose logs -f
```

### 重启服务
```bash
cd ~/MoneyPrinterTurbo
/usr/local/bin/docker-compose restart
```

### 停止服务
```bash
cd ~/MoneyPrinterTurbo
/usr/local/bin/docker-compose down
```

### 启动服务
```bash
cd ~/MoneyPrinterTurbo
/usr/local/bin/docker-compose up -d
```

## ⚙️ 配置说明

### 配置文件位置
- **docker-compose.yml**: `/home/ubuntu/MoneyPrinterTurbo/docker-compose.yml`
- **应用配置**: `/home/ubuntu/MoneyPrinterTurbo/config.toml`

### 重要配置
- Web界面已配置为监听 `0.0.0.0:8501`，可以从外部访问
- API服务监听 `0.0.0.0:8080`
- 容器配置为自动重启 (`restart: always`)

## 🔧 防火墙配置

防火墙规则已配置：
- ✅ 8501端口 (Web界面)
- ✅ 8080端口 (API服务)

如果无法访问，请检查：
1. 云服务商安全组是否开放了8501和8080端口
2. 服务器防火墙状态：`sudo ufw status`

## 🌐 访问地址

- **Web界面**: http://150.107.38.113:8501
- **API接口**: http://150.107.38.113:8080

## 📝 后续操作

### 1. 配置API密钥（如需要）

编辑配置文件：
```bash
ssh ubuntu@150.107.38.113
cd ~/MoneyPrinterTurbo
nano config.toml
```

根据项目文档配置以下API密钥：
- Pexels API密钥（用于获取图片）
- LLM Provider API密钥（用于AI功能）

配置完成后重启服务：
```bash
/usr/local/bin/docker-compose restart
```

### 2. 验证服务访问

在浏览器中访问：
- http://150.107.38.113:8501

如果无法访问，请检查：
1. 安全组是否开放了8501端口
2. 服务是否正在运行：`docker ps | grep moneyprinter`
3. 查看服务日志：`/usr/local/bin/docker-compose logs webui`

## 🐛 故障排查

### 问题1: 无法访问Web界面

**检查步骤**:
1. 确认服务运行状态：
   ```bash
   docker ps | grep moneyprinter
   ```

2. 检查端口监听：
   ```bash
   sudo netstat -tlnp | grep 8501
   ```

3. 查看服务日志：
   ```bash
   cd ~/MoneyPrinterTurbo
   /usr/local/bin/docker-compose logs webui
   ```

4. 检查安全组配置（云服务商控制台）

### 问题2: 容器无法启动

**解决方法**:
```bash
cd ~/MoneyPrinterTurbo
/usr/local/bin/docker-compose down
/usr/local/bin/docker-compose up -d --build
```

### 问题3: 权限错误

如果遇到权限问题，可以使用sudo：
```bash
cd ~/MoneyPrinterTurbo
sudo /usr/local/bin/docker-compose down
sudo /usr/local/bin/docker-compose up -d
```

## 📊 服务监控

### 查看资源使用情况
```bash
docker stats moneyprinterturbo-webui moneyprinterturbo-api
```

### 查看容器详细信息
```bash
docker inspect moneyprinterturbo-webui
docker inspect moneyprinterturbo-api
```

## 🔄 更新项目

如果需要更新到最新版本：
```bash
ssh ubuntu@150.107.38.113
cd ~/MoneyPrinterTurbo
git pull origin main
/usr/local/bin/docker-compose down
/usr/local/bin/docker-compose up -d --build
```

## ✅ 部署完成检查清单

- [x] 项目已克隆到服务器
- [x] Docker和Docker Compose已安装
- [x] 服务容器已启动
- [x] 端口映射已配置
- [x] 防火墙规则已添加
- [ ] 安全组端口已开放（需要在云服务商控制台配置）
- [ ] API密钥已配置（如需要）
- [ ] Web界面可正常访问

---

**部署完成时间**: 2025-12-22 23:06  
**服务状态**: ✅ 运行中  
**下一步**: 配置API密钥并验证Web界面访问

