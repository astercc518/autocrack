#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据反馈模型
定义攻击结果反馈、性能监控相关的数据模型
"""

import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, Boolean, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship, backref
from models.database import db

class FeedbackType(enum.Enum):
    """反馈类型枚举"""
    SUCCESS = "success"          # 成功反馈
    FAILED = "failed"            # 失败反馈
    ERROR = "error"              # 错误反馈
    WARNING = "warning"          # 警告反馈
    INFO = "info"                # 信息反馈

class FeedbackSource(enum.Enum):
    """反馈来源枚举"""
    ATTACK_ENGINE = "attack_engine"      # 攻击引擎
    PROXY_SYSTEM = "proxy_system"        # 代理系统
    TARGET_CHECKER = "target_checker"    # 目标检查器
    DATA_CLEANER = "data_cleaner"        # 数据清洗器
    TASK_DISTRIBUTOR = "task_distributor" # 任务分配器
    USER_REPORT = "user_report"          # 用户报告

class AttackFeedback(db.Model):
    """攻击反馈模型"""
    __tablename__ = 'attack_feedbacks'
    
    id = Column(Integer, primary_key=True)
    
    # 关联信息
    task_id = Column(Integer, comment='任务ID')  # 暂时移除外键约束
    target_id = Column(Integer, comment='目标ID')  # 暂时移除外键约束
    credential_id = Column(Integer, comment='凭据ID')
    proxy_id = Column(Integer, comment='代理ID')  # 暂时移除外键约束
    
    # 反馈属性
    feedback_type = Column(Enum(FeedbackType), nullable=False, comment='反馈类型')
    source = Column(Enum(FeedbackSource), nullable=False, comment='反馈来源')
    
    # 反馈内容
    title = Column(String(200), comment='反馈标题')
    message = Column(Text, comment='反馈消息')
    details = Column(JSON, comment='详细信息JSON')
    
    # 攻击结果
    is_successful = Column(Boolean, comment='是否成功')
    response_code = Column(Integer, comment='响应状态码')
    response_time = Column(Float, comment='响应时间(秒)')
    response_size = Column(Integer, comment='响应大小(字节)')
    
    # 时间信息
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    
    # 关系
    # target = relationship('Target', backref='attack_feedbacks')  # 暂时注释
    # proxy = relationship('Proxy', backref='attack_feedbacks')  # 暂时注释
    
    def __repr__(self):
        return f'<AttackFeedback {self.feedback_type.value}:{self.title}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'target_id': self.target_id,
            'credential_id': self.credential_id,
            'proxy_id': self.proxy_id,
            'feedback_type': self.feedback_type.value if self.feedback_type else None,
            'source': self.source.value if self.source else None,
            'title': self.title,
            'message': self.message,
            'details': self.details,
            'is_successful': self.is_successful,
            'response_code': self.response_code,
            'response_time': self.response_time,
            'response_size': self.response_size,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'target_name': self.target.name if self.target else None,
            'target_url': self.target.url if self.target else None,
            'proxy_info': f"{self.proxy.host}:{self.proxy.port}" if self.proxy else None
        }

class PerformanceMetric(db.Model):
    """性能指标模型"""
    __tablename__ = 'performance_metrics'
    
    id = Column(Integer, primary_key=True)
    
    # 关联信息
    task_id = Column(Integer, comment='任务ID')  # 暂时移除外键约束
    source = Column(Enum(FeedbackSource), nullable=False, comment='指标来源')
    
    # 指标信息
    metric_name = Column(String(100), nullable=False, comment='指标名称')
    metric_value = Column(Float, nullable=False, comment='指标值')
    metric_unit = Column(String(50), comment='指标单位')
    
    # 时间信息
    timestamp = Column(DateTime, default=datetime.utcnow, comment='时间戳')
    
    # 额外信息
    extra_data = Column(JSON, comment='元数据JSON')
    
    def __repr__(self):
        return f'<PerformanceMetric {self.metric_name}:{self.metric_value}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'source': self.source.value if self.source else None,
            'metric_name': self.metric_name,
            'metric_value': self.metric_value,
            'metric_unit': self.metric_unit,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'extra_data': self.extra_data
        }

class SystemAlert(db.Model):
    """系统告警模型"""
    __tablename__ = 'system_alerts'
    
    id = Column(Integer, primary_key=True)
    
    # 告警属性
    alert_type = Column(Enum(FeedbackType), nullable=False, comment='告警类型')
    source = Column(Enum(FeedbackSource), nullable=False, comment='告警来源')
    severity = Column(String(20), default='medium', comment='严重程度')
    
    # 告警内容
    title = Column(String(200), nullable=False, comment='告警标题')
    description = Column(Text, comment='告警描述')
    details = Column(JSON, comment='告警详情JSON')
    
    # 状态信息
    is_active = Column(Boolean, default=True, comment='是否激活')
    is_acknowledged = Column(Boolean, default=False, comment='是否已确认')
    acknowledged_by = Column(Integer, ForeignKey('users.id'), comment='确认人ID')
    acknowledged_at = Column(DateTime, comment='确认时间')
    
    # 时间信息
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    resolved_at = Column(DateTime, comment='解决时间')
    
    # 关系
    acknowledger = relationship('User', backref='acknowledged_alerts')
    
    def __repr__(self):
        return f'<SystemAlert {self.title}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'alert_type': self.alert_type.value if self.alert_type else None,
            'source': self.source.value if self.source else None,
            'severity': self.severity,
            'title': self.title,
            'description': self.description,
            'details': self.details,
            'is_active': self.is_active,
            'is_acknowledged': self.is_acknowledged,
            'acknowledged_by': self.acknowledged_by,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'acknowledger_name': self.acknowledger.username if self.acknowledger else None
        }
    
    def acknowledge(self, user_id: int):
        """确认告警"""
        self.is_acknowledged = True
        self.acknowledged_by = user_id
        self.acknowledged_at = datetime.utcnow()
    
    def resolve(self):
        """解决告警"""
        self.is_active = False
        self.resolved_at = datetime.utcnow()

class FeedbackSummary(db.Model):
    """反馈汇总模型"""
    __tablename__ = 'feedback_summaries'
    
    id = Column(Integer, primary_key=True)
    
    # 关联信息
    task_id = Column(Integer, ForeignKey('distribution_tasks.id'), comment='任务ID')
    
    # 汇总时间
    summary_date = Column(DateTime, nullable=False, comment='汇总日期')
    summary_type = Column(String(20), default='daily', comment='汇总类型')
    
    # 统计数据
    total_attempts = Column(Integer, default=0, comment='总尝试次数')
    successful_attempts = Column(Integer, default=0, comment='成功次数')
    failed_attempts = Column(Integer, default=0, comment='失败次数')
    error_attempts = Column(Integer, default=0, comment='错误次数')
    
    # 性能数据
    avg_response_time = Column(Float, comment='平均响应时间')
    min_response_time = Column(Float, comment='最小响应时间')
    max_response_time = Column(Float, comment='最大响应时间')
    
    # 代理统计
    proxy_success_rate = Column(Float, comment='代理成功率')
    proxy_failure_rate = Column(Float, comment='代理失败率')
    
    # 目标统计
    target_coverage = Column(Float, comment='目标覆盖率')
    
    # 时间信息
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    
    def __repr__(self):
        return f'<FeedbackSummary {self.summary_date}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'summary_date': self.summary_date.isoformat() if self.summary_date else None,
            'summary_type': self.summary_type,
            'total_attempts': self.total_attempts,
            'successful_attempts': self.successful_attempts,
            'failed_attempts': self.failed_attempts,
            'error_attempts': self.error_attempts,
            'success_rate': (self.successful_attempts / self.total_attempts * 100) if self.total_attempts > 0 else 0,
            'failure_rate': (self.failed_attempts / self.total_attempts * 100) if self.total_attempts > 0 else 0,
            'error_rate': (self.error_attempts / self.total_attempts * 100) if self.total_attempts > 0 else 0,
            'avg_response_time': self.avg_response_time,
            'min_response_time': self.min_response_time,
            'max_response_time': self.max_response_time,
            'proxy_success_rate': self.proxy_success_rate,
            'proxy_failure_rate': self.proxy_failure_rate,
            'target_coverage': self.target_coverage,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def calculate_rates(self):
        """计算各种率"""
        if self.total_attempts > 0:
            self.success_rate = self.successful_attempts / self.total_attempts * 100
            self.failure_rate = self.failed_attempts / self.total_attempts * 100
            self.error_rate = self.error_attempts / self.total_attempts * 100
        else:
            self.success_rate = 0
            self.failure_rate = 0
            self.error_rate = 0