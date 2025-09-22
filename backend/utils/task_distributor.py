#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据分配管理器
负责任务分配、资源调度和负载均衡
"""

import logging
import random
import threading
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from models.database import db
from models.distribution import (
    DistributionTask, ResourceAllocation, TaskQueue, DistributionRule,
    TaskStatus, TaskPriority, ResourceType
)
from models.target import Target
from models.proxy import Proxy

logger = logging.getLogger(__name__)

class TaskDistributor:
    """任务分配器"""
    
    def __init__(self):
        self.lock = threading.Lock()
        self.active_tasks = {}
        self.resource_pools = {
            ResourceType.PROXY: [],
            ResourceType.TARGET: [],
            ResourceType.CREDENTIAL: [],
            ResourceType.THREAD: []
        }
    
    def create_task(self, creator_id: int, task_config: Dict[str, Any]) -> DistributionTask:
        """创建分配任务"""
        try:
            task = DistributionTask(
                name=task_config.get('name'),
                description=task_config.get('description'),
                priority=TaskPriority(task_config.get('priority', 'normal')),
                created_by=creator_id,
                target_count=task_config.get('target_count', 0),
                credential_count=task_config.get('credential_count', 0),
                proxy_count=task_config.get('proxy_count', 0),
                thread_count=task_config.get('thread_count', 1),
                config=task_config
            )
            
            db.session.add(task)
            db.session.commit()
            
            logger.info(f"创建任务: {task.name} (ID: {task.id})")
            return task
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"创建任务失败: {str(e)}")
            raise
    
    def assign_task(self, task_id: int, assignee_id: int) -> bool:
        """分配任务给用户"""
        try:
            task = DistributionTask.query.get(task_id)
            if not task:
                logger.error(f"任务不存在: {task_id}")
                return False
            
            if not task.can_be_assigned():
                logger.error(f"任务不能被分配: {task.name} (状态: {task.status})")
                return False
            
            task.assigned_to = assignee_id
            task.assigned_at = datetime.utcnow()
            task.status = TaskStatus.ASSIGNED
            task.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"任务分配成功: {task.name} -> 用户 {assignee_id}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"任务分配失败: {str(e)}")
            return False
    
    def auto_assign_tasks(self) -> List[int]:
        """自动分配任务"""
        assigned_tasks = []
        
        try:
            # 获取待分配的任务
            pending_tasks = DistributionTask.query.filter_by(
                status=TaskStatus.PENDING
            ).order_by(
                DistributionTask.priority.desc(),
                DistributionTask.created_at.asc()
            ).all()
            
            # 获取可用的用户（这里简化处理）
            # 实际应该根据用户负载、权限等因素来选择
            available_users = self._get_available_users()
            
            for task in pending_tasks:
                if available_users:
                    # 选择负载最小的用户
                    best_user = self._select_best_user(available_users, task)
                    if best_user and self.assign_task(task.id, best_user['id']):
                        assigned_tasks.append(task.id)
                        
                        # 更新用户负载
                        best_user['load'] += 1
            
            logger.info(f"自动分配了 {len(assigned_tasks)} 个任务")
            return assigned_tasks
            
        except Exception as e:
            logger.error(f"自动分配任务失败: {str(e)}")
            return []
    
    def allocate_resources(self, task_id: int) -> bool:
        """为任务分配资源"""
        try:
            task = DistributionTask.query.get(task_id)
            if not task:
                logger.error(f"任务不存在: {task_id}")
                return False
            
            # 分配代理资源
            if task.proxy_count > 0:
                proxies = self._allocate_proxies(task.proxy_count)
                for proxy_id in proxies:
                    allocation = ResourceAllocation(
                        task_id=task.id,
                        resource_type=ResourceType.PROXY,
                        resource_id=proxy_id,
                        allocated_count=1
                    )
                    db.session.add(allocation)
            
            # 分配目标资源
            if task.target_count > 0:
                targets = self._allocate_targets(task.target_count)
                for target_id in targets:
                    allocation = ResourceAllocation(
                        task_id=task.id,
                        resource_type=ResourceType.TARGET, 
                        resource_id=target_id,
                        allocated_count=1
                    )
                    db.session.add(allocation)
            
            # 分配线程资源
            if task.thread_count > 0:
                allocation = ResourceAllocation(
                    task_id=task.id,
                    resource_type=ResourceType.THREAD,
                    resource_id=0,  # 线程资源不需要具体ID
                    allocated_count=task.thread_count
                )
                db.session.add(allocation)
            
            db.session.commit()
            logger.info(f"为任务 {task.name} 分配了资源")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"资源分配失败: {str(e)}")
            return False
    
    def start_task(self, task_id: int) -> bool:
        """启动任务"""
        try:
            task = DistributionTask.query.get(task_id)
            if not task:
                logger.error(f"任务不存在: {task_id}")
                return False
            
            if not task.can_be_started():
                logger.error(f"任务不能启动: {task.name} (状态: {task.status})")
                return False
            
            # 检查资源分配
            if not self._check_resource_availability(task):
                logger.error(f"任务资源不足: {task.name}")
                return False
            
            # 分配资源
            if not self.allocate_resources(task.id):
                logger.error(f"资源分配失败: {task.name}")
                return False
            
            # 更新任务状态
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()
            task.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            # 添加到活跃任务列表
            with self.lock:
                self.active_tasks[task.id] = {
                    'task': task,
                    'start_time': datetime.utcnow(),
                    'last_update': datetime.utcnow()
                }
            
            logger.info(f"任务启动成功: {task.name}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"任务启动失败: {str(e)}")
            return False
    
    def pause_task(self, task_id: int) -> bool:
        """暂停任务"""
        try:
            task = DistributionTask.query.get(task_id)
            if not task:
                logger.error(f"任务不存在: {task_id}")
                return False
            
            if task.status != TaskStatus.RUNNING:
                logger.error(f"任务不在运行状态: {task.name}")
                return False
            
            task.status = TaskStatus.PAUSED
            task.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            # 从活跃任务列表移除
            with self.lock:
                self.active_tasks.pop(task.id, None)
            
            logger.info(f"任务暂停成功: {task.name}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"任务暂停失败: {str(e)}")
            return False
    
    def complete_task(self, task_id: int, success: bool = True) -> bool:
        """完成任务"""
        try:
            task = DistributionTask.query.get(task_id)
            if not task:
                logger.error(f"任务不存在: {task_id}")
                return False
            
            task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
            task.completed_at = datetime.utcnow()
            task.updated_at = datetime.utcnow()
            task.progress = 100.0 if success else task.progress
            
            db.session.commit()
            
            # 释放资源
            self._release_task_resources(task.id)
            
            # 从活跃任务列表移除
            with self.lock:
                self.active_tasks.pop(task.id, None)
            
            logger.info(f"任务完成: {task.name} ({'成功' if success else '失败'})")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"任务完成失败: {str(e)}")
            return False
    
    def update_task_progress(self, task_id: int, processed: int, success: int, failed: int) -> bool:
        """更新任务进度"""
        try:
            task = DistributionTask.query.get(task_id)
            if not task:
                return False
            
            task.processed_count = processed
            task.success_count = success
            task.failed_count = failed
            task.update_progress()
            
            db.session.commit()
            
            # 更新活跃任务记录
            with self.lock:
                if task.id in self.active_tasks:
                    self.active_tasks[task.id]['last_update'] = datetime.utcnow()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新任务进度失败: {str(e)}")
            return False
    
    def get_task_stats(self) -> Dict[str, Any]:
        """获取任务统计信息"""
        try:
            stats = {}
            
            # 按状态统计任务数量
            status_counts = db.session.query(
                DistributionTask.status,
                db.func.count(DistributionTask.id)
            ).group_by(DistributionTask.status).all()
            
            stats['by_status'] = {status.value: count for status, count in status_counts}
            
            # 按优先级统计
            priority_counts = db.session.query(
                DistributionTask.priority,
                db.func.count(DistributionTask.id)
            ).group_by(DistributionTask.priority).all()
            
            stats['by_priority'] = {priority.value: count for priority, count in priority_counts}
            
            # 活跃任务统计
            stats['active_tasks'] = len(self.active_tasks)
            
            # 资源使用统计
            stats['resource_usage'] = self._get_resource_usage_stats()
            
            return stats
            
        except Exception as e:
            logger.error(f"获取任务统计失败: {str(e)}")
            return {}
    
    def _get_available_users(self) -> List[Dict[str, Any]]:
        """获取可用用户列表"""
        # 这里简化处理，实际应该查询数据库
        # 获取有权限执行任务的用户，并计算他们的当前负载
        from models.user import User
        
        users = User.query.filter_by(is_active=True).all()
        available_users = []
        
        for user in users:
            # 计算用户当前负载
            current_load = DistributionTask.query.filter_by(
                assigned_to=user.id,
                status=TaskStatus.RUNNING
            ).count()
            
            available_users.append({
                'id': user.id,
                'username': user.username,
                'load': current_load,
                'max_load': 5  # 假设每个用户最多处理5个任务
            })
        
        # 过滤掉负载已满的用户
        return [user for user in available_users if user['load'] < user['max_load']]
    
    def _select_best_user(self, users: List[Dict[str, Any]], task: DistributionTask) -> Optional[Dict[str, Any]]:
        """选择最适合的用户"""
        if not users:
            return None
        
        # 根据负载选择用户（负载均衡）
        users.sort(key=lambda u: u['load'])
        return users[0]
    
    def _allocate_proxies(self, count: int) -> List[int]:
        """分配代理资源"""
        try:
            # 获取可用的代理
            available_proxies = Proxy.query.filter_by(
                is_active=True,
                status='working'
            ).limit(count).all()
            
            return [proxy.id for proxy in available_proxies]
            
        except Exception as e:
            logger.error(f"分配代理失败: {str(e)}")
            return []
    
    def _allocate_targets(self, count: int) -> List[int]:
        """分配目标资源"""
        try:
            # 获取可用的目标
            available_targets = Target.query.filter_by(
                is_active=True
            ).limit(count).all()
            
            return [target.id for target in available_targets]
            
        except Exception as e:
            logger.error(f"分配目标失败: {str(e)}")
            return []
    
    def _check_resource_availability(self, task: DistributionTask) -> bool:
        """检查资源可用性"""
        try:
            # 检查代理资源
            if task.proxy_count > 0:
                available_proxy_count = Proxy.query.filter_by(
                    is_active=True,
                    status='working'
                ).count()
                
                if available_proxy_count < task.proxy_count:
                    logger.warning(f"代理资源不足: 需要 {task.proxy_count}, 可用 {available_proxy_count}")
                    return False
            
            # 检查目标资源
            if task.target_count > 0:
                available_target_count = Target.query.filter_by(
                    is_active=True
                ).count()
                
                if available_target_count < task.target_count:
                    logger.warning(f"目标资源不足: 需要 {task.target_count}, 可用 {available_target_count}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"检查资源可用性失败: {str(e)}")
            return False
    
    def _release_task_resources(self, task_id: int):
        """释放任务资源"""
        try:
            # 将资源分配标记为非活跃
            ResourceAllocation.query.filter_by(
                task_id=task_id
            ).update({'is_active': False})
            
            db.session.commit()
            logger.info(f"释放任务 {task_id} 的资源")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"释放资源失败: {str(e)}")
    
    def _get_resource_usage_stats(self) -> Dict[str, Any]:
        """获取资源使用统计"""
        try:
            stats = {}
            
            for resource_type in ResourceType:
                # 统计活跃的资源分配
                active_allocations = ResourceAllocation.query.filter_by(
                    resource_type=resource_type,
                    is_active=True
                ).all()
                
                total_allocated = sum(alloc.allocated_count for alloc in active_allocations)
                total_used = sum(alloc.used_count for alloc in active_allocations)
                
                stats[resource_type.value] = {
                    'allocated': total_allocated,
                    'used': total_used,
                    'usage_rate': (total_used / total_allocated * 100) if total_allocated > 0 else 0
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"获取资源使用统计失败: {str(e)}")
            return {}


class LoadBalancer:
    """负载均衡器"""
    
    def __init__(self):
        self.task_queues = {}
        self.load_metrics = defaultdict(dict)
    
    def register_queue(self, queue_name: str, max_concurrent: int = 5):
        """注册任务队列"""
        try:
            queue = TaskQueue.query.filter_by(name=queue_name).first()
            if not queue:
                queue = TaskQueue(
                    name=queue_name,
                    max_concurrent_tasks=max_concurrent
                )
                db.session.add(queue)
                db.session.commit()
            
            self.task_queues[queue_name] = queue
            logger.info(f"注册任务队列: {queue_name}")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"注册队列失败: {str(e)}")
    
    def get_best_queue(self) -> Optional[str]:
        """获取最佳队列"""
        available_queues = [
            name for name, queue in self.task_queues.items()
            if queue.can_accept_task()
        ]
        
        if not available_queues:
            return None
        
        # 选择负载最小的队列
        best_queue = min(available_queues, key=lambda name: self.task_queues[name].current_task_count)
        return best_queue
    
    def balance_load(self) -> Dict[str, Any]:
        """执行负载均衡"""
        try:
            # 获取所有队列的负载情况
            queue_loads = {}
            for name, queue in self.task_queues.items():
                load_percentage = (queue.current_task_count / queue.max_concurrent_tasks * 100) if queue.max_concurrent_tasks > 0 else 0
                queue_loads[name] = {
                    'current': queue.current_task_count,
                    'max': queue.max_concurrent_tasks,
                    'load_percentage': load_percentage
                }
            
            # 找出负载不均衡的情况
            loads = [info['load_percentage'] for info in queue_loads.values()]
            if loads:
                avg_load = sum(loads) / len(loads)
                max_load = max(loads)
                min_load = min(loads)
                
                imbalance = max_load - min_load
                
                result = {
                    'queues': queue_loads,
                    'average_load': avg_load,
                    'max_load': max_load,
                    'min_load': min_load,
                    'imbalance': imbalance,
                    'needs_balancing': imbalance > 30  # 如果负载差异超过30%就需要平衡
                }
                
                logger.info(f"负载均衡检查完成: 平均负载 {avg_load:.1f}%")
                return result
            
            return {'error': '没有可用队列'}
            
        except Exception as e:
            logger.error(f"负载均衡失败: {str(e)}")
            return {'error': str(e)}


# 全局分配器实例
task_distributor = TaskDistributor()
load_balancer = LoadBalancer()