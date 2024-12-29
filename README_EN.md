# Password Manager System | 账号密码管理系统

[English](README_EN.md) | [中文](README.md)

> A secure and elegant local password management system. Let's manage your passwords with style! ✨

---

## 📚 Table of Contents
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Configuration](#️-configuration)
- [User Guide](#-user-guide)
- [Data Management](#-data-management)
- [Development](#️-development)
- [FAQ](#-faq)
- [Changelog](#-changelog)

---

## ⭐ Features

### 🛡️ Security
- CSRF & XSS Protection
- Session Management & Auto Expiry
- Login Rate Limiting
- Password Salt Hashing
- Secure Headers

### 📝 Data Management
- Text & Image Mixed Storage
- Automatic Image Cleanup
- Real-time Data Saving
- JSON Format Storage
- Dynamic Field Management

### 🎨 Interface Design
- Responsive Design, Mobile-friendly
- Real-time Search & Preview
- Smooth Animations
- Intuitive Operation

### 💻 Environment
- Python 3.8+
- Modern Browsers (Chrome/Firefox/Safari/Edge)
- Cross-platform (Windows/Linux/MacOS)

---

## 📥 Quick Start

### 🔧 Basic Configuration

1. **Edit Configuration File** (config.py)
   ```python
   class Config:
       # Password Encryption Salt (Recommended to modify)
       SALT = 'YourSalt'           # Set password encryption salt
       
       # Admin Account (Must modify)
       ADMIN_USERNAME = 'admin'     # Set login username
       ADMIN_PASSWORD = '123456'    # Set login password
       
       # Session Settings (Optional)
       PERMANENT_SESSION_LIFETIME = 300  # Session duration (seconds)
       
       # Supported Image Formats (Optional)
       ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', ...}
       
       # Upload Limits (Optional)
       MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Max 16MB
   ```

### 💻Windows Environment

1. **Prerequisites**
   - Install Python 3.8 or higher
   - Download project code
   - Modify configuration file

2. **Start Service**
   ```bash
   # Double click to run
   start.bat
   ```

### 🐧 Linux/MacOS Environment

1. **Prerequisites**
   - Install Python 3.8 or higher
   - Download project code
   - Modify configuration file

   ```bash
   # 1. Add execute permission
   chmod +x start.sh
   
   # 2. Edit configuration
   vim config.py
   ```

2. **Launch Options**
   ```bash
   # Foreground (Development)
   ./start.sh
   
   # Background (Recommended)
   nohup ./start.sh > app.log 2>&1 &
   ```

3. **Log Management (Background)**
   ```bash
   # Real-time log view
   tail -f app.log
   
   # View complete log
   cat app.log
   ```

4. **Process Management (Background)**
   ```bash
   # View process
   ps aux | grep start.sh
   
   # Stop service
   kill $(ps aux | grep 'start.sh' | awk '{print $2}')
   ```

5. **Access Service**
   > https://127.0.0.1:43891

6. **Auto-start (Linux)**

   > Configure auto-start using systemd:

   #### Step 1: Create Service File
   ```bash
   # Create service configuration file
   sudo vim /etc/systemd/system/password-manager.service
   ```

   #### Step 2: Write Service Configuration
   Remove all comments after configuration

   ```ini
   [Unit]
   Description=Password Manager Service
   After=network.target
   
   [Service]
   Type=simple
   # Replace with your username (e.g., root)
   User=your_username
   # Replace with actual project path
   WorkingDirectory=/path/to/your/project
   # Replace with actual script path
   ExecStart=/bin/bash /path/to/your/project/start.sh
   Restart=always
   RestartSec=10
   Environment=LANG=en_US.UTF-8
   StandardOutput=append:/var/log/password-manager/access.log
   StandardError=append:/var/log/password-manager/error.log
   
   [Install]
   WantedBy=multi-user.target
   ```

   #### Step 3: Create Log Directory
   ```bash
   # Create log directory
   sudo mkdir -p /var/log/password-manager
   # Set directory permissions
   sudo chown -R your_username:your_username /var/log/password-manager
   ```

   #### Step 4: Enable Service
   ```bash
   # Start service immediately
   sudo systemctl start password-manager
   
   # Enable auto-start
   sudo systemctl enable password-manager
   
   # Reload service configuration
   sudo systemctl daemon-reload
   ```

   #### Step 5: Check Service Status
   ```bash
   # View service status
   sudo systemctl status password-manager
   
   # View service logs
   sudo journalctl -u password-manager -f
   ```

   #### Common Management Commands
   ```bash
   # Stop service
   sudo systemctl stop password-manager
   
   # Restart service
   sudo systemctl restart password-manager
   
   # Disable auto-start
   sudo systemctl disable password-manager
   
   # View recent logs (last 100 lines)
   sudo tail -n 100 /var/log/password-manager/access.log
   sudo tail -n 100 /var/log/password-manager/error.log
   
   # Real-time log view
   sudo tail -f /var/log/password-manager/access.log
   ```

   #### Troubleshooting
   ```bash
   # View detailed service status
   sudo systemctl status password-manager -l
   
   # View startup failure reason
   sudo journalctl -u password-manager -n 50 --no-pager
   
   # Check service configuration syntax
   sudo systemd-analyze verify password-manager.service
   ```

---

## ⚙️ Configuration

### Basic Configuration
> Configuration file: config.py
```python
class Config:
    # Admin Account
    ADMIN_USERNAME = 'admin'     # Login username
    ADMIN_PASSWORD = '123456'    # Login password
    
    # Session Settings
    PERMANENT_SESSION_LIFETIME = 7200  # Session duration (seconds)
    
    # Upload Limits
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', ...}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Max 16MB
```

### Port Configuration
> Default port: 43891

1. **Windows Configuration** (start.bat)
   ```batch
   python app.py --port=43891
   ```

2. **Linux Configuration** (start.sh)
   ```bash
   python3 app.py --port=43891
   ```

3. **Program Configuration** (app.py)
   ```python
   app.run(port=43891)
   ```

### Run Modes
- Development: `./start.sh dev` or `start.bat dev`
- Production: Run startup script directly

---

## 📖 User Guide

### ➕ Add Data
1. Click blue plus button in bottom right
2. Fill in name (required)
3. Add more fields
4. Support text/images
5. Save data

### ✏️ Edit Data
1. Click data card
2. Modify content
3. Save changes

### 🗑️ Delete Data
1. Enter details page
2. Click delete
3. Confirm operation

### 🔍 Search Function
- Top search bar
- Real-time search
- Full field matching

---

## 💾 Data Management

### 📄 Text Data
- Storage location: data.json
- Format: JSON
- Auto-save

### 🖼️ Image Data
- Storage location: static/img
- Auto cleanup
- Multiple formats support

---

## 🛠️ Development

### 📁 Directory Structure
```
├── app.py              # Main program
├── config.py           # Configuration file
├── security.py         # Security module
├── requirements.txt    # Dependencies
├── static/            # Static resources
│   └── img/          # Image storage
├── templates/         # Page templates
│   ├── index.html    # Homepage
│   ├── detail.html   # Details page
│   └── login.html    # Login page
├── data.json         # Data file
└── start.{sh,bat}    # Startup scripts
```

### 🔧 Core Modules
- User Authentication (app.py)
- Data Management (app.py)
- Image Processing (app.py)
- Security Middleware (security.py)
- Configuration Management (config.py)

---

## ❓ FAQ

### 🚫 Startup Issues
- Check Python version
- Check dependencies
- Check port availability

### ❌ Upload Issues
- Wait for preview
- Check image format
- Check file size
- Check directory permissions

### ⏰ Session Issues
- Re-login after timeout
- Adjust expiry time

### 🔍 Search Issues
- Check console errors
- Refresh page

---

## 📝 Changelog

### v1.0.0 🎉
- Basic functionality ✨
- Text & image storage 🖼️
- Security implementation 🛡️
- Responsive interface 📱

---

## ⚠️ Security Notice
> Avoid deploying in public networks to prevent potential security risks ❤️

---

## 📄 License
MIT License 🎉 <u></u>