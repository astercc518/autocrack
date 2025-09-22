#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoCrack API测试脚本
测试所有主要API接口的功能
"""

import requests
import json
import time
from pprint import pprint

BASE_URL = "http://localhost:5000/api"

def test_health():
    """测试健康检查"""
    print("🔍 测试健康检查...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    print()

def test_targets():
    """测试目标管理"""
    print("🎯 测试目标管理...")
    
    # 获取所有目标
    print("获取所有目标:")
    response = requests.get(f"{BASE_URL}/targets/")
    print(f"状态码: {response.status_code}")
    pprint(response.json())
    
    # 创建新目标
    print("\n创建新目标:")
    target_data = {
        "name": "测试网站",
        "url": "https://httpbin.org/post",
        "login_url": "https://httpbin.org/post",
        "method": "POST",
        "username_field": "username",
        "password_field": "password",
        "success_indicators": ["success", "dashboard"],
        "failure_indicators": ["error", "invalid"]
    }
    
    response = requests.post(f"{BASE_URL}/targets/", json=target_data)
    print(f"状态码: {response.status_code}")
    if response.status_code == 201:
        target_id = response.json()['data']['id']
        print(f"创建成功，目标ID: {target_id}")
        return target_id
    else:
        print(f"创建失败: {response.json()}")
        return None
    print()

def test_proxies():
    """测试代理管理"""
    print("🌐 测试代理管理...")
    
    # 获取代理统计
    print("获取代理统计:")
    response = requests.get(f"{BASE_URL}/proxies/stats")
    print(f"状态码: {response.status_code}")
    pprint(response.json())
    
    # 添加测试代理
    print("\n添加测试代理:")
    proxy_data = {
        "host": "127.0.0.1",
        "port": 8080,
        "proxy_type": "http",
        "source": "test"
    }
    
    response = requests.post(f"{BASE_URL}/proxies/", json=proxy_data)
    print(f"状态码: {response.status_code}")
    if response.status_code == 201:
        proxy_id = response.json()['data']['id']
        print(f"创建成功，代理ID: {proxy_id}")
        return proxy_id
    else:
        print(f"创建失败: {response.json()}")
        return None
    print()

def test_attacks(target_id):
    """测试攻击任务"""
    if not target_id:
        print("⚠️ 跳过攻击测试（没有有效的目标ID）")
        return
    
    print("⚔️ 测试攻击任务...")
    
    # 获取所有攻击任务
    print("获取所有攻击任务:")
    response = requests.get(f"{BASE_URL}/attacks/")
    print(f"状态码: {response.status_code}")
    pprint(response.json())
    
    # 创建新攻击任务
    print("\n创建新攻击任务:")
    attack_data = {
        "name": "测试攻击任务",
        "target_id": target_id,
        "wordlist_type": "combo",
        "combo_list": "admin:admin\ntest:test\nuser:password",
        "threads": 2,
        "delay": 1.0,
        "timeout": 10,
        "use_proxy": False
    }
    
    response = requests.post(f"{BASE_URL}/attacks/", json=attack_data)
    print(f"状态码: {response.status_code}")
    if response.status_code == 201:
        attack_id = response.json()['data']['id']
        print(f"创建成功，攻击ID: {attack_id}")
        
        # 启动攻击（仅作演示，不实际执行）
        print(f"\n模拟启动攻击任务 {attack_id}:")
        start_response = requests.post(f"{BASE_URL}/attacks/{attack_id}/start")
        print(f"状态码: {start_response.status_code}")
        if start_response.status_code == 200:
            print("攻击任务启动成功")
            
            # 等待一秒后检查进度
            time.sleep(2)
            progress_response = requests.get(f"{BASE_URL}/attacks/{attack_id}/progress")
            print(f"进度查询状态码: {progress_response.status_code}")
            if progress_response.status_code == 200:
                pprint(progress_response.json())
            
            # 停止攻击
            stop_response = requests.post(f"{BASE_URL}/attacks/{attack_id}/stop")
            print(f"停止攻击状态码: {stop_response.status_code}")
        
        return attack_id
    else:
        print(f"创建失败: {response.json()}")
        return None
    print()

def test_data_import():
    """测试数据导入"""
    print("📥 测试数据导入...")
    
    # 测试目标模板获取
    print("获取目标导入模板:")
    response = requests.get(f"{BASE_URL}/import/templates/targets")
    print(f"状态码: {response.status_code}")
    pprint(response.json())
    
    # 测试代理模板获取
    print("\n获取代理导入模板:")
    response = requests.get(f"{BASE_URL}/import/templates/proxies")
    print(f"状态码: {response.status_code}")
    pprint(response.json())
    print()

def main():
    """主测试函数"""
    print("=" * 60)
    print("🚀 AutoCrack API 功能测试")
    print("=" * 60)
    
    try:
        # 测试基础功能
        test_health()
        
        # 测试各个模块
        target_id = test_targets()
        proxy_id = test_proxies()
        test_attacks(target_id)
        test_data_import()
        
        print("✅ 所有测试完成！")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务器")
        print("请确保后端服务已启动: python backend/app.py")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")

if __name__ == "__main__":
    main()