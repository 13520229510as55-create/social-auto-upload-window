# Windows OpenSSH 服务器安装脚本
# 在 Windows 服务器上以管理员身份运行此脚本

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🔧 安装 OpenSSH 服务器" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 检查管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "❌ 错误: 需要管理员权限运行此脚本" -ForegroundColor Red
    Write-Host "请右键点击 PowerShell，选择'以管理员身份运行'" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "[1/5] 检查 OpenSSH 服务器状态..." -ForegroundColor Yellow
$sshService = Get-Service -Name sshd -ErrorAction SilentlyContinue

if ($sshService -and $sshService.Status -eq 'Running') {
    Write-Host "✅ OpenSSH 服务器已安装并运行中" -ForegroundColor Green
    Write-Host "   服务状态: $($sshService.Status)" -ForegroundColor Gray
} else {
    Write-Host "[2/5] 安装 OpenSSH 服务器..." -ForegroundColor Yellow
    
    # Windows 10/11 和 Windows Server 2019+ 自带 OpenSSH
    # 检查是否已安装但未启用
    $opensshFeature = Get-WindowsCapability -Online | Where-Object Name -like 'OpenSSH.Server*'
    
    if ($opensshFeature) {
        if ($opensshFeature.State -eq 'Installed') {
            Write-Host "✅ OpenSSH 服务器已安装，但可能未启动" -ForegroundColor Green
        } else {
            Write-Host "   正在安装 OpenSSH 服务器..." -ForegroundColor Gray
            Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ OpenSSH 服务器安装成功" -ForegroundColor Green
            } else {
                Write-Host "❌ 安装失败，尝试备用方法..." -ForegroundColor Red
                
                # 备用方法：使用 Chocolatey（如果已安装）
                if (Get-Command choco -ErrorAction SilentlyContinue) {
                    Write-Host "   使用 Chocolatey 安装..." -ForegroundColor Gray
                    choco install openssh -y
                } else {
                    Write-Host "❌ 自动安装失败" -ForegroundColor Red
                    Write-Host "请手动安装：" -ForegroundColor Yellow
                    Write-Host "1. 打开'设置' > '应用' > '可选功能'" -ForegroundColor Gray
                    Write-Host "2. 点击'添加功能'" -ForegroundColor Gray
                    Write-Host "3. 搜索并安装'OpenSSH 服务器'" -ForegroundColor Gray
                    pause
                    exit 1
                }
            }
        }
    } else {
        Write-Host "⚠️  未找到 OpenSSH 服务器功能" -ForegroundColor Yellow
        Write-Host "   尝试使用 Chocolatey 安装..." -ForegroundColor Gray
        if (Get-Command choco -ErrorAction SilentlyContinue) {
            choco install openssh -y
        } else {
            Write-Host "❌ 请手动安装 OpenSSH 服务器" -ForegroundColor Red
            pause
            exit 1
        }
    }
}

Write-Host ""
Write-Host "[3/5] 配置 OpenSSH 服务器..." -ForegroundColor Yellow

# 启动服务
Write-Host "   启动 OpenSSH 服务..." -ForegroundColor Gray
Start-Service sshd
Set-Service -Name sshd -StartupType 'Automatic'

Write-Host "✅ OpenSSH 服务已启动并设置为自动启动" -ForegroundColor Green

Write-Host ""
Write-Host "[4/5] 配置防火墙规则..." -ForegroundColor Yellow

# 添加防火墙规则（如果不存在）
$firewallRule = Get-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -ErrorAction SilentlyContinue
if (-not $firewallRule) {
    Write-Host "   添加防火墙规则..." -ForegroundColor Gray
    New-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -DisplayName "OpenSSH Server (sshd)" -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22 | Out-Null
    Write-Host "✅ 防火墙规则已添加" -ForegroundColor Green
} else {
    Write-Host "✅ 防火墙规则已存在" -ForegroundColor Green
}

Write-Host ""
Write-Host "[5/5] 验证安装..." -ForegroundColor Yellow

$sshService = Get-Service -Name sshd -ErrorAction SilentlyContinue
if ($sshService -and $sshService.Status -eq 'Running') {
    Write-Host "✅ OpenSSH 服务器运行正常" -ForegroundColor Green
    Write-Host "   服务状态: $($sshService.Status)" -ForegroundColor Gray
    Write-Host "   监听端口: 22" -ForegroundColor Gray
} else {
    Write-Host "❌ OpenSSH 服务器未运行" -ForegroundColor Red
    Write-Host "   请检查服务状态: Get-Service sshd" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ 安装完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 下一步：" -ForegroundColor Yellow
Write-Host "   1. 确保阿里云安全组开放了 22 端口" -ForegroundColor Gray
Write-Host "   2. 测试连接: ssh administrator@39.105.227.6" -ForegroundColor Gray
Write-Host "   3. 安装完成后，可以运行远程部署脚本" -ForegroundColor Gray
Write-Host ""
pause

