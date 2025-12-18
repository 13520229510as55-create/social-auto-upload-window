# yutt.xyz 域名配置说明

## ✅ 已完成的配置

### 1. Nginx 配置
- 已创建 `/etc/nginx/sites-available/yutt.xyz` 配置文件
- 已创建软链接到 `/etc/nginx/sites-enabled/yutt.xyz`
- 配置已加载并生效

### 2. 服务配置
- **yutt.xyz** → Social 前端服务（根路径）
- **yutt.xyz/api/** → Social 后端服务（API 代理）
- **aicode.ltd** → n8n 服务（保持不变，不受影响）

## 📋 需要完成的步骤

### 步骤 1: 配置 DNS 记录

在您的域名 DNS 提供商处添加以下 A 记录：

```
类型: A
主机记录: @ (或 yutt.xyz)
记录值: 150.107.38.113
TTL: 600 (或默认)

类型: A  
主机记录: www
记录值: 150.107.38.113
TTL: 600 (或默认)
```

### 步骤 2: 等待 DNS 生效

DNS 记录生效通常需要几分钟到几小时。您可以使用以下命令检查：

```bash
# 检查 DNS 解析
nslookup yutt.xyz
dig yutt.xyz A

# 应该返回: 150.107.38.113
```

### 步骤 3: 申请 SSL 证书

DNS 生效后，在服务器上执行以下命令申请 SSL 证书：

```bash
sudo certbot --nginx -d yutt.xyz -d www.yutt.xyz
```

或者使用非交互模式（需要提供邮箱）：

```bash
sudo certbot --nginx -d yutt.xyz -d www.yutt.xyz --non-interactive --agree-tos --email your-email@example.com
```

Certbot 会自动：
- 申请 Let's Encrypt SSL 证书
- 更新 Nginx 配置文件，添加 HTTPS 支持
- 配置自动续期

### 步骤 4: 验证访问

DNS 和 SSL 配置完成后，访问：
- **HTTP**: http://yutt.xyz
- **HTTPS**: https://yutt.xyz

## 🔍 当前配置详情

### yutt.xyz 配置
- **根路径 (/)**: Social 前端应用
- **静态资源 (/assets/)**: 前端静态文件，缓存 1 年
- **API 接口 (/api/)**: 代理到后端服务 (localhost:5409)

### aicode.ltd 配置（保持不变）
- **根路径 (/)**: n8n 服务 (localhost:5678)
- **/app 路径**: Social 前端应用（仍然可用）
- **/api/ 路径**: Social 后端服务

## 🛠️ 管理命令

### 查看配置
```bash
sudo cat /etc/nginx/sites-available/yutt.xyz
```

### 测试配置
```bash
sudo nginx -t
```

### 重新加载配置
```bash
sudo nginx -s reload
```

### 查看 SSL 证书状态
```bash
sudo certbot certificates
```

### 手动续期 SSL 证书
```bash
sudo certbot renew
```

## ⚠️ 注意事项

1. **DNS 配置**: 必须先将 DNS 记录指向服务器 IP，才能申请 SSL 证书
2. **SSL 证书**: Let's Encrypt 证书有效期为 90 天，Certbot 会自动续期
3. **服务状态**: 确保以下服务正常运行：
   - Social 前端: `pm2 list | grep sau-frontend`
   - Social 后端: `pm2 list | grep sau-backend`
   - n8n 服务: 通过 aicode.ltd 访问

## 📞 故障排查

如果访问出现问题：

1. **检查 DNS 解析**:
   ```bash
   nslookup yutt.xyz
   ```

2. **检查 Nginx 状态**:
   ```bash
   sudo systemctl status nginx
   ```

3. **查看 Nginx 错误日志**:
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

4. **检查服务状态**:
   ```bash
   pm2 list
   ```

5. **测试本地访问**:
   ```bash
   curl -H 'Host: yutt.xyz' http://localhost/
   ```

