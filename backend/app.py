#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoCrack - 自动化撞库工具
Flask应用入口文件
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
import sys
import logging
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import Config
from models.database import db, init_db
from api.targets import targets_bp
from api.attacks import attacks_bp
from api.proxies import proxies_bp
from api.data_import import data_import_bp
from core.attack_engine import AttackEngine
from core.proxy_manager import ProxyManager

def create_app():
    """创建Flask应用实例"""
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
    
    return app

def create_socketio_app():
    """创建SocketIO应用"""
    app = create_app()
    socketio = SocketIO(app, cors_allowed_origins=["http://localhost:3000", "http://127.0.0.1:3000"])
    
    @socketio.on('connect')
    def handle_connect():
        print(f'客户端连接: {request.sid}')
        emit('connected', {'data': '连接成功'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        print(f'客户端断开: {request.sid}')
    
    return app, socketio

# 创建应用实例
app, socketio = create_socketio_app()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('autocrack.log'),
        logging.StreamHandler()
    ]
)

@app.route('/')
def index():
    """首页"""
    return {
        'message': 'AutoCrack API Server',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    }

@app.route('/api/health')
def health_check():
    """健康检查"""
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }

if __name__ == '__main__':
    # 初始化数据库
    with app.app_context():
        init_db()
    
    print("=" * 60)
    print("🚀 AutoCrack 自动化撞库工具启动中...")
    print(f"📅 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🌐 API服务地址: http://localhost:5000")
    print("📡 WebSocket地址: ws://localhost:5000")
    print("=" * 60)
    
    # 启动服务器
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=True,
        allow_unsafe_werkzeug=True
    )