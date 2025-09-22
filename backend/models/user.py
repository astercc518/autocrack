#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户权限管理模型
实现用户、角色、权限的完整管理体系
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from models.database import db
import enum

class UserStatus(enum.Enum):
    """用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive" 
    SUSPENDED = "suspended"
    DELETED = "deleted"

class RoleType(enum.Enum):
    """角色类型枚举"""
    ADMIN = "admin"           # 管理员 - 所有权限
    MANAGER = "manager"       # 管理者 - 数据管理权限
    OPERATOR = "operator"     # 操作员 - 攻击执行权限
    VIEWER = "viewer"         # 查看者 - 只读权限

class Permission(enum.Enum):
    """权限枚举"""
    # 用户管理权限
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    
    # 角色权限管理
    ROLE_MANAGE = "role:manage"
    
    # 目标站点权限
    TARGET_CREATE = "target:create"
    TARGET_READ = "target:read"
    TARGET_UPDATE = "target:update"
    TARGET_DELETE = "target:delete"
    
    # 攻击任务权限
    ATTACK_CREATE = "attack:create"
    ATTACK_READ = "attack:read"
    ATTACK_UPDATE = "attack:update"
    ATTACK_DELETE = "attack:delete"
    ATTACK_EXECUTE = "attack:execute"
    
    # 代理管理权限
    PROXY_CREATE = "proxy:create"
    PROXY_READ = "proxy:read"
    PROXY_UPDATE = "proxy:update"
    PROXY_DELETE = "proxy:delete"
    
    # 数据管理权限
    DATA_IMPORT = "data:import"
    DATA_EXPORT = "data:export"
    DATA_CLEAN = "data:clean"
    DATA_DISTRIBUTE = "data:distribute"
    DATA_FEEDBACK = "data:feedback"
    
    # 系统管理权限
    SYSTEM_CONFIG = "system:config"
    SYSTEM_MONITOR = "system:monitor"
    SYSTEM_LOGS = "system:logs"

# 用户角色关联表
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('assigned_at', db.DateTime, default=datetime.utcnow),
    db.Column('assigned_by', db.Integer, db.ForeignKey('users.id'))
)

# 角色权限关联表
role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('permission', db.String(50), primary_key=True),
    db.Column('granted_at', db.DateTime, default=datetime.utcnow)
)

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # 用户信息
    real_name = db.Column(db.String(100))
    department = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    
    # 状态管理
    status = db.Column(db.Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    is_superuser = db.Column(db.Boolean, default=False)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # 安全相关
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)
    password_changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联关系
    roles = db.relationship('Role', secondary=user_roles, 
                           primaryjoin=id == user_roles.c.user_id,
                           backref='users', lazy='dynamic')
    login_logs = db.relationship('LoginLog', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
        self.password_changed_at = datetime.utcnow()
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def has_permission(self, permission):
        """检查用户权限"""
        if self.is_superuser:
            return True
        
        # 检查用户的所有角色权限
        for role in self.roles.all():
            if role.has_permission(permission):
                return True
        return False
    
    def has_role(self, role_name):
        """检查用户角色"""
        return any(role.name == role_name for role in self.roles.all())
    
    def add_role(self, role):
        """添加角色"""
        if not self.has_role(role.name):
            self.roles.append(role)
    
    def remove_role(self, role):
        """移除角色"""
        if self.has_role(role.name):
            self.roles.remove(role)
    
    def is_active(self):
        """检查账户是否活跃"""
        if self.status != UserStatus.ACTIVE:
            return False
        if self.locked_until and self.locked_until > datetime.utcnow():
            return False
        return True
    
    def lock_account(self, minutes=30):
        """锁定账户"""
        from datetime import timedelta
        self.locked_until = datetime.utcnow() + timedelta(minutes=minutes)
        self.status = UserStatus.SUSPENDED
    
    def unlock_account(self):
        """解锁账户"""
        self.locked_until = None
        self.failed_login_attempts = 0
        self.status = UserStatus.ACTIVE
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'real_name': self.real_name,
            'department': self.department,
            'phone': self.phone,
            'status': self.status.value,
            'is_superuser': self.is_superuser,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'roles': [role.name for role in self.roles.all()]
        }

class Role(db.Model):
    """角色模型"""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 权限列表（存储为JSON字符串）
    permissions = db.Column(db.JSON, default=list)
    
    def has_permission(self, permission):
        """检查角色权限"""
        if isinstance(permission, Permission):
            permission = permission.value
        return permission in (self.permissions or [])
    
    def add_permission(self, permission):
        """添加权限"""
        if isinstance(permission, Permission):
            permission = permission.value
        
        if not self.permissions:
            self.permissions = []
        
        if permission not in self.permissions:
            permissions_list = list(self.permissions)
            permissions_list.append(permission)
            self.permissions = permissions_list
    
    def remove_permission(self, permission):
        """移除权限"""
        if isinstance(permission, Permission):
            permission = permission.value
        
        if self.permissions and permission in self.permissions:
            permissions_list = list(self.permissions)
            permissions_list.remove(permission)
            self.permissions = permissions_list
    
class LoginLog(db.Model):
    """登录日志模型"""
    __tablename__ = 'login_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 登录信息
    ip_address = db.Column(db.String(45))  # 支持IPv6
    user_agent = db.Column(db.Text)
    login_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    logout_time = db.Column(db.DateTime)
    
    # 登录状态
    success = db.Column(db.Boolean, nullable=False)
    failure_reason = db.Column(db.String(100))
    
    # 会话信息
    session_id = db.Column(db.String(100))
    location = db.Column(db.String(200))  # 地理位置
    
    @staticmethod
    def create_log(user_id, ip_address, user_agent, success, failure_reason=None, session_id=None):
        """创建登录日志"""
        log = LoginLog(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            failure_reason=failure_reason,
            session_id=session_id
        )
        db.session.add(log)
        return log
