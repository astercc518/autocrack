# -*- coding: utf-8 -*-
"""
用户认证和权限管理API
提供登录、注册、权限验证等功能
"""

from flask import Blueprint, request, jsonify, session, current_app, g
from functools import wraps
from datetime import datetime, timedelta
import jwt
import logging
from models.database import db
from models.user import User, Role, LoginLog, Permission
from utils.validators import validate_required_fields, validate_email, validate_password

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': '未提供认证令牌'}), 401
        
        try:
            # 移除 'Bearer ' 前缀
            if token.startswith('Bearer '):
                token = token[7:]
            
            payload = jwt.decode(token, current_app.config.get('SECRET_KEY', 'secret'), algorithms=['HS256'])
            user_id = payload.get('user_id')
            
            current_user = User.query.get(user_id)
            if not current_user or not current_user.is_active():
                return jsonify({'error': '用户账户无效或已被禁用'}), 401
            
            # 将当前用户添加到请求上下文
            g.current_user = current_user
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': '认证令牌已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': '无效的认证令牌'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def permission_required(*permissions):
    """权限验证装饰器"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            user = g.current_user
            
            # 检查用户权限
            for permission in permissions:
                if not user.has_permission(permission):
                    return jsonify({
                        'error': f'权限不足，需要权限: {permission.value if hasattr(permission, "value") else permission}'
                    }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
        
        # 验证必需字段
        required_fields = ['username', 'password']
        missing_fields = validate_required_fields(data, required_fields)
        if missing_fields:
            return jsonify({'error': f'缺少必需字段: {", ".join(missing_fields)}'}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        # 查找用户
        user = User.query.filter_by(username=username).first()
        if not user:
            # 记录失败的登录尝试
            LoginLog.create_log(
                user_id=None,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                success=False,
                failure_reason='用户不存在'
            )
            return jsonify({'error': '用户名或密码错误'}), 401
        
        # 检查账户状态
        if not user.is_active():
            LoginLog.create_log(
                user_id=user.id,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                success=False,
                failure_reason='账户被禁用或锁定'
            )
            return jsonify({'error': '账户已被禁用或锁定'}), 401
        
        # 验证密码
        if not user.check_password(password):
            # 增加失败尝试次数
            user.failed_login_attempts += 1
            
            # 如果失败次数过多，锁定账户
            if user.failed_login_attempts >= 5:
                user.lock_account()
                logger.warning(f'用户 {username} 因多次登录失败被锁定')
            
            db.session.commit()
            
            LoginLog.create_log(
                user_id=user.id,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                success=False,
                failure_reason='密码错误'
            )
            
            return jsonify({'error': '用户名或密码错误'}), 401
        
        # 登录成功，重置失败次数
        user.failed_login_attempts = 0
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # 生成JWT令牌
        token_payload = {
            'user_id': user.id,
            'username': user.username,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(
            token_payload, 
            current_app.config.get('SECRET_KEY', 'secret'), 
            algorithm='HS256'
        )
        
        # 记录成功登录
        login_log = LoginLog.create_log(
            user_id=user.id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            success=True
        )
        
        logger.info(f'用户 {username} 登录成功')
        
        return jsonify({
            'message': '登录成功',
            'token': token,
            'user': user.to_dict(),
            'expires_at': token_payload['exp'].isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f'登录处理异常: {str(e)}')
        return jsonify({'error': '登录处理失败'}), 500

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """用户登出"""
    try:
        user = g.current_user
        logger.info(f'用户 {user.username} 登出')
        return jsonify({'message': '登出成功'}), 200
        
    except Exception as e:
        logger.error(f'登出处理异常: {str(e)}')
        return jsonify({'error': '登出处理失败'}), 500

@auth_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """获取用户信息"""
    try:
        user = g.current_user
        return jsonify({
            'success': True,
            'data': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f'获取用户信息异常: {str(e)}')
        return jsonify({'error': '获取用户信息失败'}), 500