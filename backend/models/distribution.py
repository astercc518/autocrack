#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据分配模型
定义任务分配、资源分配相关的数据模型
"""

import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, Boolean, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship, backref
from models.database import db

class TaskStatus(enum.Enum):
    """任务状态枚举"""
    PENDING = "pending"      # 待分配
    ASSIGNED = "assigned"    # 已分配
    RUNNING = "running"      # 执行中
    PAUSED = "paused"        # 暂停
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 失败
    CANCELLED = "cancelled"  # 已取消

class TaskPriority(enum.Enum):
    """任务优先级枚举"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class ResourceType(enum.Enum):
    """资源类型枚举"""
    PROXY = "proxy"          # 代理资源
    TARGET = "target"        # 目标站资源
    CREDENTIAL = "credential" # 凭据资源
    THREAD = "thread"        # 线程资源

class DistributionTask(db.Model):
    """分配任务模型"""
    __tablename__ = 'distribution_tasks'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, comment='任务名称')
    description = Column(Text, comment='任务描述')
    
    # 任务属性
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, comment='任务状态')
    priority = Column(Enum(TaskPriority), default=TaskPriority.NORMAL, comment='任务优先级')
    
    # 分配信息
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False, comment='创建者ID')
    assigned_to = Column(Integer, ForeignKey('users.id'), comment='分配给用户ID')
    assigned_at = Column(DateTime, comment='分配时间')
    
    # 任务配置
    target_count = Column(Integer, default=0, comment='目标数量')
    credential_count = Column(Integer, default=0, comment='凭据数量')
    proxy_count = Column(Integer, default=0, comment='代理数量')
    thread_count = Column(Integer, default=1, comment='线程数量')
    
    # 执行进度
    progress = Column(Float, default=0.0, comment='执行进度')
    processed_count = Column(Integer, default=0, comment='已处理数量')
    success_count = Column(Integer, default=0, comment='成功数量')
    failed_count = Column(Integer, default=0, comment='失败数量')
    
    # 时间信息
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    started_at = Column(DateTime, comment='开始时间')
    completed_at = Column(DateTime, comment='完成时间')
    
    # 配置信息
    config = Column(JSON, comment='任务配置JSON')
    
    # 关系
    creator = relationship('User', foreign_keys=[created_by], backref='created_tasks')
    assignee = relationship('User', foreign_keys=[assigned_to], backref='assigned_tasks')
    allocations = relationship('ResourceAllocation', back_populates='task', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<DistributionTask {self.name}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status.value if self.status else None,
            'priority': self.priority.value if self.priority else None,
            'created_by': self.created_by,
            'assigned_to': self.assigned_to,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'target_count': self.target_count,
            'credential_count': self.credential_count,
            'proxy_count': self.proxy_count,
            'thread_count': self.thread_count,
            'progress': self.progress,
            'processed_count': self.processed_count,
            'success_count': self.success_count,
            'failed_count': self.failed_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'config': self.config,
            'creator_name': self.creator.username if self.creator else None,
            'assignee_name': self.assignee.username if self.assignee else None
        }
    
    def update_progress(self):
        """更新任务进度"""
        total = self.target_count * self.credential_count
        if total > 0:
            self.progress = (self.processed_count / total) * 100
        else:
            self.progress = 0.0
        
        self.updated_at = datetime.utcnow()
    
    def is_completed(self):
        """检查任务是否完成"""
        return self.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
    
    def can_be_assigned(self):
        """检查任务是否可以被分配"""
        return self.status == TaskStatus.PENDING
    
    def can_be_started(self):
        """检查任务是否可以开始执行"""
        return self.status == TaskStatus.ASSIGNED and self.assigned_to is not None

class ResourceAllocation(db.Model):
    """资源分配模型"""
    __tablename__ = 'resource_allocations'
    
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('distribution_tasks.id'), nullable=False, comment='任务ID')
    resource_type = Column(Enum(ResourceType), nullable=False, comment='资源类型')
    resource_id = Column(Integer, nullable=False, comment='资源ID')
    
    # 分配信息
    allocated_count = Column(Integer, default=1, comment='分配数量')
    used_count = Column(Integer, default=0, comment='已使用数量')
    success_count = Column(Integer, default=0, comment='成功数量')
    failed_count = Column(Integer, default=0, comment='失败数量')
    
    # 状态信息
    is_active = Column(Boolean, default=True, comment='是否激活')
    
    # 时间信息
    allocated_at = Column(DateTime, default=datetime.utcnow, comment='分配时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系
    task = relationship('DistributionTask', back_populates='allocations')
    
    def __repr__(self):
        return f'<ResourceAllocation {self.resource_type.value}:{self.resource_id}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'resource_type': self.resource_type.value if self.resource_type else None,
            'resource_id': self.resource_id,
            'allocated_count': self.allocated_count,
            'used_count': self.used_count,
            'success_count': self.success_count,
            'failed_count': self.failed_count,
            'is_active': self.is_active,
            'allocated_at': self.allocated_at.isoformat() if self.allocated_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'usage_rate': (self.used_count / self.allocated_count * 100) if self.allocated_count > 0 else 0,
            'success_rate': (self.success_count / self.used_count * 100) if self.used_count > 0 else 0
        }
    
    def update_usage(self, used_delta=0, success_delta=0, failed_delta=0):
        """更新使用统计"""
        self.used_count += used_delta
        self.success_count += success_delta
        self.failed_count += failed_delta
        self.updated_at = datetime.utcnow()
    
    def is_fully_used(self):
        """检查资源是否已完全使用"""
        return self.used_count >= self.allocated_count

class TaskQueue(db.Model):
    """任务队列模型"""
    __tablename__ = 'task_queues'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False, comment='队列名称')
    description = Column(Text, comment='队列描述')
    
    # 队列配置
    max_concurrent_tasks = Column(Integer, default=5, comment='最大并发任务数')
    max_queue_size = Column(Integer, default=100, comment='最大队列长度')
    
    # 队列状态
    is_active = Column(Boolean, default=True, comment='是否激活')
    current_task_count = Column(Integer, default=0, comment='当前任务数量')
    total_processed = Column(Integer, default=0, comment='总处理数量')
    
    # 时间信息
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def __repr__(self):
        return f'<TaskQueue {self.name}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'max_concurrent_tasks': self.max_concurrent_tasks,
            'max_queue_size': self.max_queue_size,
            'is_active': self.is_active,
            'current_task_count': self.current_task_count,
            'total_processed': self.total_processed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'load_percentage': (self.current_task_count / self.max_concurrent_tasks * 100) if self.max_concurrent_tasks > 0 else 0
        }
    
    def can_accept_task(self):
        """检查队列是否可以接受新任务"""
        return (self.is_active and 
                self.current_task_count < self.max_concurrent_tasks)
    
    def add_task(self):
        """添加任务到队列"""
        if self.can_accept_task():
            self.current_task_count += 1
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def remove_task(self):
        """从队列移除任务"""
        if self.current_task_count > 0:
            self.current_task_count -= 1
            self.total_processed += 1
            self.updated_at = datetime.utcnow()

class DistributionRule(db.Model):
    """分配规则模型"""
    __tablename__ = 'distribution_rules'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, comment='规则名称')
    description = Column(Text, comment='规则描述')
    
    # 规则配置
    rule_type = Column(String(50), nullable=False, comment='规则类型')
    conditions = Column(JSON, comment='规则条件JSON')
    actions = Column(JSON, comment='规则动作JSON')
    
    # 规则状态
    is_active = Column(Boolean, default=True, comment='是否激活')
    priority = Column(Integer, default=0, comment='规则优先级')
    
    # 统计信息
    applied_count = Column(Integer, default=0, comment='应用次数')
    success_count = Column(Integer, default=0, comment='成功次数')
    
    # 时间信息
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False, comment='创建者ID')
    
    # 关系
    creator = relationship('User', backref='distribution_rules')
    
    def __repr__(self):
        return f'<DistributionRule {self.name}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'rule_type': self.rule_type,
            'conditions': self.conditions,
            'actions': self.actions,
            'is_active': self.is_active,
            'priority': self.priority,
            'applied_count': self.applied_count,
            'success_count': self.success_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'creator_name': self.creator.username if self.creator else None,
            'success_rate': (self.success_count / self.applied_count * 100) if self.applied_count > 0 else 0
        }
    
    def apply_rule(self, task):
        """应用规则到任务"""
        self.applied_count += 1
        self.updated_at = datetime.utcnow()
        
        # 这里实现具体的规则逻辑
        # 根据条件和动作来修改任务
        
        return True  # 返回是否成功应用
    
    def check_conditions(self, task):
        """检查规则条件是否满足"""
        if not self.conditions:
            return True
        
        # 实现具体的条件检查逻辑
        # 这里只是示例
        return True