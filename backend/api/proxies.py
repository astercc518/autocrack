#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代理API接口
"""

from flask import Blueprint, request, jsonify
from models.database import db
from models.proxy import Proxy
from core.proxy_manager import ProxyManager
from utils.validators import validate_ip, validate_port
import threading
from datetime import datetime

proxies_bp = Blueprint('proxies', __name__)
proxy_manager = ProxyManager()

@proxies_bp.route('/', methods=['GET'])
def get_proxies():
    """获取所有代理"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        status = request.args.get('status')
        
        query = Proxy.query
        
        if status:
            query = query.filter_by(status=status)
        
        proxies = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': [proxy.to_dict() for proxy in proxies.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': proxies.total,
                'pages': proxies.pages,
                'has_next': proxies.has_next,
                'has_prev': proxies.has_prev
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@proxies_bp.route('/<int:proxy_id>', methods=['GET'])
def get_proxy(proxy_id):
    """获取单个代理"""
    try:
        proxy = Proxy.query.get_or_404(proxy_id)
        return jsonify({
            'success': True,
            'data': proxy.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@proxies_bp.route('/', methods=['POST'])
def create_proxy():
    """创建新代理"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        if not data.get('host') or not data.get('port'):
            return jsonify({
                'success': False,
                'error': '主机和端口是必需的'
            }), 400
        
        # 验证IP和端口
        if not validate_ip(data['host']) and '.' not in data['host']:
            return jsonify({
                'success': False,
                'error': '无效的主机地址'
            }), 400
        
        if not validate_port(data['port']):
            return jsonify({
                'success': False,
                'error': '无效的端口号'
            }), 400
        
        # 检查代理是否已存在
        existing = Proxy.query.filter_by(
            host=data['host'],
            port=data['port']
        ).first()
        
        if existing:
            return jsonify({
                'success': False,
                'error': '代理已存在'
            }), 400
        
        # 创建代理
        proxy = Proxy(
            host=data['host'],
            port=int(data['port']),
            proxy_type=data.get('proxy_type', 'http'),
            username=data.get('username'),
            password=data.get('password'),
            country=data.get('country'),
            region=data.get('region'),
            city=data.get('city'),
            source=data.get('source'),
            notes=data.get('notes')
        )
        
        db.session.add(proxy)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': proxy.to_dict(),
            'message': '代理创建成功'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@proxies_bp.route('/<int:proxy_id>', methods=['PUT'])
def update_proxy(proxy_id):
    """更新代理"""
    try:
        proxy = Proxy.query.get_or_404(proxy_id)
        data = request.get_json()
        
        # 更新字段
        if 'host' in data:
            proxy.host = data['host']
        if 'port' in data:
            if not validate_port(data['port']):
                return jsonify({
                    'success': False,
                    'error': '无效的端口号'
                }), 400
            proxy.port = int(data['port'])
        if 'proxy_type' in data:
            proxy.proxy_type = data['proxy_type']
        if 'username' in data:
            proxy.username = data['username']
        if 'password' in data:
            proxy.password = data['password']
        if 'status' in data:
            proxy.status = data['status']
        if 'country' in data:
            proxy.country = data['country']
        if 'region' in data:
            proxy.region = data['region']
        if 'city' in data:
            proxy.city = data['city']
        if 'source' in data:
            proxy.source = data['source']
        if 'notes' in data:
            proxy.notes = data['notes']
        
        proxy.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': proxy.to_dict(),
            'message': '代理更新成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@proxies_bp.route('/<int:proxy_id>', methods=['DELETE'])
def delete_proxy(proxy_id):
    """删除代理"""
    try:
        proxy = Proxy.query.get_or_404(proxy_id)
        
        db.session.delete(proxy)
        db.session.commit()
        
        # 从代理管理器中移除
        proxy_manager.remove_proxy(proxy_id)
        
        return jsonify({
            'success': True,
            'message': '代理删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@proxies_bp.route('/batch', methods=['POST'])
def batch_import_proxies():
    """批量导入代理"""
    try:
        data = request.get_json()
        proxies_data = data.get('proxies', [])
        
        if not proxies_data:
            return jsonify({
                'success': False,
                'error': '没有提供代理数据'
            }), 400
        
        added_count = 0
        errors = []
        
        for proxy_data in proxies_data:
            try:
                # 验证数据
                if not proxy_data.get('host') or not proxy_data.get('port'):
                    errors.append(f"主机和端口是必需的: {proxy_data}")
                    continue
                
                # 检查是否已存在
                existing = Proxy.query.filter_by(
                    host=proxy_data['host'],
                    port=proxy_data['port']
                ).first()
                
                if existing:
                    continue
                
                # 创建代理
                proxy = Proxy(
                    host=proxy_data['host'],
                    port=int(proxy_data['port']),
                    proxy_type=proxy_data.get('proxy_type', 'http'),
                    username=proxy_data.get('username'),
                    password=proxy_data.get('password'),
                    country=proxy_data.get('country'),
                    region=proxy_data.get('region'),
                    city=proxy_data.get('city'),
                    source=proxy_data.get('source', 'batch_import')
                )
                
                db.session.add(proxy)
                added_count += 1
                
            except Exception as e:
                errors.append(f"处理代理失败 {proxy_data}: {str(e)}")
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'成功导入 {added_count} 个代理',
            'added_count': added_count,
            'errors': errors
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@proxies_bp.route('/<int:proxy_id>/test', methods=['POST'])
def test_proxy(proxy_id):
    """测试单个代理"""
    try:
        proxy = Proxy.query.get_or_404(proxy_id)
        
        # 在后台线程中测试代理
        def test_in_background():
            proxy_manager.validate_proxy(proxy)
        
        thread = threading.Thread(target=test_in_background)
        thread.start()
        
        return jsonify({
            'success': True,
            'message': '代理测试已启动'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@proxies_bp.route('/test/all', methods=['POST'])
def test_all_proxies():
    """测试所有代理"""
    try:
        # 在后台线程中测试所有代理
        def test_in_background():
            proxy_manager.batch_validate_proxies()
        
        thread = threading.Thread(target=test_in_background)
        thread.start()
        
        return jsonify({
            'success': True,
            'message': '批量代理测试已启动'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@proxies_bp.route('/stats', methods=['GET'])
def get_proxy_stats():
    """获取代理统计信息"""
    try:
        stats = proxy_manager.get_proxy_stats()
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@proxies_bp.route('/refresh', methods=['POST'])
def refresh_proxy_pool():
    """刷新代理池"""
    try:
        proxy_manager.refresh_proxy_pool()
        return jsonify({
            'success': True,
            'message': '代理池已刷新'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500