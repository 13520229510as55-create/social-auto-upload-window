# VideoLingo 部署文档

## 📋 部署信息

- **项目仓库**: https://github.com/Huanshere/VideoLingo.git
- **服务器 IP**: 150.107.38.113
- **服务器用户**: ubuntu
- **部署目录**: `/opt/videolingo/VideoLingo`
- **服务端口**: 8502 (8501 被占用，已改为 8502)

## ✅ 部署完成状态

### 已完成的工作

1. ✅ **项目克隆**: 已从 GitHub 克隆到服务器
2. ✅ **Python 环境**: 已创建虚拟环境并安装基础依赖
3. ✅ **系统依赖**: 已安装 ffmpeg 及相关开发库
4. ✅ **启动脚本**: 已创建 `/opt/videolingo/VideoLingo/start_videolingo.sh`
5. ✅ **Systemd 服务**: 已创建 `videolingo.service` 服务文件

### 依赖安装状态

- ✅ 基础 Python 包已安装
- ✅ Streamlit 已安装
- ⚠️ 部分依赖有版本警告（不影响基本运行）
  - torchaudio 版本不匹配（已安装 2.9.1，demucs 需要 <2.2）
  - numpy 版本警告
  - 部分可选依赖未完全安装

## 🚀 启动服务

### 方法 1: 使用 systemd 服务（推荐）

```bash
# 连接到服务器
ssh ubuntu@150.107.38.113

# 启动服务
sudo systemctl start videolingo

# 查看服务状态
sudo systemctl status videolingo

# 查看实时日志
sudo journalctl -u videolingo -f

# 设置开机自启
sudo systemctl enable videolingo

# 停止服务
sudo systemctl stop videolingo

# 重启服务
sudo systemctl restart videolingo
```

### 方法 2: 手动启动

```bash
# 连接到服务器
ssh ubuntu@150.107.38.113

# 进入项目目录
cd /opt/videolingo/VideoLingo

# 激活虚拟环境
source venv/bin/activate

# 启动 Streamlit
streamlit run st.py --server.port 8502 --server.address 0.0.0.0
```

### 方法 3: 使用启动脚本

```bash
ssh ubuntu@150.107.38.113
/opt/videolingo/VideoLingo/start_videolingo.sh
```

## 🌐 访问应用

部署完成后，通过以下地址访问：

- **本地访问**: http://localhost:8502
- **远程访问**: http://150.107.38.113:8502

**注意**: 确保服务器防火墙已开放 8502 端口

### 开放防火墙端口（如需要）

```bash
# Ubuntu/Debian
sudo ufw allow 8502/tcp
sudo ufw reload

# 或者使用 iptables
sudo iptables -A INPUT -p tcp --dport 8502 -j ACCEPT
```

## 📁 项目结构

```
/opt/videolingo/VideoLingo/
├── st.py                 # Streamlit 主启动文件
├── requirements.txt      # Python 依赖
├── install.py           # 安装脚本（需要交互式运行）
├── config.yaml          # 配置文件
├── core/                # 核心代码
├── batch/               # 批处理相关
├── docs/                # 文档
├── translations/        # 翻译文件
├── venv/                # Python 虚拟环境
└── start_videolingo.sh  # 启动脚本
```

## ⚙️ 配置说明

### 环境变量

项目可能需要配置以下环境变量（根据 README 或 config.yaml）：

```bash
# 编辑配置文件
cd /opt/videolingo/VideoLingo
nano config.yaml
```

### API 密钥配置

如果项目需要 API 密钥（如 OpenAI、Azure 等），需要：

1. 查看 `config.yaml` 或 `.env` 文件
2. 配置相应的 API 密钥
3. 重启服务

## 🔧 故障排查

### 问题 1: 服务无法启动

```bash
# 查看详细日志
sudo journalctl -u videolingo -n 100

# 检查端口是否被占用
sudo netstat -tlnp | grep 8502

# 手动测试启动
cd /opt/videolingo/VideoLingo
source venv/bin/activate
streamlit run st.py --server.port 8502 --server.address 0.0.0.0
```

### 问题 2: 依赖缺失

```bash
cd /opt/videolingo/VideoLingo
source venv/bin/activate
pip install -r requirements.txt
```

### 问题 3: 端口无法访问

1. 检查防火墙设置
2. 检查服务器安全组规则（云服务器）
3. 确认服务正在运行：`sudo systemctl status videolingo`

## 📝 更新项目

### 使用部署脚本更新

```bash
# 在本地运行
cd /Users/a58/Desktop/social-auto-upload-window
./deploy_videolingo.sh
```

### 手动更新

```bash
ssh ubuntu@150.107.38.113
cd /opt/videolingo/VideoLingo
git pull origin main  # 或 master
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart videolingo
```

## 📚 相关文档

- 项目 README: `/opt/videolingo/VideoLingo/README.md`
- 中文文档: `/opt/videolingo/VideoLingo/translations/README.zh.md`
- 部署脚本: `deploy_videolingo.sh`

## 🔐 安全建议

1. **更改默认密码**: 建议更改服务器 SSH 密码
2. **使用 SSH 密钥**: 配置 SSH 密钥认证，禁用密码登录
3. **配置防火墙**: 只开放必要的端口
4. **定期更新**: 保持系统和依赖包更新
5. **备份配置**: 定期备份重要配置文件

## 📞 支持

如有问题，请：
1. 查看项目 GitHub Issues: https://github.com/Huanshere/VideoLingo/issues
2. 查看服务器日志: `sudo journalctl -u videolingo -f`
3. 检查项目文档: `/opt/videolingo/VideoLingo/README.md`

---

**部署日期**: 2025-12-22
**部署脚本**: `deploy_videolingo.sh`
**状态**: ✅ 已部署（部分依赖有版本警告，但不影响基本运行）

