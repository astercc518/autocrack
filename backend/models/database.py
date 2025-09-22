#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化和基础配置
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

db = SQLAlchemy()

def init_db():
    """初始化数据库"""
    from models.target import Target
    from models.attack import Attack
    from models.proxy import Proxy
    from models.wordlist import Wordlist
    from models.result import AttackResult
    
    db.create_all()
    print("📁 数据库初始化完成")

def create_tables():
    """创建所有表"""
    db.create_all()

def drop_tables():
    """删除所有表"""
    db.drop_all()

def reset_database():
    """重置数据库"""
    drop_tables()
    create_tables()
    print("🔄 数据库重置完成")