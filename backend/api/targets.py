#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
目标站点API接口
"""

from flask import Blueprint, request, jsonify
from models.database import db
from models.target import Target
from utils.validators import validate_url
import json
from datetime import datetime

targets_bp = Blueprint('targets', __name__)

@targets_bp.route('/', methods=['GET'])
def get_targets():
    """获取所有目标站点"""
    try:
        targets = Target.query.all()
        return jsonify({
            'success': True,
            'data': [target.to_dict() for target in targets],
            'total': len(targets)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@targets_bp.route('/<int:target_id>', methods=['GET'])
def get_target(target_id):
    """获取单个目标站点"""
    try:
        target = Target.query.get_or_404(target_id)
        return jsonify({
            'success': True,
            'data': target.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@targets_bp.route('/', methods=['POST'])
def create_target():
    """创建新的目标站点"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        if not data.get('name') or not data.get('url'):
            return jsonify({
                'success': False,
                'error': '名称和URL是必需的'
            }), 400
        
        # 验证URL格式
        if not validate_url(data['url']):
            return jsonify({
                'success': False,
                'error': 'URL格式无效'
            }), 400
        
        # 创建目标站点
        target = Target(
            name=data['name'],
            url=data['url'],
            login_url=data.get('login_url', ''),
            method=data.get('method', 'POST'),
            username_field=data.get('username_field', 'username'),
            password_field=data.get('password_field', 'password'),
            additional_fields=json.dumps(data.get('additional_fields', {})),
            success_indicators=json.dumps(data.get('success_indicators', [])),
            failure_indicators=json.dumps(data.get('failure_indicators', [])),
            headers=json.dumps(data.get('headers', {})),
            cookies=json.dumps(data.get('cookies', {})),
            timeout=data.get('timeout', 30)
        )
        
        db.session.add(target)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': target.to_dict(),
            'message': '目标站点创建成功'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@targets_bp.route('/<int:target_id>', methods=['PUT'])
def update_target(target_id):
    """更新目标站点"""
    try:
        target = Target.query.get_or_404(target_id)
        data = request.get_json()
        
        # 更新字段
        if 'name' in data:
            target.name = data['name']
        if 'url' in data:
            if not validate_url(data['url']):
                return jsonify({
                    'success': False,
                    'error': 'URL格式无效'
                }), 400
            target.url = data['url']
        if 'login_url' in data:
            target.login_url = data['login_url']
        if 'method' in data:
            target.method = data['method']
        if 'username_field' in data:
            target.username_field = data['username_field']
        if 'password_field' in data:
            target.password_field = data['password_field']
        if 'additional_fields' in data:
            target.additional_fields = json.dumps(data['additional_fields'])
        if 'success_indicators' in data:
            target.success_indicators = json.dumps(data['success_indicators'])
        if 'failure_indicators' in data:
            target.failure_indicators = json.dumps(data['failure_indicators'])
        if 'headers' in data:
            target.headers = json.dumps(data['headers'])
        if 'cookies' in data:
            target.cookies = json.dumps(data['cookies'])
        if 'timeout' in data:
            target.timeout = data['timeout']
        if 'status' in data:
            target.status = data['status']
        
        target.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': target.to_dict(),
            'message': '目标站点更新成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@targets_bp.route('/<int:target_id>', methods=['DELETE'])
def delete_target(target_id):
    """删除目标站点"""
    try:
        target = Target.query.get_or_404(target_id)
        
        db.session.delete(target)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '目标站点删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@targets_bp.route('/<int:target_id>/test', methods=['POST'])
def test_target(target_id):
    """测试目标站点连通性"""
    try:
        target = Target.query.get_or_404(target_id)
        
        # 这里可以实现实际的连通性测试逻辑
        # 暂时返回模拟结果
        test_result = {
            'success': True,
            'response_time': 0.5,
            'status_code': 200,
            'is_accessible': True,
            'message': '目标站点可访问'
        }
        
        # 更新最后测试时间
        target.last_tested = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': test_result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500