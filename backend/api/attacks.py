#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
攻击任务API接口
"""

from flask import Blueprint, request, jsonify
from models.database import db
from models.attack import Attack
from models.target import Target
from models.result import AttackResult
from core.attack_engine import AttackEngine
import json
from datetime import datetime

attacks_bp = Blueprint('attacks', __name__)

@attacks_bp.route('/', methods=['GET'])
def get_attacks():
    """获取所有攻击任务"""
    try:
        attacks = Attack.query.all()
        return jsonify({
            'success': True,
            'data': [attack.to_dict() for attack in attacks],
            'total': len(attacks)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@attacks_bp.route('/<int:attack_id>', methods=['GET'])
def get_attack(attack_id):
    """获取单个攻击任务"""
    try:
        attack = Attack.query.get_or_404(attack_id)
        return jsonify({
            'success': True,
            'data': attack.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@attacks_bp.route('/', methods=['POST'])
def create_attack():
    """创建新的攻击任务"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        if not data.get('name') or not data.get('target_id'):
            return jsonify({
                'success': False,
                'error': '任务名称和目标ID是必需的'
            }), 400
        
        # 验证目标是否存在
        target = Target.query.get(data['target_id'])
        if not target:
            return jsonify({
                'success': False,
                'error': '目标站点不存在'
            }), 400
        
        # 创建攻击任务
        attack = Attack(
            name=data['name'],
            target_id=data['target_id'],
            wordlist_type=data.get('wordlist_type', 'combo'),
            username_list=data.get('username_list', ''),
            password_list=data.get('password_list', ''),
            combo_list=data.get('combo_list', ''),
            threads=min(data.get('threads', 10), 100),  # 限制最大线程数
            delay=data.get('delay', 0.0),
            timeout=data.get('timeout', 30),
            use_proxy=data.get('use_proxy', False),
            proxy_rotation=data.get('proxy_rotation', True)
        )
        
        db.session.add(attack)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': attack.to_dict(),
            'message': '攻击任务创建成功'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@attacks_bp.route('/<int:attack_id>/start', methods=['POST'])
def start_attack(attack_id):
    """启动攻击任务"""
    try:
        attack = Attack.query.get_or_404(attack_id)
        
        if attack.status in ['running']:
            return jsonify({
                'success': False,
                'error': '任务已在运行中'
            }), 400
        
        # 更新任务状态
        attack.status = 'running'
        attack.started_at = datetime.utcnow()
        attack.progress = 0.0
        db.session.commit()
        
        # 启动攻击引擎（异步）
        # 这里应该使用Celery或其他任务队列来异步执行
        # 暂时返回成功状态
        
        return jsonify({
            'success': True,
            'message': '攻击任务已启动',
            'data': attack.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@attacks_bp.route('/<int:attack_id>/stop', methods=['POST'])
def stop_attack(attack_id):
    """停止攻击任务"""
    try:
        attack = Attack.query.get_or_404(attack_id)
        
        if attack.status not in ['running']:
            return jsonify({
                'success': False,
                'error': '任务未在运行中'
            }), 400
        
        # 更新任务状态
        attack.status = 'stopped'
        attack.completed_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '攻击任务已停止',
            'data': attack.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@attacks_bp.route('/<int:attack_id>/results', methods=['GET'])
def get_attack_results(attack_id):
    """获取攻击结果"""
    try:
        attack = Attack.query.get_or_404(attack_id)
        
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        success_only = request.args.get('success_only', 'false').lower() == 'true'
        
        # 构建查询
        query = AttackResult.query.filter_by(attack_id=attack_id)
        
        if success_only:
            query = query.filter_by(is_success=True)
        
        # 分页查询
        results = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': [result.to_dict() for result in results.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': results.total,
                'pages': results.pages,
                'has_next': results.has_next,
                'has_prev': results.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@attacks_bp.route('/<int:attack_id>', methods=['DELETE'])
def delete_attack(attack_id):
    """删除攻击任务"""
    try:
        attack = Attack.query.get_or_404(attack_id)
        
        if attack.status == 'running':
            return jsonify({
                'success': False,
                'error': '无法删除正在运行的任务'
            }), 400
        
        db.session.delete(attack)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '攻击任务删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@attacks_bp.route('/<int:attack_id>/progress', methods=['GET'])
def get_attack_progress(attack_id):
    """获取攻击进度"""
    try:
        attack = Attack.query.get_or_404(attack_id)
        
        progress_data = {
            'attack_id': attack_id,
            'status': attack.status,
            'progress': attack.progress,
            'total_attempts': attack.total_attempts,
            'successful_attempts': attack.successful_attempts,
            'failed_attempts': attack.failed_attempts,
            'success_rate': attack.success_rate,
            'average_response_time': attack.average_response_time,
            'started_at': attack.started_at.isoformat() if attack.started_at else None,
            'estimated_completion': attack.estimated_completion.isoformat() if attack.estimated_completion else None
        }
        
        return jsonify({
            'success': True,
            'data': progress_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500