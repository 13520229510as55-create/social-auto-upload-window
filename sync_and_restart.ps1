# 同步代码并重启服务的PowerShell脚本
# 在39服务器上执行此脚本

Write-Host "=== 同步代码并重启服务 ===" -ForegroundColor Cyan

# 1. 停止后端服务
Write-Host "`n[1/3] 停止后端服务..." -ForegroundColor Yellow
$procs = Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like '*social-auto-upload-window*'}
if ($procs) {
    $procs | ForEach-Object {
        Write-Host "  停止进程 PID: $($_.Id)"
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 2
    Write-Host "  ✅ 服务已停止" -ForegroundColor Green
} else {
    Write-Host "  ℹ️ 未找到运行中的服务" -ForegroundColor Gray
}

# 2. 清除Python缓存
Write-Host "`n[2/3] 清除Python缓存..." -ForegroundColor Yellow
Get-ChildItem -Path 'C:\social-auto-upload-window' -Recurse -Filter '__pycache__' -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
Get-ChildItem -Path 'C:\social-auto-upload-window' -Recurse -Filter '*.pyc' -ErrorAction SilentlyContinue | Remove-Item -Force
Write-Host "  ✅ 缓存已清除" -ForegroundColor Green

# 3. 启动后端服务
Write-Host "`n[3/3] 启动后端服务..." -ForegroundColor Yellow
cd C:\social-auto-upload-window
Start-Process -FilePath 'python' -ArgumentList 'sau_backend.py' -WindowStyle Hidden
Start-Sleep -Seconds 8

# 检查服务状态
Write-Host "`n=== 检查服务状态 ===" -ForegroundColor Cyan
$listening = netstat -ano | findstr ':5409' | findstr 'LISTENING'
if ($listening) {
    Write-Host "✅ 后端服务已启动" -ForegroundColor Green
    netstat -ano | findstr ':5409' | findstr 'LISTENING'
} else {
    Write-Host "❌ 后端服务启动失败，请检查日志" -ForegroundColor Red
}

Write-Host "`n=== 完成 ===" -ForegroundColor Cyan

