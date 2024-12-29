#!/bin/bash

# 设置UTF-8编码
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# 设置默认环境为生产环境
ENV_MODE="prod"

# 检查命令行参数
if [ "$1" = "dev" ]; then
    ENV_MODE="dev"
fi

echo "=== 当前运行模式: $ENV_MODE"

# 根据环境设置变量
if [ "$ENV_MODE" = "dev" ]; then
    export FLASK_ENV=development
    export FLASK_DEBUG=1
else
    export FLASK_ENV=production
    export FLASK_DEBUG=0
fi

export FLASK_APP=app.py

echo "=== 正在启动服务器..."

# 确保目录存在并设置权限
if [ ! -d "static" ]; then
    echo "=== 创建static目录..."
    mkdir -p static
fi

if [ ! -d "static/img" ]; then
    echo "=== 创建图片目录..."
    mkdir -p static/img
fi

# 检查目录权限
echo "=== 检查目录权限..."
if ! touch "static/img/test.tmp" 2>/dev/null; then
    echo "=== 警告: 图片目录可能没有写入权限"
    echo "=== 尝试修复权限..."
    chmod -R 755 static
    chmod -R 777 static/img
fi
[ -f "static/img/test.tmp" ] && rm "static/img/test.tmp"

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "=== 错误: 未找到Python，请确保已安装Python 3"
    read -n 1 -s -r -p "按任意键继续..."
    exit 1
fi

# 创建并激活虚拟环境
if [ ! -d ".venv" ]; then
    echo "=== 创建虚拟环境..."
    python3 -m venv .venv
fi

echo "=== 激活虚拟环境..."
source .venv/bin/activate

# 安装依赖到虚拟环境
echo "=== 安装依赖..."
python3 -m pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "=== 错误: 依赖安装失败"
    read -n 1 -s -r -p "按任意键继续..."
    exit 1
fi

echo "=== 清理会话文件..."
if [ -d "flask_session" ]; then
    rm -f flask_session/*
fi

echo "=== 启动..."
echo "=== 正在运行"
echo "=== 按 Ctrl+C 停止"

# 根据环境选择启动方式
if [ "$ENV_MODE" = "dev" ]; then
    # 开发环境使用Flask开发服务器
    python3 -m flask run --host=127.0.0.1 --port=43891
else
    # 生产环境使用waitress
    python3 -c "from waitress import serve; from app import app; serve(app, host='127.0.0.1', port=43891)"
fi

# 如果程序异常退出，等待用户确认
if [ $? -ne 0 ]; then
    echo "=== 错误: 服务器异常退出"
    read -n 1 -s -r -p "按任意键继续..."
    exit 1
fi 