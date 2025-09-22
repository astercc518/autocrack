#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据验证工具函数
"""

import re
from typing import List, Dict, Any

def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """验证必需字段"""
    missing_fields = []
    for field in required_fields:
        if field not in data or not data[field]:
            missing_fields.append(field)
    return missing_fields

def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> bool:
    """验证密码强度"""
    if not password or len(password) < 8:
        return False
    
    # 至少包含一个字母和一个数字
    has_letter = re.search(r'[a-zA-Z]', password) is not None
    has_digit = re.search(r'\d', password) is not None
    
    return has_letter and has_digit

def validate_phone(phone: str) -> bool:
    """验证手机号格式"""
    if not phone:
        return True  # 手机号可选
    
    # 简单的手机号验证
    pattern = r'^1[3-9]\d{9}$'
    return re.match(pattern, phone) is not None

def validate_username(username: str) -> bool:
    """验证用户名格式"""
    if not username:
        return False
    
    # 用户名：3-20位，字母数字下划线
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return re.match(pattern, username) is not None

def validate_url(url: str) -> bool:
    """验证URL格式"""
    if not url:
        return False
    
    # 简单的URL验证
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return re.match(pattern, url) is not None