#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
反馈管理器
负责收集、处理和分析攻击结果反馈数据
"""

import logging
import threading
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict, deque
from models.database import db
from models.feedback import (
    AttackFeedback, PerformanceMetric, SystemAlert, FeedbackSummary,
    FeedbackType, FeedbackSource
)

logger = logging.getLogger(__name__)

class FeedbackCollector:
    """反馈收集器"""
    
    def __init__(self, max_buffer_size: int = 1000):
        self.lock = threading.Lock()
        self.feedback_buffer = deque(maxlen=max_buffer_size)
        self.metrics_buffer = deque(maxlen=max_buffer_size)
        self.alert_buffer = deque(maxlen=100)
        
        # 统计数据
        self.stats = {
            'total_feedbacks': 0,
            'success_count': 0,
            'failed_count': 0,
            'error_count': 0,
            'avg_response_time': 0.0
        }
    
    def collect_attack_feedback(self, 
                              task_id: int,
                              target_id: int,
                              credential_id: int,
                              proxy_id: Optional[int],
                              feedback_type: FeedbackType,
                              title: str,
                              message: str,
                              details: Optional[Dict[str, Any]] = None,
                              is_successful: Optional[bool] = None,
                              response_code: Optional[int] = None,
                              response_time: Optional[float] = None,
                              response_size: Optional[int] = None) -> bool:
        """收集攻击反馈"""
        try:
            feedback = AttackFeedback(
                task_id=task_id,
                target_id=target_id,
                credential_id=credential_id,
                proxy_id=proxy_id,
                feedback_type=feedback_type,
                source=FeedbackSource.ATTACK_ENGINE,
                title=title,
                message=message,
                details=details or {},
                is_successful=is_successful,
                response_code=response_code,
                response_time=response_time,
                response_size=response_size
            )
            
            # 添加到缓冲区
            with self.lock:
                self.feedback_buffer.append(feedback)
                self._update_stats(feedback)
            
            # 检查是否需要产生告警
            self._check_alert_conditions(feedback)
            
            logger.debug(f"收集攻击反馈: {title} ({feedback_type.value})")
            return True
            
        except Exception as e:
            logger.error(f"收集攻击反馈失败: {str(e)}")
            return False
    
    def collect_performance_metric(self,
                                 task_id: int,
                                 source: FeedbackSource,
                                 metric_name: str,
                                 metric_value: float,
                                 metric_unit: Optional[str] = None,
                                 extra_data: Optional[Dict[str, Any]] = None) -> bool:
        """收集性能指标"""
        try:
            metric = PerformanceMetric(
                task_id=task_id,
                source=source,
                metric_name=metric_name,
                metric_value=metric_value,
                metric_unit=metric_unit,
                extra_data=extra_data or {}
            )
            
            # 添加到缓冲区
            with self.lock:
                self.metrics_buffer.append(metric)
            
            logger.debug(f"收集性能指标: {metric_name} = {metric_value}")
            return True
            
        except Exception as e:
            logger.error(f"收集性能指标失败: {str(e)}")
            return False
    
    def create_alert(self,
                    alert_type: FeedbackType,
                    source: FeedbackSource,
                    title: str,
                    description: str,
                    severity: str = 'medium',
                    details: Optional[Dict[str, Any]] = None) -> bool:
        """创建系统告警"""
        try:
            alert = SystemAlert(
                alert_type=alert_type,
                source=source,
                severity=severity,
                title=title,
                description=description,
                details=details or {}
            )
            
            # 添加到缓冲区
            with self.lock:
                self.alert_buffer.append(alert)
            
            logger.warning(f"创建系统告警: {title} ({severity})")
            return True
            
        except Exception as e:
            logger.error(f"创建系统告警失败: {str(e)}")
            return False
    
    def flush_to_database(self) -> Dict[str, int]:
        """将缓冲区数据刷新到数据库"""
        try:
            with self.lock:
                feedback_count = len(self.feedback_buffer)
                metrics_count = len(self.metrics_buffer)
                alerts_count = len(self.alert_buffer)
                
                # 批量插入反馈数据
                if self.feedback_buffer:
                    feedbacks = list(self.feedback_buffer)
                    self.feedback_buffer.clear()
                    
                    for feedback in feedbacks:
                        db.session.add(feedback)
                
                # 批量插入性能指标
                if self.metrics_buffer:
                    metrics = list(self.metrics_buffer)
                    self.metrics_buffer.clear()
                    
                    for metric in metrics:
                        db.session.add(metric)
                
                # 批量插入告警
                if self.alert_buffer:
                    alerts = list(self.alert_buffer)
                    self.alert_buffer.clear()
                    
                    for alert in alerts:
                        db.session.add(alert)
                
                db.session.commit()
                
                logger.info(f"刷新数据到数据库: 反馈{feedback_count}, 指标{metrics_count}, 告警{alerts_count}")
                
                return {
                    'feedbacks': feedback_count,
                    'metrics': metrics_count,
                    'alerts': alerts_count
                }
                
        except Exception as e:
            db.session.rollback()
            logger.error(f"刷新数据库失败: {str(e)}")
            return {'error': str(e)}
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self.lock:
            return self.stats.copy()
    
    def _update_stats(self, feedback: AttackFeedback):
        """更新统计信息"""
        self.stats['total_feedbacks'] += 1
        
        if feedback.feedback_type == FeedbackType.SUCCESS:
            self.stats['success_count'] += 1
        elif feedback.feedback_type == FeedbackType.FAILED:
            self.stats['failed_count'] += 1
        elif feedback.feedback_type == FeedbackType.ERROR:
            self.stats['error_count'] += 1
        
        # 更新平均响应时间
        if feedback.response_time:
            total_time = self.stats['avg_response_time'] * (self.stats['total_feedbacks'] - 1)
            self.stats['avg_response_time'] = (total_time + feedback.response_time) / self.stats['total_feedbacks']
    
    def _check_alert_conditions(self, feedback: AttackFeedback):
        """检查告警条件"""
        # 检查错误率
        if self.stats['total_feedbacks'] > 100:
            error_rate = self.stats['error_count'] / self.stats['total_feedbacks']
            if error_rate > 0.5:  # 错误率超过50%
                self.create_alert(
                    FeedbackType.ERROR,
                    FeedbackSource.ATTACK_ENGINE,
                    "高错误率告警",
                    f"错误率达到 {error_rate:.1%}",
                    "high",
                    {'error_rate': error_rate, 'total_feedbacks': self.stats['total_feedbacks']}
                )
        
        # 检查响应时间
        if feedback.response_time and feedback.response_time > 30:  # 响应时间超过30秒
            self.create_alert(
                FeedbackType.WARNING,
                FeedbackSource.ATTACK_ENGINE,
                "响应超时告警",
                f"响应时间 {feedback.response_time:.2f}s 超过阈值",
                "medium",
                {'response_time': feedback.response_time, 'target_id': feedback.target_id}
            )

class FeedbackAnalyzer:
    """反馈分析器"""
    
    def __init__(self):
        self.analysis_cache = {}
        self.cache_ttl = 300  # 缓存5分钟
    
    def analyze_task_performance(self, task_id: int) -> Dict[str, Any]:
        """分析任务性能"""
        try:
            # 获取任务反馈数据
            feedbacks = AttackFeedback.query.filter_by(task_id=task_id).all()
            
            if not feedbacks:
                return {'error': '没有找到反馈数据'}
            
            # 基本统计
            total_count = len(feedbacks)
            success_count = sum(1 for f in feedbacks if f.is_successful)
            failed_count = total_count - success_count
            
            # 响应时间统计
            response_times = [f.response_time for f in feedbacks if f.response_time]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            min_response_time = min(response_times) if response_times else 0
            max_response_time = max(response_times) if response_times else 0
            
            # 按目标分组统计
            target_stats = defaultdict(lambda: {'success': 0, 'failed': 0, 'avg_time': 0})
            for feedback in feedbacks:
                target_id = feedback.target_id
                if feedback.is_successful:
                    target_stats[target_id]['success'] += 1
                else:
                    target_stats[target_id]['failed'] += 1
                
                if feedback.response_time:
                    target_stats[target_id]['avg_time'] += feedback.response_time
            
            # 计算平均时间
            for target_id, stats in target_stats.items():
                total_attempts = stats['success'] + stats['failed']
                if total_attempts > 0:
                    stats['avg_time'] /= total_attempts
                    stats['success_rate'] = stats['success'] / total_attempts * 100
            
            analysis = {
                'task_id': task_id,
                'total_attempts': total_count,
                'successful_attempts': success_count,
                'failed_attempts': failed_count,
                'success_rate': (success_count / total_count * 100) if total_count > 0 else 0,
                'avg_response_time': avg_response_time,
                'min_response_time': min_response_time,
                'max_response_time': max_response_time,
                'target_performance': dict(target_stats),
                'analysis_time': datetime.utcnow().isoformat()
            }
            
            logger.info(f"分析任务性能: {task_id} (成功率: {analysis['success_rate']:.1f}%)")
            return analysis
            
        except Exception as e:
            logger.error(f"分析任务性能失败: {str(e)}")
            return {'error': str(e)}
    
    def analyze_proxy_performance(self, proxy_id: int) -> Dict[str, Any]:
        """分析代理性能"""
        try:
            # 获取代理反馈数据
            feedbacks = AttackFeedback.query.filter_by(proxy_id=proxy_id).all()
            
            if not feedbacks:
                return {'error': '没有找到代理反馈数据'}
            
            # 统计分析
            total_count = len(feedbacks)
            success_count = sum(1 for f in feedbacks if f.is_successful)
            
            # 响应时间分析
            response_times = [f.response_time for f in feedbacks if f.response_time]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            # 按时间段分析
            time_performance = self._analyze_time_performance(feedbacks)
            
            analysis = {
                'proxy_id': proxy_id,
                'total_requests': total_count,
                'successful_requests': success_count,
                'failed_requests': total_count - success_count,
                'success_rate': (success_count / total_count * 100) if total_count > 0 else 0,
                'avg_response_time': avg_response_time,
                'time_performance': time_performance,
                'analysis_time': datetime.utcnow().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"分析代理性能失败: {str(e)}")
            return {'error': str(e)}
    
    def generate_daily_summary(self, date: datetime) -> Optional[FeedbackSummary]:
        """生成每日汇总"""
        try:
            start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
            
            # 获取当日反馈数据
            feedbacks = AttackFeedback.query.filter(
                AttackFeedback.created_at >= start_date,
                AttackFeedback.created_at < end_date
            ).all()
            
            if not feedbacks:
                return None
            
            # 统计数据
            total_attempts = len(feedbacks)
            successful_attempts = sum(1 for f in feedbacks if f.is_successful)
            failed_attempts = sum(1 for f in feedbacks if not f.is_successful and f.feedback_type == FeedbackType.FAILED)
            error_attempts = sum(1 for f in feedbacks if f.feedback_type == FeedbackType.ERROR)
            
            # 响应时间统计
            response_times = [f.response_time for f in feedbacks if f.response_time]
            avg_response_time = sum(response_times) / len(response_times) if response_times else None
            min_response_time = min(response_times) if response_times else None
            max_response_time = max(response_times) if response_times else None
            
            # 创建汇总记录
            summary = FeedbackSummary(
                summary_date=start_date,
                summary_type='daily',
                total_attempts=total_attempts,
                successful_attempts=successful_attempts,
                failed_attempts=failed_attempts,
                error_attempts=error_attempts,
                avg_response_time=avg_response_time,
                min_response_time=min_response_time,
                max_response_time=max_response_time
            )
            
            summary.calculate_rates()
            
            db.session.add(summary)
            db.session.commit()
            
            logger.info(f"生成每日汇总: {date.date()} (总计: {total_attempts})")
            return summary
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"生成每日汇总失败: {str(e)}")
            return None
    
    def _analyze_time_performance(self, feedbacks: List[AttackFeedback]) -> Dict[str, Any]:
        """按时间段分析性能"""
        time_buckets = defaultdict(lambda: {'success': 0, 'failed': 0, 'total': 0})
        
        for feedback in feedbacks:
            # 按小时分组
            hour = feedback.created_at.hour
            time_buckets[hour]['total'] += 1
            
            if feedback.is_successful:
                time_buckets[hour]['success'] += 1
            else:
                time_buckets[hour]['failed'] += 1
        
        # 计算成功率
        for hour, stats in time_buckets.items():
            if stats['total'] > 0:
                stats['success_rate'] = stats['success'] / stats['total'] * 100
        
        return dict(time_buckets)


# 全局实例
feedback_collector = FeedbackCollector()
feedback_analyzer = FeedbackAnalyzer()