#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
攻击结果模型
"""

from datetime import datetime
from models.database import db

class AttackResult(db.Model):
    """攻击结果表"""
    __tablename__ = 'attack_results'
    
    id = db.Column(db.Integer, primary_key=True)
    attack_id = db.Column(db.Integer, db.ForeignKey('attacks.id'), nullable=False, comment='攻击任务ID')
    
    # 凭据信息
    username = db.Column(db.String(200), nullable=False, comment='用户名')
    password = db.Column(db.String(200), nullable=False, comment='密码')
    
    # 结果信息
    is_success = db.Column(db.Boolean, nullable=False, comment='是否成功')
    status_code = db.Column(db.Integer, comment='HTTP状态码')
    response_time = db.Column(db.Float, comment='响应时间(秒)')
    response_size = db.Column(db.Integer, comment='响应大小(字节)')
    
    # 响应内容
    response_headers = db.Column(db.Text, comment='响应头(JSON格式)')
    response_content = db.Column(db.Text, comment='响应内容(部分)')
    error_message = db.Column(db.Text, comment='错误信息')
    
    # 请求信息
    request_url = db.Column(db.String(500), comment='请求URL')
    request_method = db.Column(db.String(20), comment='请求方法')
    proxy_used = db.Column(db.String(200), comment='使用的代理')
    user_agent = db.Column(db.String(500), comment='User-Agent')
    
    # 额外信息
    detection_method = db.Column(db.String(100), comment='检测方法')
    confidence_score = db.Column(db.Float, default=1.0, comment='置信度分数')
    notes = db.Column(db.Text, comment='备注')
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    
    def __repr__(self):
        return f'<AttackResult {self.username}:{self.password} - {"成功" if self.is_success else "失败"}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'attack_id': self.attack_id,
            'username': self.username,
            'password': self.password,
            'is_success': self.is_success,
            'status_code': self.status_code,
            'response_time': self.response_time,
            'response_size': self.response_size,
            'response_headers': self.response_headers,
            'response_content': self.response_content,
            'error_message': self.error_message,
            'request_url': self.request_url,
            'request_method': self.request_method,
            'proxy_used': self.proxy_used,
            'user_agent': self.user_agent,
            'detection_method': self.detection_method,
            'confidence_score': self.confidence_score,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }