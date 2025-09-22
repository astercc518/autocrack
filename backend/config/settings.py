#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoCrack配置文件
"""

import os
from datetime import timedelta

class Config:
    """基础配置类"""
    
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'autocrack-secret-key-2023'
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///autocrack.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    # Redis配置（用于任务队列）
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    
    # 攻击配置
    DEFAULT_THREADS = 10
    MAX_THREADS = 100
    DEFAULT_TIMEOUT = 30
    MAX_TIMEOUT = 300
    
    # 代理配置
    PROXY_CHECK_INTERVAL = 300  # 5分钟检查一次代理
    PROXY_TIMEOUT = 10
    MAX_PROXY_RETRIES = 3
    
    # 安全配置
    RATE_LIMIT_ENABLED = True
    MAX_REQUESTS_PER_MINUTE = 1000
    
    # 日志配置
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'autocrack.log'
    LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False
    LOG_LEVEL = 'WARNING'

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# 配置映射
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}