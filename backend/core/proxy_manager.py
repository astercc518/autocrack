#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代理池管理器
实现代理的自动切换、验证、负载均衡等功能
"""

import random
import time
import requests
import threading
from datetime import datetime, timedelta
from models.database import db
from models.proxy import Proxy
import logging

logger = logging.getLogger(__name__)

class ProxyManager:
    """代理池管理器"""
    
    def __init__(self):
        self.proxy_pool = []
        self.current_index = 0
        self.lock = threading.Lock()
        self.last_refresh = None
        self.refresh_interval = 300  # 5分钟刷新一次
        
        self._load_proxies()
    
    def _load_proxies(self):
        """从数据库加载代理"""
        try:
            with self.lock:
                # 加载可用的代理
                proxies = Proxy.query.filter_by(status='active', is_working=True).all()
                self.proxy_pool = proxies
                self.last_refresh = datetime.utcnow()
                
                logger.info(f"加载了 {len(self.proxy_pool)} 个可用代理")
                
        except Exception as e:
            logger.error(f"加载代理失败: {e}")
            self.proxy_pool = []
    
    def get_proxy(self):
        """获取一个可用的代理"""
        # 检查是否需要刷新代理池
        if (not self.last_refresh or 
            datetime.utcnow() - self.last_refresh > timedelta(seconds=self.refresh_interval)):
            self._load_proxies()
        
        if not self.proxy_pool:
            return None
        
        with self.lock:
            # 轮询方式选择代理
            proxy = self.proxy_pool[self.current_index % len(self.proxy_pool)]
            self.current_index += 1
            return proxy
    
    def get_random_proxy(self):
        """随机获取一个代理"""
        if not self.proxy_pool:
            self._load_proxies()
        
        if not self.proxy_pool:
            return None
        
        return random.choice(self.proxy_pool)
    
    def validate_proxy(self, proxy, test_url="http://httpbin.org/ip", timeout=10):
        """验证代理是否可用"""
        try:
            start_time = time.time()
            
            proxies = {
                'http': proxy.proxy_url,
                'https': proxy.proxy_url
            }
            
            response = requests.get(
                test_url,
                proxies=proxies,
                timeout=timeout,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                # 更新代理状态
                proxy.is_working = True
                proxy.response_time = response_time
                proxy.last_checked = datetime.utcnow()
                proxy.success_count += 1
                
                db.session.commit()
                return True
            else:
                self._mark_proxy_failed(proxy)
                return False
                
        except Exception as e:
            logger.warning(f"代理验证失败 {proxy.host}:{proxy.port} - {e}")
            self._mark_proxy_failed(proxy)
            return False
    
    def _mark_proxy_failed(self, proxy):
        """标记代理为失败"""
        try:
            proxy.failure_count += 1
            proxy.last_checked = datetime.utcnow()
            
            # 如果失败次数过多，禁用代理
            if proxy.failure_count > 10:
                proxy.is_working = False
                proxy.status = 'failed'
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"更新代理状态失败: {e}")
            db.session.rollback()
    
    def batch_validate_proxies(self, max_workers=10):
        """批量验证代理"""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        proxies = Proxy.query.filter_by(status='active').all()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.validate_proxy, proxy): proxy for proxy in proxies}
            
            valid_count = 0
            for future in as_completed(futures):
                proxy = futures[future]
                try:
                    is_valid = future.result()
                    if is_valid:
                        valid_count += 1
                except Exception as e:
                    logger.error(f"验证代理 {proxy.host}:{proxy.port} 时出错: {e}")
            
            logger.info(f"代理验证完成，有效代理: {valid_count}/{len(proxies)}")
            
            # 重新加载代理池
            self._load_proxies()
    
    def add_proxy(self, host, port, proxy_type='http', username=None, password=None, **kwargs):
        """添加新代理"""
        try:
            proxy = Proxy(
                host=host,
                port=port,
                proxy_type=proxy_type,
                username=username,
                password=password,
                **kwargs
            )
            
            db.session.add(proxy)
            db.session.commit()
            
            # 验证新代理
            if self.validate_proxy(proxy):
                logger.info(f"成功添加代理: {host}:{port}")
                return proxy
            else:
                logger.warning(f"代理验证失败: {host}:{port}")
                return None
                
        except Exception as e:
            logger.error(f"添加代理失败: {e}")
            db.session.rollback()
            return None
    
    def remove_proxy(self, proxy_id):
        """移除代理"""
        try:
            proxy = Proxy.query.get(proxy_id)
            if proxy:
                db.session.delete(proxy)
                db.session.commit()
                
                # 从内存池中移除
                with self.lock:
                    if proxy in self.proxy_pool:
                        self.proxy_pool.remove(proxy)
                
                logger.info(f"代理已移除: {proxy.host}:{proxy.port}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"移除代理失败: {e}")
            db.session.rollback()
            return False
    
    def get_proxy_stats(self):
        """获取代理池统计信息"""
        try:
            total = Proxy.query.count()
            active = Proxy.query.filter_by(status='active').count()
            working = Proxy.query.filter_by(is_working=True).count()
            
            return {
                'total': total,
                'active': active,
                'working': working,
                'in_pool': len(self.proxy_pool)
            }
            
        except Exception as e:
            logger.error(f"获取代理统计失败: {e}")
            return {'total': 0, 'active': 0, 'working': 0, 'in_pool': 0}
    
    def refresh_proxy_pool(self):
        """手动刷新代理池"""
        self._load_proxies()
        logger.info("代理池已刷新")