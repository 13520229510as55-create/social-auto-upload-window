# 代理服务器搭建完成 ✅

## 📋 服务器信息

### 海外代理服务器
- **IP 地址**: `150.107.38.113`
- **用户名**: `ubuntu`
- **操作系统**: Ubuntu Linux

### 代理服务端口
- **HTTP 代理**: `http://150.107.38.113:10810`
- **SOCKS5 代理**: `150.107.38.113:10809`
- **VMess 端口**: `10808` (可选)

### 阿里云服务器
- **IP 地址**: `39.105.227.6`
- **配置路径**: `C:\social-auto-upload-window\conf.py`

---

## ✅ 已完成的工作

1. ✅ **代理服务器搭建**
   - 已安装并配置 V2Ray
   - 服务运行正常
   - 端口监听正常

2. ✅ **阿里云服务器配置**
   - `conf.py` 已更新代理地址
   - 配置内容：
     ```python
     HTTP_PROXY = "http://150.107.38.113:10810"
     HTTPS_PROXY = "http://150.107.38.113:10810"
     ```

---

## ⚠️ 重要：配置云服务商安全组

**这是最关键的一步！** 如果安全组没有配置，阿里云服务器将无法连接到代理服务器。

### 配置步骤

1. **登录云服务商控制台**
   - 找到服务器 `150.107.38.113` 所在的控制台

2. **找到安全组配置**
   - 进入服务器管理页面
   - 找到"安全组"或"防火墙"设置

3. **添加入站规则**
   需要开放以下端口：
   - **10810** (TCP) - HTTP 代理
   - **10809** (TCP) - SOCKS5 代理
   - **10808** (TCP) - VMess（可选）

4. **设置源地址**
   - 为了安全，建议将源地址设置为：`39.105.227.6/32`
   - 或者设置为：`0.0.0.0/0`（允许所有 IP，安全性较低）

### 不同云服务商的配置位置

- **阿里云**: 云服务器 ECS → 网络与安全 → 安全组
- **腾讯云**: 云服务器 CVM → 安全组
- **AWS**: EC2 → Security Groups
- **Azure**: Network Security Groups
- **Google Cloud**: VPC Network → Firewall rules

---

## 🧪 测试代理连接

### 方法 1: 从阿里云服务器测试

```powershell
# 在阿里云服务器上执行
python -c "import requests; proxies = {'http': 'http://150.107.38.113:10810', 'https': 'http://150.107.38.113:10810'}; r = requests.get('https://www.google.com', proxies=proxies, timeout=10, verify=False); print('状态码:', r.status_code)"
```

### 方法 2: 使用 curl 测试

```bash
# 从本地或阿里云服务器执行
curl -x http://150.107.38.113:10810 https://www.google.com -I --connect-timeout 10
```

### 方法 3: 测试 Google Cloud Storage

```powershell
# 在阿里云服务器上执行
python -c "import requests; proxies = {'http': 'http://150.107.38.113:10810', 'https': 'http://150.107.38.113:10810'}; r = requests.get('https://storage.googleapis.com', proxies=proxies, timeout=10, verify=False); print('状态码:', r.status_code)"
```

---

## 🚀 重启后端服务

配置完成后，需要重启后端服务使代理配置生效：

```powershell
# 在阿里云服务器上执行
# 如果使用 PM2
pm2 restart sau_backend

# 或者直接运行
cd C:\social-auto-upload-window
python sau_backend.py
```

---

## 📝 验证配置

### 检查代理配置

```powershell
# 在阿里云服务器上执行
type C:\social-auto-upload-window\conf.py | findstr PROXY
```

应该看到：
```
HTTP_PROXY = "http://150.107.38.113:10810"
HTTPS_PROXY = "http://150.107.38.113:10810"
```

### 检查代理服务器状态

```bash
# 在代理服务器上执行
sudo systemctl status v2ray
sudo netstat -tlnp | grep 10810
```

---

## 🔧 故障排查

### 问题 1: 连接超时

**原因**: 安全组未配置或端口未开放

**解决**:
1. 检查云服务商安全组配置
2. 确认端口 10810 已开放
3. 确认源地址包含阿里云服务器 IP

### 问题 2: 代理拒绝连接

**原因**: V2Ray 服务未运行

**解决**:
```bash
# 在代理服务器上执行
sudo systemctl restart v2ray
sudo systemctl status v2ray
```

### 问题 3: SSL 错误

**原因**: 代理不支持 HTTPS 或配置问题

**解决**: 
- 代码中已设置 `verify=False` 来绕过 SSL 验证
- 确保使用 HTTP 代理端口 10810

---

## 📚 相关文档

- `GOOGLE_ACCESS_SOLUTION.md` - 阿里云访问 Google 解决方案
- `conf.py` - 后端配置文件

---

## ✅ 完成检查清单

- [x] 代理服务器搭建完成
- [x] V2Ray 服务运行正常
- [x] 阿里云服务器配置已更新
- [ ] **云服务商安全组已配置** ⚠️ **必须完成**
- [ ] 代理连接测试通过
- [ ] 后端服务已重启
- [ ] 视频下载功能测试通过

---

**下一步**: 配置云服务商安全组，然后测试代理连接！

