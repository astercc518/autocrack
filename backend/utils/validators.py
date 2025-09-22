#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证器工具函数
"""

import re
import json
from urllib.parse import urlparse

def validate_url(url):
    """验证URL格式"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def validate_ip(ip):
    """验证IP地址格式"""
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(pattern, ip):
        parts = ip.split('.')
        return all(0 <= int(part) <= 255 for part in parts)
    return False

def validate_port(port):
    """验证端口号"""
    try:
        port_num = int(port)
        return 1 <= port_num <= 65535
    except:
        return False

def validate_json(json_str):
    """验证JSON格式"""
    try:
        json.loads(json_str)
        return True
    except:
        return False

def validate_email(email):
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_domain(domain):
    """验证域名格式"""
    pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    return re.match(pattern, domain) is not None

def sanitize_input(text):
    """清理输入文本"""
    if not text:
        return ""
    
    # 移除HTML标签
    clean = re.sub(r'<[^>]+>', '', text)
    
    # 移除特殊字符，保留字母数字和常见符号
    clean = re.sub(r'[^\w\s\-_.@:]', '', clean)
    
    return clean.strip()

def validate_file_extension(filename, allowed_extensions):
    """验证文件扩展名"""
    if not filename:
        return False
    
    extension = filename.lower().split('.')[-1] if '.' in filename else ''
    return extension in [ext.lower() for ext in allowed_extensions]