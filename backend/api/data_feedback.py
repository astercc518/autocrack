#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据反馈API
提供反馈收集、分析相关的RESTful接口
"""

from flask import Blueprint, request, jsonify, current_app, g
import logging
from datetime import datetime, timedelta
from models.database import db
from models.user import Permission
from models.feedback import AttackFeedback, PerformanceMetric, SystemAlert, FeedbackType, FeedbackSource
from api.auth import login_required, permission_required
from utils.feedback_manager import feedback_collector, feedback_analyzer

logger = logging.getLogger(__name__)

data_feedback_bp = Blueprint('data_feedback', __name__)

@data_feedback_bp.route('/collect/attack', methods=['POST'])
@login_required
@permission_required(Permission.DATA_FEEDBACK)
def collect_attack_feedback():
    """收集攻击反馈"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
        
        # 验证必需字段
        required_fields = ['task_id', 'target_id', 'credential_id', 'feedback_type', 'title', 'message']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'缺少必需字段: {", ".join(missing_fields)}'}), 400
        
        # 验证反馈类型
        try:
            feedback_type = FeedbackType(data['feedback_type'])
        except ValueError:
            return jsonify({'error': f'无效的反馈类型: {data["feedback_type"]}'}), 400
        
        # 收集反馈
        success = feedback_collector.collect_attack_feedback(
            task_id=data['task_id'],
            target_id=data['target_id'],
            credential_id=data['credential_id'],
            proxy_id=data.get('proxy_id'),
            feedback_type=feedback_type,
            title=data['title'],
            message=data['message'],
            details=data.get('details'),
            is_successful=data.get('is_successful'),
            response_code=data.get('response_code'),
            response_time=data.get('response_time'),
            response_size=data.get('response_size')
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': '反馈收集成功'
            }), 200
        else:
            return jsonify({'error': '反馈收集失败'}), 500
        
    except Exception as e:
        logger.error(f'收集攻击反馈异常: {str(e)}')
        return jsonify({'error': '反馈收集失败'}), 500

@data_feedback_bp.route('/collect/metric', methods=['POST'])
@login_required
@permission_required(Permission.DATA_FEEDBACK)
def collect_performance_metric():
    """收集性能指标"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
        
        # 验证必需字段
        required_fields = ['task_id', 'source', 'metric_name', 'metric_value']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'缺少必需字段: {", ".join(missing_fields)}'}), 400
        
        # 验证来源
        try:
            source = FeedbackSource(data['source'])
        except ValueError:
            return jsonify({'error': f'无效的来源: {data["source"]}'}), 400
        
        # 收集指标
        success = feedback_collector.collect_performance_metric(
            task_id=data['task_id'],
            source=source,
            metric_name=data['metric_name'],
            metric_value=data['metric_value'],
            metric_unit=data.get('metric_unit'),
            metadata=data.get('metadata')
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': '性能指标收集成功'
            }), 200
        else:
            return jsonify({'error': '性能指标收集失败'}), 500
        
    except Exception as e:
        logger.error(f'收集性能指标异常: {str(e)}')
        return jsonify({'error': '性能指标收集失败'}), 500

@data_feedback_bp.route('/alerts', methods=['POST'])
@login_required
@permission_required(Permission.DATA_FEEDBACK)
def create_alert():
    """创建系统告警"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
        
        # 验证必需字段
        required_fields = ['alert_type', 'source', 'title', 'description']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'缺少必需字段: {", ".join(missing_fields)}'}), 400
        
        # 验证枚举值
        try:
            alert_type = FeedbackType(data['alert_type'])
            source = FeedbackSource(data['source'])
        except ValueError as e:
            return jsonify({'error': f'无效的枚举值: {str(e)}'}), 400
        
        # 创建告警
        success = feedback_collector.create_alert(
            alert_type=alert_type,
            source=source,
            title=data['title'],
            description=data['description'],
            severity=data.get('severity', 'medium'),
            details=data.get('details')
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': '告警创建成功'
            }), 201
        else:
            return jsonify({'error': '告警创建失败'}), 500
        
    except Exception as e:
        logger.error(f'创建告警异常: {str(e)}')
        return jsonify({'error': '告警创建失败'}), 500

@data_feedback_bp.route('/flush', methods=['POST'])
@login_required
@permission_required(Permission.DATA_FEEDBACK)
def flush_feedback_data():
    """刷新反馈数据到数据库"""
    try:
        result = feedback_collector.flush_to_database()
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 500
        
        return jsonify({
            'success': True,
            'message': '数据刷新成功',
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f'刷新反馈数据异常: {str(e)}')
        return jsonify({'error': '数据刷新失败'}), 500

@data_feedback_bp.route('/stats', methods=['GET'])
@login_required
@permission_required(Permission.DATA_FEEDBACK)
def get_feedback_stats():
    """获取反馈统计信息"""
    try:
        stats = feedback_collector.get_stats()
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        logger.error(f'获取反馈统计异常: {str(e)}')
        return jsonify({'error': '获取统计信息失败'}), 500

@data_feedback_bp.route('/analyze/task/<int:task_id>', methods=['GET'])
@login_required
@permission_required(Permission.DATA_FEEDBACK)
def analyze_task_performance(task_id):
    """分析任务性能"""
    try:
        analysis = feedback_analyzer.analyze_task_performance(task_id)
        
        if 'error' in analysis:
            return jsonify({'error': analysis['error']}), 404
        
        return jsonify({
            'success': True,
            'data': analysis
        }), 200
        
    except Exception as e:
        logger.error(f'分析任务性能异常: {str(e)}')
        return jsonify({'error': '性能分析失败'}), 500

@data_feedback_bp.route('/analyze/proxy/<int:proxy_id>', methods=['GET'])
@login_required
@permission_required(Permission.DATA_FEEDBACK)
def analyze_proxy_performance(proxy_id):
    """分析代理性能"""
    try:
        analysis = feedback_analyzer.analyze_proxy_performance(proxy_id)
        
        if 'error' in analysis:
            return jsonify({'error': analysis['error']}), 404
        
        return jsonify({
            'success': True,
            'data': analysis
        }), 200
        
    except Exception as e:
        logger.error(f'分析代理性能异常: {str(e)}')
        return jsonify({'error': '代理性能分析失败'}), 500

@data_feedback_bp.route('/feedbacks', methods=['GET'])
@login_required
@permission_required(Permission.DATA_FEEDBACK)
def get_feedbacks():
    """获取反馈列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        task_id = request.args.get('task_id', type=int)
        feedback_type = request.args.get('feedback_type')
        target_id = request.args.get('target_id', type=int)
        
        # 构建查询
        query = AttackFeedback.query
        
        # 应用过滤条件
        if task_id:
            query = query.filter_by(task_id=task_id)
        
        if feedback_type:
            try:
                feedback_type_enum = FeedbackType(feedback_type)
                query = query.filter_by(feedback_type=feedback_type_enum)
            except ValueError:
                return jsonify({'error': f'无效的反馈类型: {feedback_type}'}), 400
        
        if target_id:
            query = query.filter_by(target_id=target_id)
        
        # 排序
        query = query.order_by(AttackFeedback.created_at.desc())
        
        # 分页
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        feedbacks = [feedback.to_dict() for feedback in pagination.items]
        
        return jsonify({
            'success': True,
            'data': {
                'feedbacks': feedbacks,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
        }), 200
        
    except Exception as e:
        logger.error(f'获取反馈列表异常: {str(e)}')
        return jsonify({'error': '获取反馈列表失败'}), 500

@data_feedback_bp.route('/alerts', methods=['GET'])
@login_required
@permission_required(Permission.DATA_FEEDBACK)
def get_alerts():
    """获取系统告警"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        is_active = request.args.get('is_active', type=bool)
        severity = request.args.get('severity')
        
        # 构建查询
        query = SystemAlert.query
        
        # 应用过滤条件
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
        
        if severity:
            query = query.filter_by(severity=severity)
        
        # 排序
        query = query.order_by(SystemAlert.created_at.desc())
        
        # 分页
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        alerts = [alert.to_dict() for alert in pagination.items]
        
        return jsonify({
            'success': True,
            'data': {
                'alerts': alerts,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
        }), 200
        
    except Exception as e:
        logger.error(f'获取告警列表异常: {str(e)}')
        return jsonify({'error': '获取告警列表失败'}), 500

@data_feedback_bp.route('/alerts/<int:alert_id>/acknowledge', methods=['POST'])
@login_required
@permission_required(Permission.DATA_FEEDBACK)
def acknowledge_alert(alert_id):
    """确认告警"""
    try:
        alert = SystemAlert.query.get(alert_id)
        if not alert:
            return jsonify({'error': '告警不存在'}), 404
        
        alert.acknowledge(g.current_user.id)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '告警确认成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'确认告警异常: {str(e)}')
        return jsonify({'error': '告警确认失败'}), 500