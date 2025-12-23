# MoneyPrinterTurbo 部署状态报告

## 📋 部署信息

- **服务器IP**: 150.107.38.113
- **用户名**: ubuntu
- **项目目录**: /opt/MoneyPrinterTurbo
- **Git仓库**: https://github.com/harry0703/MoneyPrinterTurbo.git

## ✅ 已完成的步骤

根据部署日志，以下步骤已经完成：

1. ✅ **SSH连接测试** - 连接成功
2. ✅ **系统包更新** - 已完成
3. ✅ **基础依赖安装** - 已安装（git, curl, wget等）
4. ✅ **Docker安装检查** - Docker已安装
5. ✅ **Docker Compose安装** - 已安装标准版本（v5.0.1）
6. ✅ **项目克隆** - 项目已克隆到 `/opt/MoneyPrinterTurbo`
7. ✅ **配置文件** - `config.toml` 已创建（从 `config.example.toml` 复制）

## ⚠️ 待确认的步骤

以下步骤需要手动验证：

1. ⚠️ **Docker服务启动** - 需要确认容器是否正在运行
2. ⚠️ **防火墙配置** - 需要确认8501端口是否已开放
3. ⚠️ **Web界面访问** - 需要确认服务是否可访问

## 🔍 验证服务状态

请通过以下命令检查服务状态：

```bash
# 1. SSH连接到服务器
ssh ubuntu@150.107.38.113
# 密码: 15831929073asAS

# 2. 进入项目目录
cd /opt/MoneyPrinterTurbo

# 3. 检查Docker容器状态
/usr/local/bin/docker-compose ps

# 或者使用docker命令
docker ps | grep moneyprinter

# 4. 查看服务日志
/usr/local/bin/docker-compose logs -f

# 5. 如果服务未启动，手动启动
/usr/local/bin/docker-compose up -d --build
```

## 🌐 访问地址

- **Web界面**: http://150.107.38.113:8501
- **API接口**: http://150.107.38.113:8080

## 📝 配置说明

### 配置文件位置
- `/opt/MoneyPrinterTurbo/config.toml`

### 需要配置的API密钥
根据项目文档，您可能需要配置以下API密钥：
- Pexels API密钥（用于获取图片）
- LLM Provider API密钥（用于AI功能）

### 编辑配置文件
```bash
ssh ubuntu@150.107.38.113
cd /opt/MoneyPrinterTurbo
nano config.toml
# 或使用vim
vim config.toml
```

## 🚀 启动/停止服务

### 启动服务
```bash
cd /opt/MoneyPrinterTurbo
/usr/local/bin/docker-compose up -d
```

### 停止服务
```bash
cd /opt/MoneyPrinterTurbo
/usr/local/bin/docker-compose down
```

### 重启服务
```bash
cd /opt/MoneyPrinterTurbo
/usr/local/bin/docker-compose restart
```

### 查看日志
```bash
cd /opt/MoneyPrinterTurbo
/usr/local/bin/docker-compose logs -f
```

## 🔧 防火墙配置

如果无法访问Web界面，请检查防火墙设置：

```bash
# Ubuntu UFW防火墙
sudo ufw allow 8501/tcp
sudo ufw allow 8080/tcp
sudo ufw reload

# 或者检查防火墙状态
sudo ufw status
```

## 📋 部署脚本

已创建自动部署脚本：`deploy_moneyprinter.sh`

可以随时重新运行部署脚本：
```bash
cd /Users/a58/Desktop/social-auto-upload-window
./deploy_moneyprinter.sh
```

## ⚠️ 注意事项

1. **API密钥配置**: 部署完成后，请务必配置 `config.toml` 中的API密钥，否则某些功能可能无法使用。

2. **端口开放**: 确保服务器安全组已开放以下端口：
   - 8501 (Web界面)
   - 8080 (API接口)

3. **资源要求**: MoneyPrinterTurbo 可能需要较多系统资源，请确保服务器有足够的内存和CPU。

4. **Docker Compose版本**: 已安装标准版本的docker-compose到 `/usr/local/bin/docker-compose`，如果遇到路径问题，请使用完整路径。

## 🐛 故障排查

### 问题1: 服务无法启动
```bash
# 查看详细日志
cd /opt/MoneyPrinterTurbo
/usr/local/bin/docker-compose logs

# 检查Docker是否运行
sudo systemctl status docker

# 重启Docker服务
sudo systemctl restart docker
```

### 问题2: 端口被占用
```bash
# 检查端口占用
sudo netstat -tlnp | grep 8501
sudo netstat -tlnp | grep 8080

# 如果被占用，可以修改docker-compose.yml中的端口映射
```

### 问题3: 容器启动失败
```bash
# 查看容器日志
docker logs moneyprinterturbo-webui
docker logs moneyprinterturbo-api

# 重新构建镜像
cd /opt/MoneyPrinterTurbo
/usr/local/bin/docker-compose build --no-cache
/usr/local/bin/docker-compose up -d
```

---

**最后更新**: 2025-12-22
**部署脚本**: `deploy_moneyprinter.sh`

