# Password Manager System | 账号密码管理系统

[English](README_EN.md) | [中文](README.md)

> 一个安全、简洁的本地账号密码管理系统，让我们优雅地管理你的密码！ ✨

---

## 📚 目录
- [功能特点](#-功能特点)
- [快速开始](#-快速开始)
- [配置说明](#️-配置说明)
- [使用指南](#-使用指南)
- [数据管理](#-数据管理)
- [开发文档](#️-开发文档)
- [常见问题](#-常见问题)
- [更新日志](#-更新日志)

---

## ⭐ 功能特点

### 🛡️ 安全性
- CSRF 防护 & XSS 防护
- 会话管理和自动过期
- 登录速率限制
- 密码加盐哈希存储
- 安全响应头

### 📝 数据管理
- 文本和图片混合存储
- 自动清理未使用图片
- 数据实时保存
- JSON 格式存储
- 字段动态添加/删除

### 🎨 界面设计
- 响应式设计，完美支持移动端
- 实时搜索 & 即时预览
- 平滑动画效果
- 简洁直观的操作界面

### 💻 运行环境
- Python 3.8+
- 主流浏览器（Chrome/Firefox/Safari/Edge）
- 全平台支持（Windows/Linux/MacOS）

---

## 📥 快速开始

### 🔧 基础配置

1. **修改配置文件** (config.py)
   ```python
   class Config:
       # 密码加密盐值（建议修改）
       SALT = 'YourSalt'           # 设置密码加密盐值
       
       # 管理员账号（必改）
       ADMIN_USERNAME = 'admin'     # 设置登录用户名
       ADMIN_PASSWORD = '123456'    # 设置登录密码
       
       # 会话设置（按需修改）
       PERMANENT_SESSION_LIFETIME = 300  # 会话时长（秒）
       
       # 支持上传的图片格式（按需修改）
       ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', ...}
       
       # 上传限制（按需修改）
       MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 最大16MB
   ```

### 🪟 Windows 环境

1. **环境准备**
   - 安装 Python 3.8 或更高版本
   - 下载本项目代码
   - 修改配置文件

2. **启动服务**
   
   ```bash
   # 直接双击运行
   start.bat
   ```

### 🐧 Linux/MacOS 环境

1. **环境准备**

   - 安装 Python 3.8 或更高版本
   - 下载本项目代码
   - 修改配置文件

   ```bash
   # 1. 添加执行权限
   chmod +x start.sh
   
   # 2. 修改配置文件
   vim config.py
   ```

2. **启动方式**
   ```bash
   # 前台运行（开发调试）
   ./start.sh
   
   # 后台运行（推荐）
   nohup ./start.sh > app.log 2>&1 &
   ```

3. **日志管理（后台运行）**

   ```bash
   # 实时查看日志
   tail -f app.log
   
   # 查看完整日志
   cat app.log
   ```

4. **进程管理（后台运行）**
   ```bash
   # 查看进程
   ps aux | grep start.sh
   
   # 停止服务
   kill $(ps aux | grep 'start.sh' | awk '{print $2}')
   ```

5. **访问服务**

   > https://127.0.0.1:43891

6. **开机自启（Linux）**

   > 使用 systemd 配置开机自启，分为以下步骤：

   #### 第一步：创建服务文件

   ```bash
   # 创建服务配置文件
   sudo vim /etc/systemd/system/password-manager.service
   ```

   #### 第二步：编写服务配置

   配置完后删除全部注释

   ```ini
   [Unit]
   Description=Password Manager Service
   After=network.target
   
   [Service]
   Type=simple
   # 运行用户（替换为你的用户名 如：root）
   User=your_username
   # 工作目录（/path/to/your/project 替换为项目实际路径）
   WorkingDirectory=/path/to/your/project
   # 启动命令（/path/to/your/project/start.sh 替换为项目实际脚本路径）
   ExecStart=/bin/bash /path/to/your/project/start.sh
   Restart=always
   RestartSec=10
   Environment=LANG=en_US.UTF-8
   StandardOutput=append:/var/log/password-manager/access.log
   StandardError=append:/var/log/password-manager/error.log
   
   [Install]
   WantedBy=multi-user.target
   ```
   
   #### 第三步：创建日志目录
   
   ```bash
   # 创建日志目录
   sudo mkdir -p /var/log/password-manager
   # 设置目录权限
   sudo chown -R your_username:your_username /var/log/password-manager
   ```

   #### 第四步：启用服务

   ```bash
   # 立即启动服务
   sudo systemctl start password-manager
   
   # 启用开机自启
   sudo systemctl enable password-manager
   
   # 重载服务配置
   sudo systemctl daemon-reload
   ```
   
   #### 第五步：检查服务状态
   
   ```bash
   # 查看服务状态
   sudo systemctl status password-manager
   
   # 查看服务日志
   sudo journalctl -u password-manager -f
   ```
   
   #### 常用管理命令
   
   ```bash
   # 停止服务
   sudo systemctl stop password-manager
   
   # 重启服务
   sudo systemctl restart password-manager
   
   # 禁用开机自启
   sudo systemctl disable password-manager
   
   # 查看服务日志（最近100行）
   sudo tail -n 100 /var/log/password-manager/access.log
   sudo tail -n 100 /var/log/password-manager/error.log
   
   # 实时查看日志
   sudo tail -f /var/log/password-manager/access.log
   ```
   
   #### 故障排查
   
   ```bash
   # 查看详细服务状态
   sudo systemctl status password-manager -l
   
   # 查看启动失败原因
   sudo journalctl -u password-manager -n 50 --no-pager
   
   # 检查服务配置语法
   sudo systemd-analyze verify password-manager.service
   ```

---

## ⚙️ 配置说明

### 基础配置
> 配置文件：config.py
```python
class Config:
    # 管理员账号
    ADMIN_USERNAME = 'admin'     # 登录用户名
    ADMIN_PASSWORD = '123456'    # 登录密码
    
    # 会话设置
    PERMANENT_SESSION_LIFETIME = 7200  # 会话时长（秒）
    
    # 上传限制
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', ...}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 最大16MB
```

### 端口配置
> 默认端口：43891

1. **Windows 配置** (start.bat)
   ```batch
   python app.py --port=43891
   ```

2. **Linux 配置** (start.sh)
   ```bash
   python3 app.py --port=43891
   ```

3. **程序配置** (app.py)
   ```python
   app.run(port=43891)
   ```

### 运行模式
- 开发模式：`./start.sh dev` 或 `start.bat dev`
- 生产模式：直接运行启动脚本

---

## 📖 使用指南

### ➕ 添加数据
1. 点击右下角蓝色加号
2. 填写名称（必填）
3. 添加更多字段
4. 支持文本/图片
5. 保存数据

### ✏️ 编辑数据
1. 点击数据卡片
2. 修改内容
3. 保存更改

### 🗑️ 删除数据
1. 进入详情页
2. 点击删除
3. 确认操作

### 🔍 搜索功能
- 顶部搜索框
- 实时搜索
- 全字段匹配

---

## 💾 数据管理

### 📄 文本数据
- 存储位置：data.json
- 格式：JSON
- 自动保存

### 🖼️ 图片数据
- 存储位置：static/img
- 自动清理
- 多格式支持

---

## 🛠️ 开发文档

### 📁 目录结构
```
├── app.py              # 主程序
├── config.py           # 配置文件
├── security.py         # 安全模块
├── requirements.txt    # 依赖清单
├── static/            # 静态资源
│   └── img/          # 图片存储
├── templates/         # 页面模板
│   ├── index.html    # 首页
│   ├── detail.html   # 详情页
│   └── login.html    # 登录页
├── data.json         # 数据文件
└── start.{sh,bat}    # 启动脚本
```

### 🔧 核心模块
- 用户认证 (app.py)
- 数据管理 (app.py)
- 图片处理 (app.py)
- 安全中间件 (security.py)
- 配置管理 (config.py)

---

## ❓ 常见问题

### 🚫 启动问题
- 检查 Python 版本
- 检查依赖安装
- 检查端口占用

### ❌ 上传问题
- 等待预览图显示
- 检查图片格式
- 检查文件大小
- 检查目录权限

### ⏰ 会话问题
- 超时重新登录
- 调整过期时间

### 🔍 搜索问题
- 检查控制台错误
- 刷新页面重试

---

## 📝 更新日志

### v1.0.0 🎉
- 基础功能实现 ✨
- 文本图片存储 🖼️
- 安全机制实现 🛡️
- 响应式界面 📱

---

## ⚠️ 安全建议
> 尽量不要在公共网络中部署使用，以免遭到大佬对你的爱 ❤️

---

## 📄 许可证
MIT License 🎉 