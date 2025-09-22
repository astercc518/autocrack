#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代理服务器模型
"""

from datetime import datetime
from models.database import db

class Proxy(db.Model):
    """代理服务器表"""
    __tablename__ = 'proxies'
    
    id = db.Column(db.Integer, primary_key=True)
    host = db.Column(db.String(255), nullable=False, comment='代理主机')
    port = db.Column(db.Integer, nullable=False, comment='代理端口')
    proxy_type = db.Column(db.String(20), default='http', comment='代理类型: http, https, socks4, socks5')
    
    # 认证信息
    username = db.Column(db.String(100), comment='用户名')
    password = db.Column(db.String(100), comment='密码')
    
    # 状态信息
    status = db.Column(db.String(20), default='active', comment='状态: active, inactive, testing, failed')
    is_working = db.Column(db.Boolean, default=True, comment='是否正常工作')
    last_checked = db.Column(db.DateTime, comment='最后检查时间')
    last_used = db.Column(db.DateTime, comment='最后使用时间')
    
    # 性能统计
    response_time = db.Column(db.Float, default=0.0, comment='响应时间(秒)')
    success_count = db.Column(db.Integer, default=0, comment='成功次数')
    failure_count = db.Column(db.Integer, default=0, comment='失败次数')
    success_rate = db.Column(db.Float, default=0.0, comment='成功率')
    
    # 地理位置信息
    country = db.Column(db.String(100), comment='国家')
    region = db.Column(db.String(100), comment='地区')
    city = db.Column(db.String(100), comment='城市')
    
    # 其他信息
    source = db.Column(db.String(100), comment='代理来源')
    notes = db.Column(db.Text, comment='备注')
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def __repr__(self):
        return f'<Proxy {self.host}:{self.port}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'host': self.host,
            'port': self.port,
            'proxy_type': self.proxy_type,
            'username': self.username,
            'password': self.password,
            'status': self.status,
            'is_working': self.is_working,
            'last_checked': self.last_checked.isoformat() if self.last_checked else None,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'response_time': self.response_time,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'success_rate': self.success_rate,
            'country': self.country,
            'region': self.region,
            'city': self.city,
            'source': self.source,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @property
    def proxy_url(self):
        """获取代理URL"""
        if self.username and self.password:
            return f"{self.proxy_type}://{self.username}:{self.password}@{self.host}:{self.port}"
        else:
            return f"{self.proxy_type}://{self.host}:{self.port}"