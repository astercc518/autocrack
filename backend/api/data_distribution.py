#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据分配API
提供任务分配、资源调度相关的RESTful接口
"""

from flask import Blueprint, request, jsonify, current_app, g
import logging
from models.database import db
from models.user import Permission
from models.distribution import DistributionTask, TaskQueue, DistributionRule, TaskStatus, TaskPriority
from api.auth import login_required, permission_required
from utils.task_distributor import task_distributor, load_balancer

logger = logging.getLogger(__name__)

data_distribution_bp = Blueprint('data_distribution', __name__)

@data_distribution_bp.route('/tasks', methods=['POST'])
@login_required
@permission_required(Permission.DATA_DISTRIBUTE)
def create_task():
    """创建分配任务"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
        
        # 验证必需字段
        required_fields = ['name']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'缺少必需字段: {", ".join(missing_fields)}'}), 400
        
        # 创建任务配置
        task_config = {
            'name': data.get('name'),
            'description': data.get('description'),
            'priority': data.get('priority', 'normal'),
            'target_count': data.get('target_count', 0),
            'credential_count': data.get('credential_count', 0),
            'proxy_count': data.get('proxy_count', 0),
            'thread_count': data.get('thread_count', 1),
            'config': data.get('config', {})
        }
        
        # 创建任务
        task = task_distributor.create_task(g.current_user.id, task_config)
        
        logger.info(f'用户 {g.current_user.username} 创建了任务: {task.name}')
        
        return jsonify({
            'success': True,
            'message': '任务创建成功',
            'data': task.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f'创建任务异常: {str(e)}')
        return jsonify({'error': '任务创建失败'}), 500

@data_distribution_bp.route('/tasks', methods=['GET'])
@login_required
@permission_required(Permission.DATA_DISTRIBUTE)
def get_tasks():
    """获取任务列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        priority = request.args.get('priority')
        assigned_to = request.args.get('assigned_to', type=int)
        
        # 构建查询
        query = DistributionTask.query
        
        # 应用过滤条件
        if status:
            try:
                status_enum = TaskStatus(status)
                query = query.filter_by(status=status_enum)
            except ValueError:
                return jsonify({'error': f'无效的状态值: {status}'}), 400
        
        if priority:
            try:
                priority_enum = TaskPriority(priority)
                query = query.filter_by(priority=priority_enum)
            except ValueError:
                return jsonify({'error': f'无效的优先级值: {priority}'}), 400
        
        if assigned_to:
            query = query.filter_by(assigned_to=assigned_to)
        
        # 排序
        query = query.order_by(
            DistributionTask.priority.desc(),
            DistributionTask.created_at.desc()
        )
        
        # 分页
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        tasks = [task.to_dict() for task in pagination.items]
        
        return jsonify({
            'success': True,
            'data': {
                'tasks': tasks,
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
        logger.error(f'获取任务列表异常: {str(e)}')
        return jsonify({'error': '获取任务列表失败'}), 500

@data_distribution_bp.route('/stats', methods=['GET'])
@login_required
@permission_required(Permission.DATA_DISTRIBUTE)
def get_distribution_stats():
    """获取分配统计信息"""
    try:
        stats = task_distributor.get_task_stats()
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        logger.error(f'获取分配统计异常: {str(e)}')
        return jsonify({'error': '获取统计信息失败'}), 500