from flask import Flask, render_template, redirect, url_for, jsonify, request, send_from_directory, session
import json
import os
from datetime import datetime, timedelta
from collections import OrderedDict
from werkzeug.utils import secure_filename
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from config import Config
from security import SecurityHeaders, RateLimiter, hash_password, verify_password, csrf_protect, csrf_token
from flask_session import Session

app = Flask(__name__)
app.config.from_object(Config)

# 初始化Session
Session(app)

# 性能优化配置
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 静态文件缓存1年
app.config['JSON_SORT_KEYS'] = False  # 禁用JSON键排序
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False  # 禁用JSON美化输出

# 应用安全头部中间件
app.wsgi_app = SecurityHeaders(app.wsgi_app)

# 初始化速率限制器
login_limiter = RateLimiter(Config.LOGIN_RATE_LIMIT, Config.LOGIN_RATE_LIMIT_PERIOD)

# 添加全局上下文处理器
@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=csrf_token())

# 检查是否已登录的装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        
        # 检查会话是否过期
        if 'login_time' in session:
            login_time = datetime.fromisoformat(session['login_time'])
            if datetime.now() - login_time > timedelta(seconds=Config.PERMANENT_SESSION_LIFETIME):
                session.clear()  # 清除会话
                return redirect(url_for('login'))
            
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def load_data():
    if os.path.exists(Config.DATA_FILE):
        with open(Config.DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f, object_pairs_hook=OrderedDict)
    return OrderedDict()

def save_data(data):
    with open(Config.DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_first_data(item):
    for key, value in item.items():
        if key != '名称':
            return value
    return None

data = load_data()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        ip = request.remote_addr

        # 检查请求频率
        if not login_limiter.is_allowed(ip):
            return jsonify({'error': '请稍后再试☹️'}), 429

        try:
            # 验证用户名和密码
            if username == Config.ADMIN_USERNAME and verify_password(password, hash_password(Config.ADMIN_PASSWORD, Config.SALT), Config.SALT):
                session.clear()  # 清除旧会话
                session['logged_in'] = True
                session['login_time'] = datetime.now().isoformat()  # 记录登录时间
                session.permanent = True  # 设置为永久会话
                
                # 生成新的CSRF令牌并确保它被保存到会话中
                token = csrf_token()
                session.modified = True
                
                return jsonify({'redirect': url_for('index')})
            else:
                return jsonify({'error': '没有该用户❌️'}), 401
        except Exception as e:
            app.logger.error(f"登录错误: {str(e)}")
            return jsonify({'error': '登录失败，请重试'}), 500

    return render_template('login.html')

# 将需要登录的路由用login_required装饰器保护
@app.route('/')
@login_required
def index():
    # 自动清理未使用的图片
    cleanup_unused_images()
    
    prepared_data = {key: {'名称': value['名称'], '第一个数据': get_first_data(value)} 
                    for key, value in data.items()}
    return render_template('index.html', data=prepared_data)

@app.route('/data/<data_id>')
@login_required
def data_detail(data_id):
    # 自动清理未使用的图片
    cleanup_unused_images()
    
    item = data.get(data_id, {})
    if not item:
        return "Data not found", 404
    return render_template('detail.html', item=item, data_id=data_id)

def cleanup_unused_images():
    """清理未使用的图片"""
    try:
        # 获取data.json中所有使用的图片路径
        used_images = set()
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data.values():
                for value in item.values():
                    if isinstance(value, str) and value.startswith('/static/img/'):
                        used_images.add(value.replace('/static/img/', ''))

        # 获取img文件夹中所有的图片
        img_folder = os.path.join(app.static_folder, 'img')
        if not os.path.exists(img_folder):
            return
            
        existing_images = set(os.listdir(img_folder))

        # 找出未使用的图片
        unused_images = existing_images - used_images

        # 删除未使用的图片
        for image in unused_images:
            try:
                os.remove(os.path.join(img_folder, image))
            except Exception as e:
                app.logger.error(f"删除图片 {image} 失败: {str(e)}")

    except Exception as e:
        app.logger.error(f"清理图片失败: {str(e)}")

@app.route('/api/item/<item_id>', methods=['PUT'])
@login_required
@csrf_protect
def update_item(item_id):
    try:
        if item_id not in data:
            return jsonify({'error': '项目不存在'}), 404
        
        item_data = request.json
        if not item_data.get('名称'):
            return jsonify({'error': '名称是必需的'}), 400

        ordered_data = OrderedDict()
        ordered_data['名称'] = item_data['名称']
        
        original_keys = [k for k in data[item_id].keys() if k != '名称']
        
        for key in original_keys:
            if key in item_data:
                ordered_data[key] = item_data[key]
        
        for key, value in item_data.items():
            if key not in ordered_data:
                ordered_data[key] = value

        data[item_id] = ordered_data
        save_data(data)
        return jsonify({'id': item_id, 'data': ordered_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/item/<data_id>', methods=['DELETE'])
@login_required
@csrf_protect
def delete_item(data_id):
    try:
        if data_id not in data:
            return jsonify({'error': '数据不存在'}), 404
            
        item_data = data[data_id]
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(os.remove, os.path.join(os.path.dirname(__file__), value.lstrip('/'))) 
                       for value in item_data.values() if isinstance(value, str) and value.startswith('/static/img/')]
            for future in futures:
                future.result()
        
        del data[data_id]
        save_data(data)
            
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search')
@login_required
def search():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify(list(data.keys()))
    
    results = {}
    for key, item in data.items():
        for field, value in item.items():
            if str(value).lower().find(query) != -1:
                results[key] = item
                break
    
    return jsonify(results)

@app.route('/api/item', methods=['POST'])
@login_required
@csrf_protect
def create_item():
    try:
        # 检查会话状态
        if 'logged_in' not in session:
            app.logger.warning('会话已过期')
            return jsonify({'error': '会话已过期，请重新登录'}), 401
            
        # 从表单数据中获取JSON字符串并解析
        data_str = request.form.get('data')
        fields_order_str = request.form.get('fieldsOrder')
        
        if not data_str or not fields_order_str:
            app.logger.warning('无效的请求数据')
            return jsonify({'error': '无效的请求数据'}), 400
            
        try:
            item_data = json.loads(data_str)
            fields_order = json.loads(fields_order_str)
        except json.JSONDecodeError:
            app.logger.warning('无效的JSON数据')
            return jsonify({'error': '无效的JSON数据'}), 400
            
        app.logger.info(f'接收到的数据: {item_data}')
            
        if not item_data.get('名称'):
            app.logger.warning('缺少必需的名称字段')
            return jsonify({'error': '名称是必需的'}), 400

        existing_ids = [int(key.split('_')[1]) for key in data.keys()]
        new_id = max(existing_ids) + 1 if existing_ids else 1
        new_key = f'data_{new_id}'

        ordered_data = OrderedDict()
        for field in fields_order:
            if field in item_data:
                ordered_data[field] = item_data[field]

        app.logger.info(f'准备保存的数据: {ordered_data}')
        data[new_key] = ordered_data
        save_data(data)
        app.logger.info(f'数据保存成功: {new_key}')
        return jsonify({'id': new_key, 'data': ordered_data})
    except Exception as e:
        app.logger.error(f"添加数据错误: {str(e)}", exc_info=True)
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500

@app.route('/upload_image', methods=['POST'])
@login_required
@csrf_protect
def upload_image():
    try:
        # 检查会话状态
        if 'logged_in' not in session:
            app.logger.warning('会话已过期')
            return jsonify({'error': '会话已过期，请重新登录'}), 401

        if 'image' not in request.files:
            app.logger.warning('没有文件')
            return jsonify({'error': '没有文件'}), 400
        
        file = request.files['image']
        if file.filename == '':
            app.logger.warning('没有选择文件')
            return jsonify({'error': '没有选择文件'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}.{file.filename.rsplit('.', 1)[1].lower()}")
            
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            try:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                app.logger.info(f'图片上传成功: {filename}')
                return jsonify({'path': f'/static/img/{filename}'})
            except Exception as e:
                app.logger.error(f'保存文件失败: {str(e)}')
                return jsonify({'error': '保存文件失败'}), 500
        
        app.logger.warning('不支持的文件类型')
        return jsonify({'error': '不支持的文件类型'}), 400
    except Exception as e:
        app.logger.error(f'图片上传错误: {str(e)}', exc_info=True)
        return jsonify({'error': str(e)}), 500

# 添加静态文件路由
@app.route('/img/<path:filename>')
@login_required
def serve_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/delete_image', methods=['POST'])
@login_required
@csrf_protect
def delete_image():
    try:
        image_path = request.json.get('path')
        if not image_path:
            return jsonify({'error': '未提供图片路径'}), 400

        full_path = os.path.join(os.path.dirname(__file__), image_path.lstrip('/'))
        
        if os.path.exists(full_path):
            os.remove(full_path)
            return jsonify({'success': True})
        else:
            return jsonify({'error': '文件不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cleanup_images', methods=['POST'])
@login_required
def cleanup_images():
    try:
        # 获取data.json中所有使用的图片路径
        used_images = set()
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data.values():
                for value in item.values():
                    if isinstance(value, str) and value.startswith('/static/img/'):
                        used_images.add(value.replace('/static/img/', ''))

        # 获取img文件夹中所有的图片
        img_folder = os.path.join(app.static_folder, 'img')
        existing_images = set(os.listdir(img_folder))

        # 找出未使用的图片
        unused_images = existing_images - used_images

        # 删除未使用的图片
        deleted_count = 0
        for image in unused_images:
            try:
                os.remove(os.path.join(img_folder, image))
                deleted_count += 1
            except Exception as e:
                print(f"删除图片 {image} 失败: {str(e)}")

        return jsonify({
            'success': True,
            'message': f'成功清理 {deleted_count} 个未使用的图片'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'清理图片失败: {str(e)}'
        }), 500

if __name__ == '__main__':
    # 生成初始管理员密码哈希
    admin_hash = hash_password(Config.ADMIN_PASSWORD, Config.SALT)
    print(f"Admin password hash: {admin_hash}")
    
    # 使用自签名证书启动HTTPS服务器
    app.run(debug=True, port=43891, ssl_context=('cert.pem', 'key.pem'))