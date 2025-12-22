# PowerShell 环境检查脚本
# 在服务器上执行: PowerShell -ExecutionPolicy Bypass -File quick_check.ps1

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🔍 检查服务器环境配置" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$allOk = $true

# 1. 检查 Python
Write-Host "[1/7] 检查 Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python 已安装: $pythonVersion" -ForegroundColor Green
        
        # 检查版本
        $versionCheck = python -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Python 版本符合要求 (>= 3.10)" -ForegroundColor Green
        } else {
            Write-Host "⚠️  警告: Python 版本低于 3.10" -ForegroundColor Yellow
        }
    } else {
        Write-Host "❌ Python 未安装或未添加到 PATH" -ForegroundColor Red
        $allOk = $false
    }
} catch {
    Write-Host "❌ Python 未安装或未添加到 PATH" -ForegroundColor Red
    $allOk = $false
}
Write-Host ""

# 2. 检查 pip
Write-Host "[2/7] 检查 pip..." -ForegroundColor Yellow
try {
    $pipVersion = python -m pip --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ pip 已安装: $($pipVersion -split ' ')[1]" -ForegroundColor Green
    } else {
        Write-Host "❌ pip 未安装" -ForegroundColor Red
        $allOk = $false
    }
} catch {
    Write-Host "❌ pip 未安装" -ForegroundColor Red
    $allOk = $false
}
Write-Host ""

# 3. 检查 Node.js
Write-Host "[3/7] 检查 Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Node.js 已安装: $nodeVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ Node.js 未安装或未添加到 PATH" -ForegroundColor Red
        $allOk = $false
    }
} catch {
    Write-Host "❌ Node.js 未安装或未添加到 PATH" -ForegroundColor Red
    $allOk = $false
}
Write-Host ""

# 4. 检查 npm
Write-Host "[4/7] 检查 npm..." -ForegroundColor Yellow
try {
    $npmVersion = npm --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ npm 已安装: $npmVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ npm 未安装" -ForegroundColor Red
        $allOk = $false
    }
} catch {
    Write-Host "❌ npm 未安装" -ForegroundColor Red
    $allOk = $false
}
Write-Host ""

# 5. 检查端口占用
Write-Host "[5/7] 检查端口占用情况..." -ForegroundColor Yellow
$port5409 = Get-NetTCPConnection -LocalPort 5409 -ErrorAction SilentlyContinue
if ($port5409) {
    Write-Host "⚠️  端口 5409 已被占用" -ForegroundColor Yellow
    $port5409 | Format-Table -AutoSize
} else {
    Write-Host "✅ 端口 5409 未被占用" -ForegroundColor Green
}

$port5173 = Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue
if ($port5173) {
    Write-Host "⚠️  端口 5173 已被占用" -ForegroundColor Yellow
    $port5173 | Format-Table -AutoSize
} else {
    Write-Host "✅ 端口 5173 未被占用" -ForegroundColor Green
}
Write-Host ""

# 6. 检查防火墙规则
Write-Host "[6/7] 检查防火墙规则..." -ForegroundColor Yellow
$fw5409 = Get-NetFirewallRule | Where-Object { $_.DisplayName -like "*5409*" -or $_.DisplayName -like "*social*" }
if ($fw5409) {
    Write-Host "✅ 找到端口 5409 相关防火墙规则" -ForegroundColor Green
} else {
    Write-Host "⚠️  未找到端口 5409 的防火墙规则" -ForegroundColor Yellow
    Write-Host "   建议添加规则允许端口 5409" -ForegroundColor Gray
}

$fw5173 = Get-NetFirewallRule | Where-Object { $_.DisplayName -like "*5173*" -or $_.DisplayName -like "*social*" }
if ($fw5173) {
    Write-Host "✅ 找到端口 5173 相关防火墙规则" -ForegroundColor Green
} else {
    Write-Host "⚠️  未找到端口 5173 的防火墙规则" -ForegroundColor Yellow
    Write-Host "   建议添加规则允许端口 5173" -ForegroundColor Gray
}
Write-Host ""

# 7. 检查项目目录
Write-Host "[7/7] 检查项目目录..." -ForegroundColor Yellow
$projectDir = "C:\social-auto-upload-window"
if (Test-Path $projectDir) {
    Write-Host "✅ 项目目录存在: $projectDir" -ForegroundColor Green
    
    if (Test-Path "$projectDir\sau_backend.py") {
        Write-Host "✅ 后端文件存在" -ForegroundColor Green
    } else {
        Write-Host "⚠️  后端文件不存在，需要部署" -ForegroundColor Yellow
    }
    
    if (Test-Path "$projectDir\sau_frontend") {
        Write-Host "✅ 前端目录存在" -ForegroundColor Green
    } else {
        Write-Host "⚠️  前端目录不存在，需要部署" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  项目目录不存在，需要部署" -ForegroundColor Yellow
}
Write-Host ""

# 总结
Write-Host "==========================================" -ForegroundColor Cyan
if ($allOk) {
    Write-Host "✅ 环境检查通过！可以开始部署" -ForegroundColor Green
} else {
    Write-Host "❌ 环境检查未通过，请先解决上述问题" -ForegroundColor Red
}
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 下一步操作：" -ForegroundColor Yellow
Write-Host "   1. 如果环境检查通过，执行: deploy_on_windows.bat" -ForegroundColor Gray
Write-Host "   2. 部署完成后，执行: start-win.bat" -ForegroundColor Gray
Write-Host ""

