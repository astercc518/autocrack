# -*- coding: utf-8 -*-
"""
AutoCrack - 自动化撞库工具
Flask应用入口文件
"""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
import sys
import logging
import traceback
from datetime import datetime
from functools import wraps

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from config.settings import Config
    from models.database import db, init_db
    from api.targets import targets_bp
    from api.attacks import attacks_bp
    from api.proxies import proxies_bp
    from api.data_import import data_import_bp
    from api.auth import auth_bp
    from api.data_cleaning import data_clean_bp
    from api.data_distribution import data_distribution_bp
    from api.data_feedback import data_feedback_bp
    from core.attack_engine import AttackEngine
    from core.proxy_manager import ProxyManager
except ImportError as e:
    print(f"⚗ 导入模块失败: {e}")
    print("⚠️  请检查项目结构和依赖安装")
    sys.exit(1)

# 配置日志
def setup_logging():
    """配置日志系统"""
    # 创建日志目录
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    # 文件处理器
    file_handler = logging.FileHandler(
        os.path.join(log_dir, 'autocrack.log'),
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return logging.getLogger(__name__)

# 初始化日志
logger = setup_logging()

def handle_errors(f):
    """错误处理装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"请求处理错误: {str(e)}")
            logger.error(f"错误详情: {traceback.format_exc()}")
            return jsonify({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500
    return decorated_function

def create_app():
    """创建 Flask应用实例"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 配置CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # 初始化数据库
    db.init_app(app)
    
    # 注册蓝图
    app.register_blueprint(targets_bp, url_prefix='/api/targets')
    app.register_blueprint(attacks_bp, url_prefix='/api/attacks')
    app.register_blueprint(proxies_bp, url_prefix='/api/proxies')
    app.register_blueprint(data_import_bp, url_prefix='/api/import')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(data_clean_bp, url_prefix='/api/data-clean')
    app.register_blueprint(data_distribution_bp, url_prefix='/api/data-distribution')
    app.register_blueprint(data_feedback_bp, url_prefix='/api/data-feedback')
    
    # 全局错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'API端点未找到',
            'timestamp': datetime.now().isoformat()
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"内部服务器错误: {str(error)}")
        return jsonify({
            'success': False,
            'error': '内部服务器错误',
            'timestamp': datetime.now().isoformat()
        }), 500
    
    return app

def create_socketio_app():
    """创建SocketIO应用"""
    app = create_app()
    socketio = SocketIO(
        app, 
        cors_allowed_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        logger=True,
        engineio_logger=False
    )
    
    @socketio.on('connect')
    def handle_connect():
        logger.info('客户端连接成功')
        emit('connected', {'data': '连接成功', 'timestamp': datetime.now().isoformat()})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        logger.info('客户端断开连接')
    
    @socketio.on_error_default
    def default_error_handler(e):
        logger.error(f'SocketIO错误: {str(e)}')
        logger.error(f'错误详情: {traceback.format_exc()}')
    
    return app, socketio

# 创建应用实例
app, socketio = create_socketio_app()

@app.route('/')
@handle_errors
def index():
    """首页"""
    return {
        'message': 'AutoCrack API Server',
        'version': '1.0.1',
        'status': 'running',
        'features': [
            '用户权限管理',
            '数据清洗',
            '数据分配',
            '数据反馈'
        ],
        'timestamp': datetime.now().isoformat()
    }

@app.route('/api/health')
@handle_errors
def health_check():
    """健康检查"""
    try:
        # 检查数据库连接
        with db.engine.connect() as conn:
            conn.execute(db.text('SELECT 1'))
        db_status = 'healthy'
    except Exception as e:
        logger.warning(f'数据库连接检查失败: {e}')
        db_status = 'unhealthy'
    
    return {
        'status': 'healthy',
        'database': db_status,
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.1'
    }

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)