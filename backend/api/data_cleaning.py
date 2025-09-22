#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据清洗API
提供数据清洗相关的RESTful接口
"""

from flask import Blueprint, request, jsonify, current_app, g
import logging
import json
import tempfile
import os
from models.database import db
from models.user import Permission
from api.auth import login_required, permission_required
from utils.data_cleaner import DataCleaner, DataValidator, clean_csv_data, batch_clean_data

logger = logging.getLogger(__name__)

data_clean_bp = Blueprint('data_clean', __name__)

@data_clean_bp.route('/clean/urls', methods=['POST'])
@login_required
@permission_required(Permission.DATA_CLEAN)
def clean_urls():
    """清洗URL数据"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
        
        urls = data.get('urls', [])
        base_url = data.get('base_url')
        
        if not urls:
            return jsonify({'error': 'URLs列表不能为空'}), 400
        
        if not isinstance(urls, list):
            return jsonify({'error': 'URLs必须是列表格式'}), 400
        
        # 执行清洗
        cleaner = DataCleaner()
        cleaned_urls, stats = cleaner.clean_urls(urls, base_url)
        
        logger.info(f'用户 {g.current_user.username} 清洗了 {len(urls)} 个URL')
        
        return jsonify({
            'success': True,
            'message': 'URL清洗完成',
            'data': {
                'cleaned_urls': cleaned_urls,
                'statistics': stats
            }
        }), 200
        
    except Exception as e:
        logger.error(f'URL清洗异常: {str(e)}')
        return jsonify({'error': 'URL清洗失败'}), 500

@data_clean_bp.route('/clean/credentials', methods=['POST'])
@login_required
@permission_required(Permission.DATA_CLEAN)
def clean_credentials():
    """清洗认证凭据数据"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
        
        credentials = data.get('credentials', [])
        
        if not credentials:
            return jsonify({'error': '凭据列表不能为空'}), 400
        
        if not isinstance(credentials, list):
            return jsonify({'error': '凭据必须是列表格式'}), 400
        
        # 执行清洗
        cleaner = DataCleaner()
        cleaned_credentials, stats = cleaner.clean_credentials(credentials)
        
        logger.info(f'用户 {g.current_user.username} 清洗了 {len(credentials)} 个凭据')
        
        return jsonify({
            'success': True,
            'message': '凭据清洗完成',
            'data': {
                'cleaned_credentials': cleaned_credentials,
                'statistics': stats
            }
        }), 200
        
    except Exception as e:
        logger.error(f'凭据清洗异常: {str(e)}')
        return jsonify({'error': '凭据清洗失败'}), 500

@data_clean_bp.route('/clean/proxies', methods=['POST'])
@login_required
@permission_required(Permission.DATA_CLEAN)
def clean_proxies():
    """清洗代理服务器数据"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
        
        proxies = data.get('proxies', [])
        
        if not proxies:
            return jsonify({'error': '代理列表不能为空'}), 400
        
        if not isinstance(proxies, list):
            return jsonify({'error': '代理必须是列表格式'}), 400
        
        # 执行清洗
        cleaner = DataCleaner()
        cleaned_proxies, stats = cleaner.clean_proxies(proxies)
        
        logger.info(f'用户 {g.current_user.username} 清洗了 {len(proxies)} 个代理')
        
        return jsonify({
            'success': True,
            'message': '代理清洗完成',
            'data': {
                'cleaned_proxies': cleaned_proxies,
                'statistics': stats
            }
        }), 200
        
    except Exception as e:
        logger.error(f'代理清洗异常: {str(e)}')
        return jsonify({'error': '代理清洗失败'}), 500

@data_clean_bp.route('/clean/file', methods=['POST'])
@login_required
@permission_required(Permission.DATA_CLEAN)
def clean_file():
    """清洗上传的文件数据"""
    try:
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({'error': '未找到上传文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '未选择文件'}), 400
        
        # 获取数据类型
        data_type = request.form.get('data_type', 'urls')
        if data_type not in ['urls', 'credentials', 'proxies']:
            return jsonify({'error': '不支持的数据类型'}), 400
        
        # 检查文件扩展名
        if not file.filename or not file.filename.lower().endswith('.csv'):
            return jsonify({'error': '只支持CSV文件格式'}), 400
        
        # 保存临时文件
        with tempfile.NamedTemporaryFile(mode='w+b', suffix='.csv', delete=False) as temp_file:
            file.save(temp_file.name)
            temp_file_path = temp_file.name
        
        try:
            # 清洗文件数据
            cleaned_data, stats = clean_csv_data(temp_file_path, data_type)
            
            logger.info(f'用户 {g.current_user.username} 清洗了文件 {file.filename}')
            
            return jsonify({
                'success': True,
                'message': '文件数据清洗完成',
                'data': {
                    'cleaned_data': cleaned_data,
                    'statistics': stats,
                    'file_name': file.filename,
                    'data_type': data_type
                }
            }), 200
            
        finally:
            # 删除临时文件
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except Exception as e:
        logger.error(f'文件清洗异常: {str(e)}')
        return jsonify({'error': '文件清洗失败'}), 500

@data_clean_bp.route('/validate/target', methods=['POST'])
@login_required
@permission_required(Permission.DATA_CLEAN)
def validate_target():
    """验证目标站数据"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
        
        # 验证数据
        errors = DataValidator.validate_target_data(data)
        
        if errors:
            return jsonify({
                'success': False,
                'message': '数据验证失败',
                'errors': errors
            }), 400
        
        return jsonify({
            'success': True,
            'message': '数据验证通过'
        }), 200
        
    except Exception as e:
        logger.error(f'目标站验证异常: {str(e)}')
        return jsonify({'error': '数据验证失败'}), 500

@data_clean_bp.route('/validate/credential', methods=['POST'])
@login_required
@permission_required(Permission.DATA_CLEAN)
def validate_credential():
    """验证凭据数据"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
        
        # 验证数据
        errors = DataValidator.validate_credential_data(data)
        
        if errors:
            return jsonify({
                'success': False,
                'message': '数据验证失败',
                'errors': errors
            }), 400
        
        return jsonify({
            'success': True,
            'message': '数据验证通过'
        }), 200
        
    except Exception as e:
        logger.error(f'凭据验证异常: {str(e)}')
        return jsonify({'error': '数据验证失败'}), 500

@data_clean_bp.route('/batch/clean', methods=['POST'])
@login_required
@permission_required(Permission.DATA_CLEAN)
def batch_clean():
    """批量清洗数据"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
        
        data_list = data.get('data_list', [])
        data_type = data.get('data_type')
        
        if not data_list:
            return jsonify({'error': '数据列表不能为空'}), 400
        
        if not data_type or data_type not in ['urls', 'credentials', 'proxies']:
            return jsonify({'error': '必须指定有效的数据类型'}), 400
        
        # 执行批量清洗
        cleaned_data, stats = batch_clean_data(data_list, data_type)
        
        logger.info(f'用户 {g.current_user.username} 批量清洗了 {len(data_list)} 条 {data_type} 数据')
        
        return jsonify({
            'success': True,
            'message': '批量数据清洗完成',
            'data': {
                'cleaned_data': cleaned_data,
                'statistics': stats,
                'data_type': data_type
            }
        }), 200
        
    except Exception as e:
        logger.error(f'批量清洗异常: {str(e)}')
        return jsonify({'error': '批量清洗失败'}), 500

@data_clean_bp.route('/stats', methods=['GET'])
@login_required
@permission_required(Permission.DATA_CLEAN)
def get_clean_stats():
    """获取数据清洗统计信息"""
    try:
        # 这里可以从数据库中获取历史清洗统计信息
        # 暂时返回示例数据
        stats = {
            'total_cleaned': 0,
            'urls_cleaned': 0,
            'credentials_cleaned': 0,
            'proxies_cleaned': 0,
            'files_processed': 0,
            'last_clean_time': None
        }
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        logger.error(f'获取清洗统计异常: {str(e)}')
        return jsonify({'error': '获取统计信息失败'}), 500

@data_clean_bp.route('/export/cleaned', methods=['POST'])
@login_required
@permission_required(Permission.DATA_CLEAN)
def export_cleaned_data():
    """导出清洗后的数据"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
        
        cleaned_data = data.get('cleaned_data', [])
        data_type = data.get('data_type', 'urls')
        export_format = data.get('format', 'json')
        
        if not cleaned_data:
            return jsonify({'error': '没有可导出的数据'}), 400
        
        # 根据格式导出数据
        if export_format == 'json':
            result = {
                'data': cleaned_data,
                'type': data_type,
                'count': len(cleaned_data),
                'export_time': logger.info(f'用户 {g.current_user.username} 导出了 {len(cleaned_data)} 条清洗数据')
            }
            
            return jsonify({
                'success': True,
                'message': '数据导出成功',
                'data': result
            }), 200
        
        elif export_format == 'csv':
            # 返回CSV格式的数据（客户端处理下载）
            return jsonify({
                'success': True,
                'message': 'CSV导出准备完成',
                'data': {
                    'csv_data': cleaned_data,
                    'headers': _get_csv_headers(data_type),
                    'filename': f'cleaned_{data_type}_{len(cleaned_data)}.csv'
                }
            }), 200
        
        else:
            return jsonify({'error': '不支持的导出格式'}), 400
        
    except Exception as e:
        logger.error(f'数据导出异常: {str(e)}')
        return jsonify({'error': '数据导出失败'}), 500

def _get_csv_headers(data_type: str) -> list:
    """获取CSV表头"""
    headers_map = {
        'urls': ['url', 'normalized_url'],
        'credentials': ['username', 'password', 'hash'],
        'proxies': ['host', 'port', 'protocol', 'username', 'password']
    }
    return headers_map.get(data_type, ['data'])