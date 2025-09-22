#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字典文件模型
"""

from datetime import datetime
from models.database import db

class Wordlist(db.Model):
    """字典文件表"""
    __tablename__ = 'wordlists'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, comment='字典名称')
    file_path = db.Column(db.String(500), nullable=False, comment='文件路径')
    wordlist_type = db.Column(db.String(50), nullable=False, comment='字典类型: username, password, combo')
    
    # 文件信息
    file_size = db.Column(db.Integer, default=0, comment='文件大小(字节)')
    line_count = db.Column(db.Integer, default=0, comment='行数')
    encoding = db.Column(db.String(20), default='utf-8', comment='文件编码')
    
    # 状态信息
    status = db.Column(db.String(20), default='active', comment='状态: active, inactive, processing')
    is_processed = db.Column(db.Boolean, default=False, comment='是否已处理')
    
    # 统计信息
    usage_count = db.Column(db.Integer, default=0, comment='使用次数')
    success_count = db.Column(db.Integer, default=0, comment='成功次数')
    
    # 描述信息
    description = db.Column(db.Text, comment='描述')
    tags = db.Column(db.String(500), comment='标签(逗号分隔)')
    source = db.Column(db.String(200), comment='来源')
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    last_used = db.Column(db.DateTime, comment='最后使用时间')
    
    def __repr__(self):
        return f'<Wordlist {self.name}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'file_path': self.file_path,
            'wordlist_type': self.wordlist_type,
            'file_size': self.file_size,
            'line_count': self.line_count,
            'encoding': self.encoding,
            'status': self.status,
            'is_processed': self.is_processed,
            'usage_count': self.usage_count,
            'success_count': self.success_count,
            'description': self.description,
            'tags': self.tags,
            'source': self.source,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_used': self.last_used.isoformat() if self.last_used else None
        }