@echo off
REM 重启前端服务脚本
REM 在服务器上执行此脚本

echo ==========================================
echo 重启前端服务
echo ==========================================
echo.

echo 1. 停止现有前端服务...
taskkill /PID 6860 /F
if %ERRORLEVEL% EQU 0 (
    echo    [成功] 前端服务已停止
) else (
    echo    [警告] 无法停止服务或服务未运行
)

echo.
echo 2. 等待3秒...
timeout /t 3 /nobreak >nul

echo.
echo 3. 切换到项目目录...
cd /d C:\social-auto-upload-window
if %ERRORLEVEL% EQU 0 (
    echo    [成功] 已切换到项目目录
) else (
    echo    [错误] 无法切换到项目目录
    pause
    exit /b 1
)

echo.
echo 4. 启动前端服务...
if exist start-win.bat (
    call start-win.bat
    echo    [成功] 前端服务已启动
) else (
    echo    [错误] 找不到 start-win.bat 启动脚本
    pause
    exit /b 1
)

echo.
echo ==========================================
echo 前端服务重启完成！
echo ==========================================
echo.
echo 请等待几秒钟，然后访问：
echo http://39.105.227.6:5173/#/production/config
echo.
echo 如果仍然看到错误，请清除浏览器缓存（Ctrl+Shift+R）
echo.
pause

