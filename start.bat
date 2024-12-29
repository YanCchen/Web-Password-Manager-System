@echo off
chcp 65001 > nul

:: 设置Python环境
:: set PYTHON_HOME=D:\python\3.12
:: set PATH=%PYTHON_HOME%;%PYTHON_HOME%\Scripts;%PATH%

:: 设置默认环境为生产环境
set ENV_MODE=prod

:: 检查命令行参数
if "%1"=="dev" (
    set ENV_MODE=dev
)

echo === 当前运行模式: %ENV_MODE%

:: 根据环境设置变量
if "%ENV_MODE%"=="dev" (
    set FLASK_ENV=development
    set FLASK_DEBUG=1
) else (
    set FLASK_ENV=production
    set FLASK_DEBUG=0
)

set FLASK_APP=app.py

echo === 正在启动服务器...

:: 确保目录存在并设置权限
if not exist "static" (
    echo === 创建static目录...
    mkdir static
)

if not exist "static\img" (
    echo === 创建图片目录...
    mkdir static\img
)

:: 检查Python是否安装
python --version > nul 2>&1
if errorlevel 1 (
    echo === 错误: 未找到Python，请确保已安装Python 3
    pause
    exit /b 1
)

:: 创建并激活虚拟环境
if not exist ".venv" (
    echo === 创建虚拟环境...
    python -m venv .venv
)

echo === 激活虚拟环境...
call .venv\Scripts\activate.bat

:: 安装依赖到虚拟环境
echo === 安装依赖...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo === 错误: 依赖安装失败
    pause
    exit /b 1
)

echo === 清理会话文件...
if exist "flask_session" (
    del /F /Q "flask_session\*.*"
)

echo === 启动...
echo === 正在运行
echo === 按 Ctrl+C 停止

:: 根据环境选择启动方式
if "%ENV_MODE%"=="dev" (
    :: 开发环境使用Flask开发服务器
    python -m flask run --host=127.0.0.1 --port=43891
) else (
    :: 生产环境使用waitress
    python -c "from waitress import serve; from app import app; serve(app, host='127.0.0.1', port=43891)"
)

:: 如果程序异常退出，等待用户确认
if errorlevel 1 (
    echo === 错误: 服务器异常退出
    pause
    exit /b 1
) 