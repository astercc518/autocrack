#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
攻击任务模型
"""

from datetime import datetime
from models.database import db

class Attack(db.Model):
    """攻击任务表"""
    __tablename__ = 'attacks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, comment='任务名称')
    target_id = db.Column(db.Integer, db.ForeignKey('targets.id'), nullable=False, comment='目标ID')
    
    # 攻击配置
    wordlist_type = db.Column(db.String(50), default='combo', comment='字典类型: combo, separate')
    username_list = db.Column(db.Text, comment='用户名列表(文本或文件路径)')
    password_list = db.Column(db.Text, comment='密码列表(文本或文件路径)')
    combo_list = db.Column(db.Text, comment='组合字典(用户名:密码格式)')
    
    # 并发配置
    threads = db.Column(db.Integer, default=10, comment='线程数')
    delay = db.Column(db.Float, default=0.0, comment='请求间隔(秒)')
    timeout = db.Column(db.Integer, default=30, comment='超时时间(秒)')
    
    # 代理配置
    use_proxy = db.Column(db.Boolean, default=False, comment='是否使用代理')
    proxy_rotation = db.Column(db.Boolean, default=True, comment='是否轮换代理')
    
    # 状态信息
    status = db.Column(db.String(20), default='pending', comment='状态: pending, running, completed, failed, stopped')
    progress = db.Column(db.Float, default=0.0, comment='进度百分比')
    total_attempts = db.Column(db.Integer, default=0, comment='总尝试次数')
    successful_attempts = db.Column(db.Integer, default=0, comment='成功次数')
    failed_attempts = db.Column(db.Integer, default=0, comment='失败次数')
    
    # 时间信息
    started_at = db.Column(db.DateTime, comment='开始时间')
    completed_at = db.Column(db.DateTime, comment='完成时间')
    estimated_completion = db.Column(db.DateTime, comment='预计完成时间')
    
    # 结果统计
    success_rate = db.Column(db.Float, default=0.0, comment='成功率')
    average_response_time = db.Column(db.Float, default=0.0, comment='平均响应时间')
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关联关系
    results = db.relationship('AttackResult', backref='attack', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Attack {self.name}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'target_id': self.target_id,
            'wordlist_type': self.wordlist_type,
            'username_list': self.username_list,
            'password_list': self.password_list,
            'combo_list': self.combo_list,
            'threads': self.threads,
            'delay': self.delay,
            'timeout': self.timeout,
            'use_proxy': self.use_proxy,
            'proxy_rotation': self.proxy_rotation,
            'status': self.status,
            'progress': self.progress,
            'total_attempts': self.total_attempts,
            'successful_attempts': self.successful_attempts,
            'failed_attempts': self.failed_attempts,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'estimated_completion': self.estimated_completion.isoformat() if self.estimated_completion else None,
            'success_rate': self.success_rate,
            'average_response_time': self.average_response_time,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }