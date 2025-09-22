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
    
    def update_progress(self):
        """更新任务进度"""
        total = self.target_count * self.credential_count
        if total > 0:
            self.progress = (self.processed_count / total) * 100
        else:
            self.progress = 0.0
        
        self.updated_at = datetime.utcnow()
    
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
    
    def can_accept_task(self):
        """检查队列是否可以接受新任务"""
        return (self.is_active and 
                self.current_task_count < self.max_concurrent_tasks)
