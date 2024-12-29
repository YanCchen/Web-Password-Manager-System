import hashlib
from functools import wraps
from flask import request, Response, session, jsonify
from datetime import datetime, timedelta
import time
from threading import Lock
from collections import deque
import secrets

class RateLimiter:
    def __init__(self, max_requests, period):
        self.max_requests = max_requests
        self.period = period  # 秒
        self.requests = {}  # ip -> deque([(timestamp, count)])
        self.locks = {}     # ip -> Lock()
        self.cleanup_lock = Lock()
        
    def _get_lock(self, ip):
        """获取IP对应的锁"""
        with self.cleanup_lock:
            if ip not in self.locks:
                self.locks[ip] = Lock()
            return self.locks[ip]
    
    def _cleanup(self, now):
        """清理过期的IP记录"""
        with self.cleanup_lock:
            expired_ips = []
            for ip, lock in self.locks.items():
                if ip not in self.requests or not self.requests[ip]:
                    expired_ips.append(ip)
                    
            for ip in expired_ips:
                self.locks.pop(ip, None)
                self.requests.pop(ip, None)
    
    def is_allowed(self, ip):
        now = time.time()
        
        # 定期清理
        if now % 60 < 1:  # 每分钟执行一次清理
            self._cleanup(now)
        
        lock = self._get_lock(ip)
        with lock:
            # 初始化请求队列
            if ip not in self.requests:
                self.requests[ip] = deque(maxlen=self.max_requests)
            
            requests = self.requests[ip]
            
            # 移除过期的请求
            while requests and now - requests[0] >= self.period:
                requests.popleft()
            
            # 检查是否超过限制
            if len(requests) >= self.max_requests:
                return False
            
            # 添加新请求
            requests.append(now)
            return True

def hash_password(password, salt):
    """使用SHA-256和盐值哈希密码"""
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()

def verify_password(password, hashed_password, salt):
    """验证密码是否匹配"""
    return hash_password(password, salt) == hashed_password

class SecurityHeaders:
    """安全头部中间件"""
    def __init__(self, app):
        self.app = app
        self._csp_header = (
            "default-src 'self'; "
            "img-src 'self' data: https://q.qlogo.cn; "
            "style-src 'self' 'unsafe-inline' https://www.xiaoxiaodediyi.xyz; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "font-src 'self' data:; "
            "connect-src 'self'"
        )
        
    def __call__(self, environ, start_response):
        def security_headers(status, headers, exc_info=None):
            headers.extend([
                ('X-Content-Type-Options', 'nosniff'),
                ('X-Frame-Options', 'SAMEORIGIN'),
                ('X-XSS-Protection', '1; mode=block'),
                ('Strict-Transport-Security', 'max-age=31536000; includeSubDomains'),
                ('Content-Security-Policy', self._csp_header),
                ('Referrer-Policy', 'strict-origin-when-cross-origin')
            ])
            return start_response(status, headers, exc_info)
        return self.app(environ, security_headers)

def csrf_token():
    """生成CSRF令牌"""
    if 'csrf_token' not in session:
        session['csrf_token'] = hashlib.sha256(f"{time.time()}{secrets.token_hex(16)}".encode()).hexdigest()
    return session['csrf_token']

def csrf_protect(f):
    """CSRF保护装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == "POST":
            token = session.get('csrf_token')
            if not token:
                return jsonify({'error': 'CSRF令牌缺失'}), 403
            
            # 从不同位置获取CSRF令牌
            request_token = None
            
            # 1. 尝试从表单数据获取
            if request.form:
                request_token = request.form.get('csrf_token')
            
            # 2. 如果不在表单中，尝试从JSON数据获取
            if not request_token and request.is_json:
                request_token = request.json.get('csrf_token')
            
            # 3. 最后尝试从请求头获取
            if not request_token:
                request_token = request.headers.get('X-CSRFToken')
            
            if not request_token:
                return jsonify({'error': '未找到CSRF令牌'}), 403
            
            if token != request_token:
                return jsonify({'error': 'CSRF验证失败'}), 403
                
        return f(*args, **kwargs)
    return decorated_function 