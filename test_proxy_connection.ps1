# 测试代理连接脚本
# 在阿里云 Windows 服务器上执行

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🧪 测试代理服务器连接" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$proxyUrl = "http://150.107.38.113:10810"
Write-Host "代理地址: $proxyUrl" -ForegroundColor Gray
Write-Host ""

# 测试 1: 基本连接测试
Write-Host "[1/3] 测试代理服务器连接..." -ForegroundColor Yellow
try {
    $result = python -c "import requests; proxies = {'http': '$proxyUrl', 'https': '$proxyUrl'}; r = requests.get('https://www.google.com', proxies=proxies, timeout=10, verify=False); print('✅ 连接成功，状态码:', r.status_code)"
    Write-Host $result -ForegroundColor Green
} catch {
    Write-Host "❌ 连接失败: $_" -ForegroundColor Red
    Write-Host "   可能原因: 安全组未配置或代理服务器未运行" -ForegroundColor Yellow
}
Write-Host ""

# 测试 2: Google Cloud Storage 连接测试
Write-Host "[2/3] 测试 Google Cloud Storage 连接..." -ForegroundColor Yellow
try {
    $result = python -c "import requests; proxies = {'http': '$proxyUrl', 'https': '$proxyUrl'}; r = requests.get('https://storage.googleapis.com', proxies=proxies, timeout=10, verify=False); print('✅ 连接成功，状态码:', r.status_code)"
    Write-Host $result -ForegroundColor Green
} catch {
    Write-Host "❌ 连接失败: $_" -ForegroundColor Red
}
Write-Host ""

# 测试 3: 检查配置文件
Write-Host "[3/3] 检查配置文件..." -ForegroundColor Yellow
$confPath = "C:\social-auto-upload-window\conf.py"
if (Test-Path $confPath) {
    $proxyConfig = Get-Content $confPath | Select-String -Pattern "PROXY"
    Write-Host "代理配置:" -ForegroundColor Gray
    $proxyConfig | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
} else {
    Write-Host "❌ 配置文件不存在: $confPath" -ForegroundColor Red
}
Write-Host ""

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "💡 如果连接失败，请检查:" -ForegroundColor Yellow
Write-Host "  1. 云服务商安全组是否开放端口 10810" -ForegroundColor White
Write-Host "  2. 代理服务器是否正常运行" -ForegroundColor White
Write-Host "  3. 防火墙是否阻止连接" -ForegroundColor White
Write-Host "==========================================" -ForegroundColor Cyan

