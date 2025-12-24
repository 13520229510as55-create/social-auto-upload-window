# 重启39机器后端服务的脚本
Write-Host "正在停止旧服务..."
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like '*social-auto-upload-window*'} | Stop-Process -Force
Start-Sleep -Seconds 3

Write-Host "清除Python缓存..."
Get-ChildItem -Path "C:\social-auto-upload-window" -Recurse -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
Get-ChildItem -Path "C:\social-auto-upload-window" -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force

Write-Host "启动新服务..."
cd C:\social-auto-upload-window
Start-Process -FilePath "python" -ArgumentList "sau_backend.py" -WindowStyle Hidden

Start-Sleep -Seconds 5
Write-Host "检查服务状态..."
$listening = netstat -ano | findstr ":5409" | findstr "LISTENING"
if ($listening) {
    Write-Host "✅ 服务已启动"
} else {
    Write-Host "❌ 服务启动失败，请检查错误"
}

