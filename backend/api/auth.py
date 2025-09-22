#!/usr/bin/env python3
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
        
        # 更新登录日志
        # 这里可以根据session_id或其他方式找到对应的登录记录
        # 简化处理，记录登出时间
        
        logger.info(f'用户 {user.username} 登出')
        
        return jsonify({'message': '登出成功'}), 200
        
    except Exception as e:
        logger.error(f'登出处理异常: {str(e)}')
        return jsonify({'error': '登出处理失败'}), 500

@auth_bp.route('/register', methods=['POST'])
@permission_required(Permission.USER_CREATE)
def register():
    """用户注册（需要管理员权限）"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
        
        # 验证必需字段
        required_fields = ['username', 'email', 'password']
        missing_fields = validate_required_fields(data, required_fields)
        if missing_fields:
            return jsonify({'error': f'缺少必需字段: {", ".join(missing_fields)}'}), 400
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        # 验证数据格式
        if not validate_email(email):
            return jsonify({'error': '邮箱格式无效'}), 400
        
        if not validate_password(password):
            return jsonify({'error': '密码强度不足，至少8位包含字母和数字'}), 400
        
        # 检查用户名和邮箱是否已存在
        if User.query.filter_by(username=username).first():
            return jsonify({'error': '用户名已存在'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': '邮箱已被注册'}), 400
        
        # 创建新用户
        new_user = User(
            username=username,
            email=email,
            real_name=data.get('real_name'),
            department=data.get('department'),
            phone=data.get('phone')
        )
        new_user.set_password(password)
        
        # 分配默认角色
        default_role_name = data.get('role', 'viewer')
        default_role = Role.query.filter_by(name=default_role_name).first()
        if default_role:
            new_user.add_role(default_role)
        
        db.session.add(new_user)
        db.session.commit()
        
        logger.info(f'新用户注册成功: {username}')
        
        return jsonify({
            'message': '用户注册成功',
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'用户注册异常: {str(e)}')
        return jsonify({'error': '用户注册失败'}), 500

@auth_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """获取当前用户信息"""
    try:
        user = g.current_user
        return jsonify({
            'user': user.to_dict(),
            'permissions': [p.value for p in Permission if user.has_permission(p)]
        }), 200
        
    except Exception as e:
        logger.error(f'获取用户信息异常: {str(e)}')
        return jsonify({'error': '获取用户信息失败'}), 500

@auth_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """更新当前用户信息"""
    try:
        user = g.current_user
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
        
        # 允许用户更新的字段
        allowed_fields = ['real_name', 'department', 'phone']
        
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        
        # 如果要更新邮箱，需要验证
        if 'email' in data:
            new_email = data['email']
            if not validate_email(new_email):
                return jsonify({'error': '邮箱格式无效'}), 400
            
            # 检查邮箱是否已被其他用户使用
            existing_user = User.query.filter_by(email=new_email).first()
            if existing_user and existing_user.id != user.id:
                return jsonify({'error': '邮箱已被其他用户使用'}), 400
            
            user.email = new_email
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f'用户 {user.username} 更新了个人信息')
        
        return jsonify({
            'message': '个人信息更新成功',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'更新用户信息异常: {str(e)}')
        return jsonify({'error': '更新用户信息失败'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """修改密码"""
    try:
        user = g.current_user
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
        
        required_fields = ['old_password', 'new_password']
        missing_fields = validate_required_fields(data, required_fields)
        if missing_fields:
            return jsonify({'error': f'缺少必需字段: {", ".join(missing_fields)}'}), 400
        
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        # 验证旧密码
        if not user.check_password(old_password):
            return jsonify({'error': '原密码错误'}), 400
        
        # 验证新密码强度
        if not validate_password(new_password):
            return jsonify({'error': '新密码强度不足，至少8位包含字母和数字'}), 400
        
        # 设置新密码
        user.set_password(new_password)
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f'用户 {user.username} 修改了密码')
        
        return jsonify({'message': '密码修改成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'修改密码异常: {str(e)}')
        return jsonify({'error': '修改密码失败'}), 500

# 在LoginLog模型中添加create_log类方法
def create_login_log(user_id, ip_address, user_agent, success, failure_reason=None, session_id=None):
    """创建登录日志"""
    login_log = LoginLog(
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent,
        success=success,
        failure_reason=failure_reason,
        session_id=session_id
    )
    db.session.add(login_log)
    db.session.commit()
    return login_log

# 将create_log方法添加到LoginLog类
LoginLog.create_log = staticmethod(create_login_log)