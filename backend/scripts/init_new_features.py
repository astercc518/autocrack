#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
创建新增的用户权限、数据分配、反馈相关表
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from models.database import db, init_db
from models.user import User, Role, Permission, RoleType
from models.distribution import DistributionTask, ResourceAllocation, TaskQueue, DistributionRule
from models.feedback import AttackFeedback, PerformanceMetric, SystemAlert, FeedbackSummary
from config.settings import Config

def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def init_roles_and_permissions():
    """初始化角色和权限"""
    try:
        # 创建默认角色
        roles_data = [
            {
                'name': 'admin',
                'display_name': '系统管理员',
                'description': '拥有所有权限的超级管理员',
                'permissions': [p.value for p in Permission]  # 所有权限
            },
            {
                'name': 'manager',
                'display_name': '项目管理员',
                'description': '负责项目管理和数据管理',
                'permissions': [
                    Permission.TARGET_CREATE.value, Permission.TARGET_READ.value,
                    Permission.TARGET_UPDATE.value, Permission.ATTACK_CREATE.value,
                    Permission.ATTACK_READ.value, Permission.ATTACK_UPDATE.value,
                    Permission.ATTACK_EXECUTE.value, Permission.DATA_IMPORT.value,
                    Permission.DATA_EXPORT.value, Permission.DATA_CLEAN.value,
                    Permission.DATA_DISTRIBUTE.value, Permission.DATA_FEEDBACK.value,
                    Permission.PROXY_READ.value, Permission.SYSTEM_MONITOR.value
                ]
            },
            {
                'name': 'operator',
                'display_name': '系统操作员',
                'description': '负责执行攻击任务和数据处理',
                'permissions': [
                    Permission.TARGET_READ.value, Permission.ATTACK_READ.value,
                    Permission.ATTACK_EXECUTE.value, Permission.DATA_CLEAN.value,
                    Permission.DATA_FEEDBACK.value, Permission.PROXY_READ.value
                ]
            },
            {
                'name': 'viewer',
                'display_name': '查看者',
                'description': '只能查看系统信息',
                'permissions': [
                    Permission.TARGET_READ.value, Permission.ATTACK_READ.value,
                    Permission.PROXY_READ.value, Permission.SYSTEM_MONITOR.value
                ]
            }
        ]
        
        for role_data in roles_data:
            existing_role = Role.query.filter_by(name=role_data['name']).first()
            if not existing_role:
                role = Role(
                    name=role_data['name'],
                    display_name=role_data['display_name'],
                    description=role_data['description'],
                    permissions=role_data['permissions']
                )
                db.session.add(role)
                print(f"✓ 创建角色: {role_data['display_name']}")
            else:
                # 更新权限
                existing_role.permissions = role_data['permissions']
                print(f"✓ 更新角色权限: {role_data['display_name']}")
        
        db.session.commit()
        print("✓ 角色和权限初始化完成")
        
    except Exception as e:
        db.session.rollback()
        print(f"✗ 角色和权限初始化失败: {str(e)}")

def create_default_admin():
    """创建默认管理员账户"""
    try:
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@autocrack.com',
                real_name='系统管理员',
                is_superuser=True
            )
            admin_user.set_password('admin123')
            
            # 分配管理员角色
            admin_role = Role.query.filter_by(name='admin').first()
            if admin_role:
                admin_user.add_role(admin_role)
            
            db.session.add(admin_user)
            db.session.commit()
            
            print("✓ 创建默认管理员账户")
            print("  用户名: admin")
            print("  密码: admin123")
            print("  ⚠️  请在生产环境中立即修改密码!")
        else:
            print("✓ 管理员账户已存在")
            
    except Exception as e:
        db.session.rollback()
        print(f"✗ 创建管理员账户失败: {str(e)}")

def create_default_queues():
    """创建默认任务队列"""
    try:
        queues_data = [
            {
                'name': 'default',
                'description': '默认任务队列',
                'max_concurrent_tasks': 5,
                'max_queue_size': 100
            },
            {
                'name': 'high_priority',
                'description': '高优先级任务队列',
                'max_concurrent_tasks': 3,
                'max_queue_size': 50
            },
            {
                'name': 'low_priority',
                'description': '低优先级任务队列',
                'max_concurrent_tasks': 10,
                'max_queue_size': 200
            }
        ]
        
        for queue_data in queues_data:
            existing_queue = TaskQueue.query.filter_by(name=queue_data['name']).first()
            if not existing_queue:
                queue = TaskQueue(
                    name=queue_data['name'],
                    description=queue_data['description'],
                    max_concurrent_tasks=queue_data['max_concurrent_tasks'],
                    max_queue_size=queue_data['max_queue_size']
                )
                db.session.add(queue)
                print(f"✓ 创建任务队列: {queue_data['name']}")
        
        db.session.commit()
        print("✓ 默认任务队列创建完成")
        
    except Exception as e:
        db.session.rollback()
        print(f"✗ 创建任务队列失败: {str(e)}")

def main():
    """主函数"""
    print("=" * 60)
    print("🔧 AutoCrack 数据库初始化")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        try:
            # 创建所有表
            print("📊 创建数据库表...")
            db.create_all()
            print("✓ 数据库表创建完成")
            
            # 初始化角色和权限
            print("\n👥 初始化角色和权限...")
            init_roles_and_permissions()
            
            # 创建默认管理员
            print("\n🔑 创建默认管理员...")
            create_default_admin()
            
            # 创建默认队列
            print("\n📋 创建默认任务队列...")
            create_default_queues()
            
            print("\n" + "=" * 60)
            print("✅ 数据库初始化完成!")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ 数据库初始化失败: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    main()