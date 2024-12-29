import os
import secrets

class Config:
    # 环境配置
    ENV = os.environ.get('FLASK_ENV', 'production')
    DEBUG = ENV == 'development'
    TESTING = False
    
    # 生成随机的密钥
    SECRET_KEY = 'your-secret-key'  # 用于会话加密
    
    # 密码哈希盐值
    SALT = 'YanX'  # 密码加密盐值
    
    # 登录凭证
    ADMIN_USERNAME = 'admin'  # 用户名
    ADMIN_PASSWORD = '123456'  # 密码
    
    # 会话配置
    PERMANENT_SESSION_LIFETIME = 300  # 会话过期时间（秒）
    SESSION_COOKIE_SECURE = ENV != 'development'  # 开发环境下允许HTTP，生产环境强制HTTPS
    SESSION_COOKIE_HTTPONLY = True  # 防止JavaScript访问cookie
    SESSION_COOKIE_SAMESITE = 'Lax'  # 防止CSRF攻击
    SESSION_REFRESH_EACH_REQUEST = True  # 每次请求都刷新会话
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = 'flask_session'
    SESSION_PERMANENT = True
    
    # 请求限制
    LOGIN_RATE_LIMIT = 5  # 登录尝试次数限制
    LOGIN_RATE_LIMIT_PERIOD = 300  # 限制期(秒)
    
    # 文件配置
    DATA_FILE = 'data.json'
    UPLOAD_FOLDER = 'static/img'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'ico', 'icon', 'svg', 'tiff', 'heic', 'heif'}
    MAX_CONTENT_LENGTH = 1000 * 1024 * 1024  # 最大1000MB 