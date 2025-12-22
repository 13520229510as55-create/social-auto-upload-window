@echo off
TITLE 检查服务器环境配置

echo ==========================================
echo 🔍 检查服务器环境配置
echo ==========================================
echo.

set ALL_OK=1

REM 1. 检查 Python
echo [1/6] 检查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 未安装或未添加到 PATH
    set ALL_OK=0
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo ✅ Python 已安装: %PYTHON_VERSION%
    
    REM 检查 Python 版本是否 >= 3.10
    python -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
    if errorlevel 1 (
        echo ⚠️  警告: Python 版本低于 3.10，建议升级
    ) else (
        echo ✅ Python 版本符合要求 (^>= 3.10)
    )
)
echo.

REM 2. 检查 pip
echo [2/6] 检查 pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip 未安装
    set ALL_OK=0
) else (
    for /f "tokens=2" %%i in ('python -m pip --version 2^>^&1') do set PIP_VERSION=%%i
    echo ✅ pip 已安装: %PIP_VERSION%
)
echo.

REM 3. 检查 Node.js
echo [3/6] 检查 Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js 未安装或未添加到 PATH
    set ALL_OK=0
) else (
    for /f %%i in ('node --version') do set NODE_VERSION=%%i
    echo ✅ Node.js 已安装: %NODE_VERSION%
)
echo.

REM 4. 检查 npm
echo [4/6] 检查 npm...
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm 未安装
    set ALL_OK=0
) else (
    for /f %%i in ('npm --version') do set NPM_VERSION=%%i
    echo ✅ npm 已安装: %NPM_VERSION%
)
echo.

REM 5. 检查端口占用
echo [5/6] 检查端口占用情况...
echo    检查端口 5409 (后端)...
netstat -ano | findstr ":5409" >nul 2>&1
if errorlevel 1 (
    echo ✅ 端口 5409 未被占用
) else (
    echo ⚠️  端口 5409 已被占用
    echo    占用进程:
    netstat -ano | findstr ":5409"
)

echo    检查端口 5173 (前端)...
netstat -ano | findstr ":5173" >nul 2>&1
if errorlevel 1 (
    echo ✅ 端口 5173 未被占用
) else (
    echo ⚠️  端口 5173 已被占用
    echo    占用进程:
    netstat -ano | findstr ":5173"
)
echo.

REM 6. 检查防火墙规则
echo [6/6] 检查防火墙规则...
echo    检查端口 5409 防火墙规则...
netsh advfirewall firewall show rule name=all | findstr /i "5409" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  未找到端口 5409 的防火墙规则
    echo    建议添加规则允许端口 5409
) else (
    echo ✅ 端口 5409 防火墙规则已配置
)

echo    检查端口 5173 防火墙规则...
netsh advfirewall firewall show rule name=all | findstr /i "5173" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  未找到端口 5173 的防火墙规则
    echo    建议添加规则允许端口 5173
) else (
    echo ✅ 端口 5173 防火墙规则已配置
)
echo.

REM 7. 检查项目目录
echo [7/7] 检查项目目录...
if exist "C:\social-auto-upload-window" (
    echo ✅ 项目目录存在: C:\social-auto-upload-window
    
    if exist "C:\social-auto-upload-window\sau_backend.py" (
        echo ✅ 后端文件存在
    ) else (
        echo ⚠️  后端文件不存在，需要部署
    )
    
    if exist "C:\social-auto-upload-window\sau_frontend" (
        echo ✅ 前端目录存在
    ) else (
        echo ⚠️  前端目录不存在，需要部署
    )
) else (
    echo ⚠️  项目目录不存在，需要部署
)
echo.

REM 8. 测试网络连接（可选）
echo [额外] 测试网络连接...
echo    测试访问清华源...
python -m pip install --dry-run flask -i https://pypi.tuna.tsinghua.edu.cn/simple >nul 2>&1
if errorlevel 1 (
    echo ⚠️  无法访问清华源，可能需要配置代理
) else (
    echo ✅ 可以访问清华源
)

echo    测试访问 npm 镜像...
npm config get registry >nul 2>&1
if errorlevel 1 (
    echo ⚠️  npm 配置可能有问题
) else (
    echo ✅ npm 配置正常
)
echo.

REM 总结
echo ==========================================
if %ALL_OK%==1 (
    echo ✅ 环境检查通过！可以开始部署
) else (
    echo ❌ 环境检查未通过，请先解决上述问题
)
echo ==========================================
echo.
echo 📋 下一步操作：
echo    1. 如果环境检查通过，执行: deploy_on_windows.bat
echo    2. 部署完成后，执行: start-win.bat
echo.
pause

