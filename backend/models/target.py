#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
目标站点模型
"""

from datetime import datetime
from models.database import db

class Target(db.Model):
    """目标站点表"""
    __tablename__ = 'targets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, comment='目标名称')
    url = db.Column(db.String(500), nullable=False, comment='目标URL')
    login_url = db.Column(db.String(500), comment='登录页面URL')
    method = db.Column(db.String(20), default='POST', comment='请求方法')
    
    # 表单字段配置
    username_field = db.Column(db.String(100), default='username', comment='用户名字段名')
    password_field = db.Column(db.String(100), default='password', comment='密码字段名')
    additional_fields = db.Column(db.Text, comment='额外字段(JSON格式)')
    
    # 成功判断条件
    success_indicators = db.Column(db.Text, comment='成功标识符(JSON数组)')
    failure_indicators = db.Column(db.Text, comment='失败标识符(JSON数组)')
    
    # 请求配置
    headers = db.Column(db.Text, comment='自定义请求头(JSON格式)')
    cookies = db.Column(db.Text, comment='Cookie(JSON格式)')
    timeout = db.Column(db.Integer, default=30, comment='超时时间(秒)')
    
    # 状态信息
    status = db.Column(db.String(20), default='active', comment='状态: active, inactive, testing')
    last_tested = db.Column(db.DateTime, comment='最后测试时间')
    success_rate = db.Column(db.Float, default=0.0, comment='成功率')
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关联关系
    attacks = db.relationship('Attack', backref='target', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Target {self.name}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'login_url': self.login_url,
            'method': self.method,
            'username_field': self.username_field,
            'password_field': self.password_field,
            'additional_fields': self.additional_fields,
            'success_indicators': self.success_indicators,
            'failure_indicators': self.failure_indicators,
            'headers': self.headers,
            'cookies': self.cookies,
            'timeout': self.timeout,
            'status': self.status,
            'last_tested': self.last_tested.isoformat() if self.last_tested else None,
            'success_rate': self.success_rate,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }