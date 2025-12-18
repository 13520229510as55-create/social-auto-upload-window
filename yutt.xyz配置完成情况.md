# yutt.xyz 配置完成情况总结

## ✅ 已完成配置（服务器端）

### 1. Nginx 配置 ✅
- ✅ 配置文件已创建: `/etc/nginx/sites-available/yutt.xyz`
- ✅ 已启用: `/etc/nginx/sites-enabled/yutt.xyz`
- ✅ 配置语法正确: `nginx -t` 通过
- ✅ Nginx 服务运行正常

### 2. 服务配置 ✅
- ✅ Social 前端服务: PM2 运行中 (sau-frontend)
- ✅ Social 后端服务: PM2 运行中 (sau-backend)
- ✅ n8n 服务: 正常运行（通过 aicode.ltd 访问，不受影响）

### 3. 路由配置 ✅
- ✅ `yutt.xyz/` → Social 前端应用（根路径）
- ✅ `yutt.xyz/assets/` → 静态资源（缓存优化）
- ✅ `yutt.xyz/api/` → Social 后端 API 服务
- ✅ `aicode.ltd/` → n8n 服务（保持不变）

### 4. 前端文件 ✅
- ✅ 前端构建文件存在: `/home/ubuntu/social-auto-upload/sau_frontend/dist/`
- ✅ index.html 文件正常

## ⚠️ 待完成配置（需要您操作）

### 1. DNS Nameserver 配置（关键步骤）⚠️

**问题**: 根据截图，域名当前使用的是 Cloudflare 的 nameserver，但 DNS 记录配置在阿里云。

**需要操作**:
1. 登录域名注册商控制台（不是阿里云，是您购买域名的注册商）
2. 找到域名 `yutt.xyz` 的 DNS/Nameserver 设置
3. 将 nameserver 从：
   ```
   earl.ns.cloudflare.com
   melina.ns.cloudflare.com
   ```
   修改为阿里云的 nameserver：
   ```
   dns11.hichina.com
   dns12.hichina.com
   ```
4. 保存并等待生效（通常 10 分钟到 24 小时）

**验证 DNS 是否生效**:
```bash
# 在服务器上执行
dig yutt.xyz A
# 应该返回: 150.107.38.113

# 或在本地执行
nslookup yutt.xyz
```

### 2. SSL 证书申请（DNS 生效后）⚠️

**前提条件**: DNS 必须生效后才能申请 SSL 证书

**申请命令**:
```bash
sudo certbot --nginx -d yutt.xyz -d www.yutt.xyz
```

**或者使用非交互模式**:
```bash
sudo certbot --nginx -d yutt.xyz -d www.yutt.xyz --non-interactive --agree-tos --email your-email@example.com
```

**预期结果**:
- Certbot 自动申请 Let's Encrypt SSL 证书
- 自动更新 Nginx 配置文件，添加 HTTPS 支持
- 配置自动续期（证书有效期 90 天）

### 3. 验证访问（DNS 和 SSL 配置后）⚠️

配置完成后，验证以下访问：
- [ ] HTTP: http://yutt.xyz
- [ ] HTTPS: https://yutt.xyz
- [ ] 前端路由: https://yutt.xyz/#/production-center
- [ ] API 接口: https://yutt.xyz/api/

## 📋 完整操作步骤

### 步骤 1: 修改 Nameserver（在域名注册商处）

1. 登录您购买 `yutt.xyz` 域名的注册商控制台
   - 可能是 GoDaddy, Namecheap, Cloudflare, 或其他注册商
2. 找到域名管理/DNS 设置
3. 修改 Nameserver 为：
   ```
   dns11.hichina.com
   dns12.hichina.com
   ```
4. 保存更改

### 步骤 2: 等待 DNS 生效

- 通常需要 10 分钟到 24 小时
- 可以使用以下命令检查：
  ```bash
  dig yutt.xyz A
  nslookup yutt.xyz
  ```

### 步骤 3: 申请 SSL 证书

DNS 生效后，在服务器上执行：
```bash
sudo certbot --nginx -d yutt.xyz -d www.yutt.xyz
```

### 步骤 4: 验证 HTTPS 访问

访问 https://yutt.xyz 确认：
- 浏览器显示锁图标
- 前端功能正常
- API 接口正常

## 🔍 当前配置详情

### Nginx 配置
- **配置文件**: `/etc/nginx/sites-available/yutt.xyz`
- **启用链接**: `/etc/nginx/sites-enabled/yutt.xyz`
- **状态**: 已加载并运行

### 服务端口
- **前端服务**: localhost:5173 (开发模式，通过 Nginx 代理)
- **后端服务**: localhost:5409 (通过 Nginx /api/ 代理)
- **n8n 服务**: localhost:5678 (通过 aicode.ltd 访问)

### 域名路由
- **yutt.xyz/** → Social 前端（根路径直接访问）
- **yutt.xyz/api/** → Social 后端 API
- **aicode.ltd/** → n8n 服务（保持不变）
- **aicode.ltd/app/** → Social 前端（仍然可用）

## 🛠️ 管理命令

### 检查 DNS 解析
```bash
dig yutt.xyz A
nslookup yutt.xyz
```

### 检查 Nginx 配置
```bash
sudo nginx -t
sudo cat /etc/nginx/sites-available/yutt.xyz
```

### 重新加载 Nginx
```bash
sudo nginx -s reload
```

### 查看 SSL 证书
```bash
sudo certbot certificates
```

### 检查服务状态
```bash
export PATH=~/.npm-global/bin:$PATH
pm2 list
sudo systemctl status nginx
```

## ⚠️ 重要提示

1. **DNS Nameserver 必须修改**: 如果域名仍使用 Cloudflare 的 nameserver，阿里云配置的 DNS 记录不会生效
2. **DNS 生效后才能申请 SSL**: Let's Encrypt 需要验证域名所有权，DNS 必须生效
3. **证书自动续期**: Certbot 已配置自动续期，无需手动操作
4. **不影响 n8n 服务**: aicode.ltd 的配置保持不变，n8n 服务不受影响

## 📞 故障排查

### DNS 未生效
```bash
# 检查 DNS 解析
dig yutt.xyz A

# 如果返回空，检查：
# 1. Nameserver 是否已修改为阿里云的
# 2. 是否等待足够时间（最长 24 小时）
```

### SSL 证书申请失败
```bash
# 查看详细错误
sudo certbot --nginx -d yutt.xyz -d www.yutt.xyz -v

# 常见原因：
# 1. DNS 未生效
# 2. 80 端口被占用
# 3. 防火墙阻止访问
```

### 访问 404 错误
```bash
# 检查 Nginx 配置
sudo nginx -t

# 检查前端文件
ls -la /home/ubuntu/social-auto-upload/sau_frontend/dist/

# 查看错误日志
sudo tail -f /var/log/nginx/error.log
```

## ✅ 总结

**服务器端配置**: 100% 完成 ✅
- Nginx 配置完成
- 服务运行正常
- 路由配置正确

**待您完成**:
1. ⚠️ 修改域名 Nameserver 为阿里云的（关键步骤）
2. ⚠️ 等待 DNS 生效
3. ⚠️ 申请 SSL 证书（DNS 生效后）

完成以上步骤后，即可通过 https://yutt.xyz 访问 Social 服务！

