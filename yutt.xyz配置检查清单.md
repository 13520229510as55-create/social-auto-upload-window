# yutt.xyz 配置检查清单

## ✅ 已完成的配置

### 1. Nginx 配置 ✅
- [x] 创建 `/etc/nginx/sites-available/yutt.xyz` 配置文件
- [x] 创建软链接到 `/etc/nginx/sites-enabled/yutt.xyz`
- [x] Nginx 配置语法正确
- [x] Nginx 服务正常运行
- [x] 配置已加载

### 2. 服务配置 ✅
- [x] Social 前端服务运行正常 (sau-frontend)
- [x] Social 后端服务运行正常 (sau-backend)
- [x] n8n 服务正常运行（通过 aicode.ltd 访问）

### 3. 路由配置 ✅
- [x] yutt.xyz/ → Social 前端（根路径）
- [x] yutt.xyz/api/ → Social 后端 API
- [x] yutt.xyz/assets/ → 静态资源（缓存优化）
- [x] aicode.ltd/ → n8n 服务（保持不变）

## ⚠️ 待完成的配置

### 1. DNS 配置（关键步骤）

**当前状态**: 已在阿里云配置 A 记录，但域名 nameserver 仍指向 Cloudflare

**需要操作**:
1. 在域名注册商处修改 nameserver：
   - 从 Cloudflare: `earl.ns.cloudflare.com`, `melina.ns.cloudflare.com`
   - 改为阿里云: `dns11.hichina.com`, `dns12.hichina.com`

2. 等待 DNS 生效（通常 10 分钟到 24 小时）

3. 验证 DNS 解析：
   ```bash
   dig yutt.xyz A
   # 应该返回: 150.107.38.113
   
   dig www.yutt.xyz A
   # 应该返回: 150.107.38.113
   ```

### 2. SSL 证书申请（DNS 生效后）

**命令**:
```bash
sudo certbot --nginx -d yutt.xyz -d www.yutt.xyz
```

**或者非交互模式**:
```bash
sudo certbot --nginx -d yutt.xyz -d www.yutt.xyz --non-interactive --agree-tos --email your-email@example.com
```

**预期结果**:
- Certbot 自动申请 Let's Encrypt SSL 证书
- 自动更新 Nginx 配置，添加 HTTPS 支持
- 配置自动续期

### 3. 验证访问

DNS 和 SSL 配置完成后，验证：
- [ ] HTTP: http://yutt.xyz （应该能访问）
- [ ] HTTPS: https://yutt.xyz （SSL 证书申请后）
- [ ] 前端路由: https://yutt.xyz/#/production-center （应该能正常访问）
- [ ] API 接口: https://yutt.xyz/api/ （应该能正常访问）

## 📋 完整配置流程

### 步骤 1: 修改 Nameserver（在域名注册商处）
1. 登录域名注册商控制台
2. 找到域名 `yutt.xyz` 的 DNS 设置
3. 将 nameserver 修改为：
   - `dns11.hichina.com`
   - `dns12.hichina.com`
4. 保存并等待生效

### 步骤 2: 验证 DNS 解析
```bash
# 在服务器上执行
dig yutt.xyz A
dig www.yutt.xyz A

# 或在本地执行
nslookup yutt.xyz
```

### 步骤 3: 申请 SSL 证书
```bash
sudo certbot --nginx -d yutt.xyz -d www.yutt.xyz
```

### 步骤 4: 验证 HTTPS 访问
- 访问 https://yutt.xyz
- 检查浏览器地址栏显示锁图标
- 测试前端功能是否正常

## 🔍 当前配置详情

### Nginx 配置位置
- 配置文件: `/etc/nginx/sites-available/yutt.xyz`
- 启用链接: `/etc/nginx/sites-enabled/yutt.xyz`

### 服务状态
- Social 前端: PM2 运行中 (sau-frontend)
- Social 后端: PM2 运行中 (sau-backend)
- Nginx: systemd 服务运行中

### 端口配置
- 前端服务: localhost:5173 (开发模式)
- 后端服务: localhost:5409
- n8n 服务: localhost:5678
- Nginx: 80, 443

## 🛠️ 常用管理命令

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
pm2 list
sudo systemctl status nginx
```

## ⚠️ 注意事项

1. **DNS 生效时间**: 修改 nameserver 后，DNS 生效可能需要 10 分钟到 24 小时
2. **SSL 证书**: 只有在 DNS 生效后才能申请 SSL 证书
3. **证书续期**: Let's Encrypt 证书有效期为 90 天，Certbot 会自动续期
4. **服务依赖**: 确保 Social 前端和后端服务正常运行

## 📞 故障排查

### DNS 未生效
```bash
# 检查 DNS 解析
dig yutt.xyz A

# 如果返回空，说明 DNS 还未生效，需要等待或检查 nameserver 配置
```

### SSL 证书申请失败
```bash
# 查看详细错误
sudo certbot --nginx -d yutt.xyz -d www.yutt.xyz -v

# 检查 DNS 是否生效
dig yutt.xyz A
```

### 访问 404 错误
```bash
# 检查 Nginx 配置
sudo nginx -t

# 检查前端文件是否存在
ls -la /home/ubuntu/social-auto-upload/sau_frontend/dist/

# 查看 Nginx 错误日志
sudo tail -f /var/log/nginx/error.log
```

