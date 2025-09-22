#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据导入API接口
"""

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import csv
import json
from models.database import db
from models.target import Target
from models.proxy import Proxy
from models.wordlist import Wordlist
from utils.validators import validate_file_extension
from datetime import datetime

data_import_bp = Blueprint('data_import', __name__)

ALLOWED_EXTENSIONS = ['txt', 'csv', 'json']
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'data')

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return validate_file_extension(filename, ALLOWED_EXTENSIONS)

@data_import_bp.route('/targets', methods=['POST'])
def import_targets():
    """批量导入目标站点"""
    try:
        if 'file' in request.files:
            # 文件上传方式
            file = request.files['file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, 'targets', filename)
                
                # 确保目录存在
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                file.save(filepath)
                
                # 解析文件
                targets_data = _parse_targets_file(filepath)
            else:
                return jsonify({
                    'success': False,
                    'error': '无效的文件格式'
                }), 400
        else:
            # JSON数据方式
            data = request.get_json()
            targets_data = data.get('targets', [])
        
        if not targets_data:
            return jsonify({
                'success': False,
                'error': '没有提供目标数据'
            }), 400
        
        added_count = 0
        errors = []
        
        for target_data in targets_data:
            try:
                # 验证必需字段
                if not target_data.get('name') or not target_data.get('url'):
                    errors.append(f"名称和URL是必需的: {target_data}")
                    continue
                
                # 检查是否已存在
                existing = Target.query.filter_by(
                    name=target_data['name']
                ).first()
                
                if existing:
                    continue
                
                # 创建目标
                target = Target(
                    name=target_data['name'],
                    url=target_data['url'],
                    login_url=target_data.get('login_url', ''),
                    method=target_data.get('method', 'POST'),
                    username_field=target_data.get('username_field', 'username'),
                    password_field=target_data.get('password_field', 'password'),
                    additional_fields=json.dumps(target_data.get('additional_fields', {})),
                    success_indicators=json.dumps(target_data.get('success_indicators', [])),
                    failure_indicators=json.dumps(target_data.get('failure_indicators', [])),
                    headers=json.dumps(target_data.get('headers', {})),
                    cookies=json.dumps(target_data.get('cookies', {})),
                    timeout=target_data.get('timeout', 30)
                )
                
                db.session.add(target)
                added_count += 1
                
            except Exception as e:
                errors.append(f"处理目标失败 {target_data.get('name', 'unknown')}: {str(e)}")
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'成功导入 {added_count} 个目标站点',
            'added_count': added_count,
            'errors': errors
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@data_import_bp.route('/proxies', methods=['POST'])
def import_proxies():
    """批量导入代理"""
    try:
        if 'file' in request.files:
            # 文件上传方式
            file = request.files['file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, 'proxies', filename)
                
                # 确保目录存在
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                file.save(filepath)
                
                # 解析文件
                proxies_data = _parse_proxies_file(filepath)
            else:
                return jsonify({
                    'success': False,
                    'error': '无效的文件格式'
                }), 400
        else:
            # JSON数据方式
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
                # 验证必需字段
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
                    source=proxy_data.get('source', 'import')
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

@data_import_bp.route('/wordlists', methods=['POST'])
def import_wordlist():
    """导入字典文件"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': '没有上传文件'
            }), 400
        
        file = request.files['file']
        if not file or not file.filename or not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': '无效的文件格式'
            }), 400
        
        # 获取其他参数
        name = request.form.get('name')
        wordlist_type = request.form.get('type', 'combo')
        description = request.form.get('description', '')
        
        if not name:
            return jsonify({
                'success': False,
                'error': '字典名称是必需的'
            }), 400
        
        # 保存文件
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, 'wordlists', filename)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)
        
        # 分析文件
        file_size = os.path.getsize(filepath)
        line_count = _count_file_lines(filepath)
        encoding = _detect_file_encoding(filepath)
        
        # 创建字典记录
        wordlist = Wordlist(
            name=name,
            file_path=filepath,
            wordlist_type=wordlist_type,
            file_size=file_size,
            line_count=line_count,
            encoding=encoding,
            description=description,
            source='upload'
        )
        
        db.session.add(wordlist)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': wordlist.to_dict(),
            'message': '字典文件导入成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def _parse_targets_file(filepath):
    """解析目标文件"""
    targets = []
    
    try:
        if filepath.endswith('.json'):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                targets = data if isinstance(data, list) else data.get('targets', [])
        
        elif filepath.endswith('.csv'):
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    targets.append(row)
        
        elif filepath.endswith('.txt'):
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            targets.append({
                                'name': parts[0],
                                'url': parts[1],
                                'login_url': parts[2] if len(parts) > 2 else ''
                            })
    
    except Exception as e:
        raise Exception(f"解析目标文件失败: {e}")
    
    return targets

def _parse_proxies_file(filepath):
    """解析代理文件"""
    proxies = []
    
    try:
        if filepath.endswith('.json'):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                proxies = data if isinstance(data, list) else data.get('proxies', [])
        
        elif filepath.endswith('.csv'):
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    proxies.append(row)
        
        elif filepath.endswith('.txt'):
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # 支持多种格式：host:port, host:port:username:password, http://host:port等
                        if '://' in line:
                            # URL格式
                            parts = line.replace('http://', '').replace('https://', '').split(':')
                            if len(parts) >= 2:
                                proxies.append({
                                    'host': parts[0],
                                    'port': parts[1],
                                    'proxy_type': 'http'
                                })
                        elif ':' in line:
                            parts = line.split(':')
                            if len(parts) >= 2:
                                proxy_data = {
                                    'host': parts[0],
                                    'port': parts[1],
                                    'proxy_type': 'http'
                                }
                                if len(parts) >= 4:
                                    proxy_data['username'] = parts[2]
                                    proxy_data['password'] = parts[3]
                                proxies.append(proxy_data)
    
    except Exception as e:
        raise Exception(f"解析代理文件失败: {e}")
    
    return proxies

def _count_file_lines(filepath):
    """统计文件行数"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return sum(1 for line in f)
    except:
        return 0

def _detect_file_encoding(filepath):
    """检测文件编码"""
    try:
        # 简单的编码检测，避免额外依赖
        encodings = ['utf-8', 'gbk', 'latin-1']
        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    f.read(100)  # 尝试读取前100个字符
                return encoding
            except UnicodeDecodeError:
                continue
        return 'utf-8'
    except:
        return 'utf-8'

@data_import_bp.route('/templates/targets', methods=['GET'])
def get_targets_template():
    """获取目标导入模板"""
    template = [
        {
            "name": "示例网站",
            "url": "https://example.com",
            "login_url": "https://example.com/login",
            "method": "POST",
            "username_field": "username",
            "password_field": "password",
            "additional_fields": {"csrf_token": ""},
            "success_indicators": ["dashboard", "welcome"],
            "failure_indicators": ["error", "invalid"],
            "headers": {"User-Agent": "Custom Agent"},
            "cookies": {},
            "timeout": 30
        }
    ]
    
    return jsonify({
        'success': True,
        'data': template
    })

@data_import_bp.route('/templates/proxies', methods=['GET'])
def get_proxies_template():
    """获取代理导入模板"""
    template = [
        {
            "host": "127.0.0.1",
            "port": 8080,
            "proxy_type": "http",
            "username": "",
            "password": "",
            "country": "CN",
            "region": "Beijing",
            "city": "Beijing",
            "source": "free"
        }
    ]
    
    return jsonify({
        'success': True,
        'data': template
    })