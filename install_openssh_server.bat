@echo off
TITLE 安装 OpenSSH 服务器

echo ==========================================
echo 🔧 安装 OpenSSH 服务器
echo ==========================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 需要管理员权限运行此脚本
    echo 请右键点击此文件，选择"以管理员身份运行"
    pause
    exit /b 1
)

echo [1/5] 检查 OpenSSH 服务器状态...
sc query sshd >nul 2>&1
if errorlevel 1 (
    echo    未找到 OpenSSH 服务，开始安装...
) else (
    echo ✅ OpenSSH 服务器已安装
    goto :start_service
)

echo.
echo [2/5] 安装 OpenSSH 服务器...
echo    方法1: 使用 Windows 可选功能...

REM 使用 PowerShell 安装
powershell -Command "Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0" 2>nul
if errorlevel 1 (
    echo    PowerShell 安装失败，尝试图形界面安装...
    echo.
    echo    请手动安装：
    echo    1. 按 Win+I 打开"设置"
    echo    2. 点击"应用" ^> "可选功能"
    echo    3. 点击"添加功能"
    echo    4. 搜索"OpenSSH 服务器"并安装
    echo.
    pause
    exit /b 1
)

:start_service
echo.
echo [3/5] 启动 OpenSSH 服务...
sc config sshd start= auto >nul 2>&1
net start sshd >nul 2>&1
if errorlevel 1 (
    echo    启动服务...
    net start sshd
    if errorlevel 1 (
        echo ❌ 启动服务失败
        pause
        exit /b 1
    )
)
echo ✅ OpenSSH 服务已启动并设置为自动启动

echo.
echo [4/5] 配置防火墙规则...
netsh advfirewall firewall show rule name="OpenSSH-Server-In-TCP" >nul 2>&1
if errorlevel 1 (
    echo    添加防火墙规则...
    netsh advfirewall firewall add rule name="OpenSSH-Server-In-TCP" dir=in action=allow protocol=TCP localport=22 >nul 2>&1
    echo ✅ 防火墙规则已添加
) else (
    echo ✅ 防火墙规则已存在
)

echo.
echo [5/5] 验证安装...
sc query sshd | findstr "RUNNING" >nul 2>&1
if errorlevel 1 (
    echo ❌ OpenSSH 服务器未运行
    echo    请检查服务状态
) else (
    echo ✅ OpenSSH 服务器运行正常
    echo    监听端口: 22
)

echo.
echo ==========================================
echo ✅ 安装完成！
echo ==========================================
echo.
echo 📋 下一步：
echo    1. 确保阿里云安全组开放了 22 端口
echo    2. 测试连接: ssh administrator@39.105.227.6
echo    3. 安装完成后，可以运行远程部署脚本
echo.
pause

