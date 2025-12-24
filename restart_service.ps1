# 完整重启服务脚本
Write-Host '========================================'  -ForegroundColor Cyan
Write-Host '完整重启后端服务' -ForegroundColor Cyan
Write-Host '========================================' -ForegroundColor Cyan

# 1. 停止所有Python进程
Write-Host "`n[1/5] 停止所有Python进程..." -ForegroundColor Yellow
taskkill /F /IM python.exe 2>&1 | Out-Null
Start-Sleep -Seconds 3
Write-Host '✅ 完成' -ForegroundColor Green

# 2. 清除缓存
Write-Host "`n[2/5] 清除Python缓存..." -ForegroundColor Yellow
cd C:\social-auto-upload-window
Get-ChildItem -Recurse -Filter '__pycache__' -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
Get-ChildItem -Recurse -Filter '*.pyc' -ErrorAction SilentlyContinue | Remove-Item -Force
Write-Host '✅ 完成' -ForegroundColor Green

# 3. 验证代码文件
Write-Host "`n[3/5] 验证代码文件..." -ForegroundColor Yellow
$file = Get-Item 'C:\social-auto-upload-window\sau_backend.py'
Write-Host "   文件大小: $([math]::Round($file.Length/1KB, 2)) KB"
Write-Host "   修改时间: $($file.LastWriteTime)"
Write-Host '✅ 完成' -ForegroundColor Green

# 4. 确保数据库存在
Write-Host "`n[4/5] 检查数据库..." -ForegroundColor Yellow
if (-not (Test-Path 'C:\social-auto-upload-window\db')) {
    New-Item -ItemType Directory -Path 'C:\social-auto-upload-window\db' -Force | Out-Null
}
Write-Host '✅ 完成' -ForegroundColor Green

# 5. 启动服务
Write-Host "`n[5/5] 启动服务..." -ForegroundColor Yellow
$proc = Start-Process -FilePath 'python' -ArgumentList 'sau_backend.py' -WindowStyle Hidden -PassThru -WorkingDirectory 'C:\social-auto-upload-window'
Write-Host "   进程PID: $($proc.Id)" -ForegroundColor Cyan

# 等待服务启动
Write-Host "`n等待服务启动..." -ForegroundColor Yellow
for ($i = 1; $i -le 15; $i++) {
    Start-Sleep -Seconds 1
    $listening = netstat -ano | findstr ':5409' | findstr 'LISTENING'
    if ($listening) {
        Write-Host "`r✅ 服务已启动 (用时 $i 秒)" -ForegroundColor Green
        break
    }
    Write-Host "`r   等待中... $i/15秒" -NoNewline
}

# 验证
Write-Host "`n`n========================================"  -ForegroundColor Cyan
Write-Host '验证服务状态' -ForegroundColor Cyan
Write-Host '========================================' -ForegroundColor Cyan

$listening = netstat -ano | findstr ':5409' | findstr 'LISTENING'
if ($listening) {
    Write-Host '✅ 端口5409正在监听' -ForegroundColor Green
    $pid = ($listening -split '\s+')[-1]
    Write-Host "   PID: $pid" -ForegroundColor Gray
} else {
    Write-Host '❌ 端口5409未监听' -ForegroundColor Red
}

Write-Host "`n测试API..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri 'http://localhost:5409/getAccounts' -Method GET -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host '✅ API响应正常 (200 OK)' -ForegroundColor Green
        $json = $response.Content | ConvertFrom-Json
        Write-Host "   返回数据条数: $($json.data.Count)" -ForegroundColor Cyan
    } else {
        Write-Host "⚠️ API响应异常 (状态码: $($response.StatusCode))" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ API测试失败: $_" -ForegroundColor Red
}

Write-Host "`n========================================"  -ForegroundColor Cyan
Write-Host '重启完成！' -ForegroundColor Green
Write-Host '========================================' -ForegroundColor Cyan

