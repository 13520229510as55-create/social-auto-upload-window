@echo off
TITLE 部署 social-auto-upload-window 到 Windows 服务器

echo ==========================================
echo 🚀 开始部署 social-auto-upload-window
echo ==========================================
echo.

set PROJECT_DIR=C:\social-auto-upload-window
set ZIP_FILE=C:\temp\social-auto-upload-window-deploy.zip

REM 1. 检查部署文件
echo [1/5] 检查部署文件...
if not exist "%ZIP_FILE%" (
    echo ❌ 错误: 找不到部署文件 %ZIP_FILE%
    echo 请确保文件已上传到服务器
    pause
    exit /b 1
)

REM 2. 解压文件
echo [2/5] 解压文件到 %PROJECT_DIR%...
if exist "%PROJECT_DIR%" (
    echo    备份现有目录...
    set BACKUP_DIR=%PROJECT_DIR%_backup_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
    set BACKUP_DIR=%BACKUP_DIR: =0%
    move "%PROJECT_DIR%" "%BACKUP_DIR%" >nul 2>&1
)

if not exist "%PROJECT_DIR%" mkdir "%PROJECT_DIR%"

REM 使用 PowerShell 解压（Windows 10+ 自带）
powershell -Command "Expand-Archive -Path '%ZIP_FILE%' -DestinationPath 'C:\temp\extracted' -Force"
xcopy /E /I /Y "C:\temp\extracted\social-auto-upload-window\*" "%PROJECT_DIR%\"
rmdir /S /Q "C:\temp\extracted"

echo ✅ 解压完成
echo.

REM 3. 检查 Python
echo [3/5] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Python
    echo 请先安装 Python 3.10+
    pause
    exit /b 1
)

python --version
echo.

REM 4. 安装 Python 依赖
echo [4/5] 安装 Python 依赖（使用清华源）...
cd /d "%PROJECT_DIR%"
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

echo    安装 Playwright 浏览器...
python -m playwright install chromium

echo ✅ Python 依赖安装完成
echo.

REM 5. 检查 Node.js
echo [5/5] 检查 Node.js 环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  警告: 未找到 Node.js
    echo 前端服务将无法启动，请先安装 Node.js LTS
) else (
    node --version
    
    echo    安装前端依赖...
    cd /d "%PROJECT_DIR%\sau_frontend"
    call npm install --registry https://registry.npmmirror.com
    
    echo ✅ 前端依赖安装完成
)

echo.
echo ==========================================
echo ✅ 部署完成！
echo ==========================================
echo.
echo 📋 启动服务：
echo    方法1: 双击 start-win.bat
echo    方法2: 在项目目录执行:
echo           python sau_backend.py
echo           (新窗口) cd sau_frontend ^&^& npm run dev -- --host 0.0.0.0
echo.
echo 🌐 访问地址：
echo    前端: http://localhost:5173
echo    后端: http://localhost:5409
echo.
pause

