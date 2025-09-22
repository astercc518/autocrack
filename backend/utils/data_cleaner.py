#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据清洗工具
提供目标站数据、攻击数据的清洗和预处理功能
"""

import re
import csv
import json
import logging
import hashlib
from typing import List, Dict, Set, Any, Tuple, Optional
import urllib.parse
from urllib.parse import urlparse, urljoin
from ipaddress import ip_address, AddressValueError
# import validators  # 注释掉，使用自定义验证

logger = logging.getLogger(__name__)

class DataCleaner:
    """数据清洗器"""
    
    def __init__(self):
        self.cleaned_count = 0
        self.duplicate_count = 0
        self.invalid_count = 0
        self.total_count = 0
        
        # 常见的无效URL模式
        self.invalid_url_patterns = [
            r'^javascript:',
            r'^mailto:',
            r'^tel:',
            r'^ftp:',
            r'^\#',
            r'^data:',
        ]
        
        # 编译正则表达式
        self.invalid_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.invalid_url_patterns]
        
        # 常见的用户名/密码黑名单
        self.username_blacklist = {
            'admin', 'test', 'user', 'demo', 'guest', 'example',
            'sample', 'default', 'temp', 'anonymous', 'root'
        }
        
        self.password_blacklist = {
            'password', '123456', 'admin', 'test', 'demo', 'guest',
            '111111', '000000', 'qwerty', 'abc123', 'password123'
        }
        
    def reset_stats(self):
        """重置统计信息"""
        self.cleaned_count = 0
        self.duplicate_count = 0
        self.invalid_count = 0
        self.total_count = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """获取清洗统计信息"""
        return {
            'total': self.total_count,
            'cleaned': self.cleaned_count,
            'duplicates': self.duplicate_count,
            'invalid': self.invalid_count,
            'success_rate': round((self.cleaned_count / self.total_count * 100), 2) if self.total_count > 0 else 0
        }
    
    def clean_urls(self, urls: List[str], base_url: Optional[str] = None) -> Tuple[List[str], Dict[str, Any]]:
        """
        清洗URL列表
        
        Args:
            urls: URL列表
            base_url: 基础URL，用于处理相对路径
            
        Returns:
            (清洗后的URL列表, 统计信息)
        """
        self.reset_stats()
        self.total_count = len(urls)
        
        cleaned_urls = []
        seen_urls = set()
        
        for url in urls:
            if not url or not isinstance(url, str):
                self.invalid_count += 1
                continue
                
            # 去除前后空白字符
            url = url.strip()
            
            # 跳过空字符串
            if not url:
                self.invalid_count += 1
                continue
            
            # 检查是否为无效URL模式
            if self._is_invalid_url_pattern(url):
                self.invalid_count += 1
                continue
            
            # 处理相对URL
            if base_url and not url.startswith(('http://', 'https://')):
                url = urljoin(base_url, url)
            
            # 验证URL格式
            if not self._is_valid_url(url):
                self.invalid_count += 1
                continue
            
            # 标准化URL
            normalized_url = self._normalize_url(url)
            
            # 去重
            if normalized_url in seen_urls:
                self.duplicate_count += 1
                continue
            
            seen_urls.add(normalized_url)
            cleaned_urls.append(normalized_url)
            self.cleaned_count += 1
        
        logger.info(f"URL清洗完成: 总数{self.total_count}, 有效{self.cleaned_count}, 重复{self.duplicate_count}, 无效{self.invalid_count}")
        
        return cleaned_urls, self.get_stats()
    
    def clean_credentials(self, credentials: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
        """
        清洗认证凭据数据
        
        Args:
            credentials: 凭据列表，每个元素包含username和password
            
        Returns:
            (清洗后的凭据列表, 统计信息)
        """
        self.reset_stats()
        self.total_count = len(credentials)
        
        cleaned_credentials = []
        seen_combinations = set()
        
        for cred in credentials:
            if not isinstance(cred, dict):
                self.invalid_count += 1
                continue
            
            username = cred.get('username', '').strip()
            password = cred.get('password', '').strip()
            
            # 验证必需字段
            if not username or not password:
                self.invalid_count += 1
                continue
            
            # 检查是否在黑名单中
            if self._is_blacklisted_credential(username, password):
                self.invalid_count += 1
                continue
            
            # 验证凭据格式
            if not self._is_valid_credential(username, password):
                self.invalid_count += 1
                continue
            
            # 创建组合哈希用于去重
            combo_hash = hashlib.md5(f"{username}:{password}".encode()).hexdigest()
            
            if combo_hash in seen_combinations:
                self.duplicate_count += 1
                continue
            
            seen_combinations.add(combo_hash)
            cleaned_credentials.append({
                'username': username,
                'password': password,
                'hash': combo_hash
            })
            self.cleaned_count += 1
        
        logger.info(f"凭据清洗完成: 总数{self.total_count}, 有效{self.cleaned_count}, 重复{self.duplicate_count}, 无效{self.invalid_count}")
        
        return cleaned_credentials, self.get_stats()
    
    def clean_proxies(self, proxies: List[str]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        清洗代理服务器数据
        
        Args:
            proxies: 代理服务器列表
            
        Returns:
            (清洗后的代理列表, 统计信息)
        """
        self.reset_stats()
        self.total_count = len(proxies)
        
        cleaned_proxies = []
        seen_proxies = set()
        
        for proxy in proxies:
            if not proxy or not isinstance(proxy, str):
                self.invalid_count += 1
                continue
            
            proxy = proxy.strip()
            if not proxy:
                self.invalid_count += 1
                continue
            
            # 解析代理格式
            parsed_proxy = self._parse_proxy(proxy)
            if not parsed_proxy:
                self.invalid_count += 1
                continue
            
            # 验证IP和端口
            if not self._is_valid_proxy(parsed_proxy):
                self.invalid_count += 1
                continue
            
            # 创建代理标识用于去重
            proxy_id = f"{parsed_proxy['host']}:{parsed_proxy['port']}"
            
            if proxy_id in seen_proxies:
                self.duplicate_count += 1
                continue
            
            seen_proxies.add(proxy_id)
            cleaned_proxies.append(parsed_proxy)
            self.cleaned_count += 1
        
        logger.info(f"代理清洗完成: 总数{self.total_count}, 有效{self.cleaned_count}, 重复{self.duplicate_count}, 无效{self.invalid_count}")
        
        return cleaned_proxies, self.get_stats()
    
    def _is_invalid_url_pattern(self, url: str) -> bool:
        """检查是否为无效URL模式"""
        for pattern in self.invalid_patterns:
            if pattern.match(url):
                return True
        return False
    
    def _is_valid_url(self, url: str) -> bool:
        """验证URL格式"""
        try:
            result = urlparse(url)
            # 检查scheme和netloc
            if not result.scheme or not result.netloc:
                return False
            
            # 只允许http和https
            if result.scheme not in ['http', 'https']:
                return False
            
            # 使用简单的URL验证
            return self._simple_url_validation(url)
        except Exception:
            return False
    
    def _normalize_url(self, url: str) -> str:
        """标准化URL"""
        try:
            parsed = urlparse(url)
            
            # 移除默认端口
            netloc = parsed.netloc
            if parsed.scheme == 'http' and netloc.endswith(':80'):
                netloc = netloc[:-3]
            elif parsed.scheme == 'https' and netloc.endswith(':443'):
                netloc = netloc[:-4]
            
            # 重新构建URL
            normalized = f"{parsed.scheme}://{netloc}{parsed.path}"
            
            # 添加查询参数（如果有）
            if parsed.query:
                normalized += f"?{parsed.query}"
            
            # 去除尾部斜杠（除非是根路径）
            if normalized.endswith('/') and len(parsed.path) > 1:
                normalized = normalized[:-1]
            
            return normalized.lower()
        except Exception:
            return url.lower()
    
    def _is_blacklisted_credential(self, username: str, password: str) -> bool:
        """检查凭据是否在黑名单中"""
        username_lower = username.lower()
        password_lower = password.lower()
        
        return (username_lower in self.username_blacklist or 
                password_lower in self.password_blacklist)
    
    def _is_valid_credential(self, username: str, password: str) -> bool:
        """验证凭据格式"""
        # 基本长度检查
        if len(username) < 1 or len(username) > 50:
            return False
        
        if len(password) < 1 or len(password) > 100:
            return False
        
        # 检查是否包含不可见字符
        if any(ord(c) < 32 for c in username + password):
            return False
        
        return True
    
    def _parse_proxy(self, proxy: str) -> Optional[Dict[str, Any]]:
        """解析代理字符串"""
        try:
            # 支持多种格式：
            # 1. host:port
            # 2. protocol://host:port
            # 3. protocol://username:password@host:port
            
            original_proxy = proxy
            protocol = 'http'  # 默认协议
            
            # 提取协议
            if '://' in proxy:
                protocol, proxy = proxy.split('://', 1)
            
            # 提取认证信息
            username = None
            password = None
            if '@' in proxy:
                auth_part, proxy = proxy.rsplit('@', 1)
                if ':' in auth_part:
                    username, password = auth_part.split(':', 1)
                else:
                    username = auth_part
            
            # 提取主机和端口
            if ':' in proxy:
                host, port = proxy.rsplit(':', 1)
                port = int(port)
            else:
                host = proxy
                port = 8080  # 默认端口
            
            return {
                'host': host,
                'port': port,
                'protocol': protocol,
                'username': username,
                'password': password,
                'original': original_proxy
            }
            
        except Exception as e:
            logger.debug(f"代理解析失败 {proxy}: {str(e)}")
            return None
    
    def _is_valid_proxy(self, proxy: Dict[str, Any]) -> bool:
        """验证代理有效性"""
        try:
            # 验证IP地址
            ip_address(proxy['host'])
        except AddressValueError:
            # 检查是否为有效域名
            if not self._is_valid_domain(proxy['host']):
                return False
        
        # 验证端口范围
        port = proxy['port']
        if not isinstance(port, int) or port < 1 or port > 65535:
            return False
        
        # 验证协议
        if proxy['protocol'] not in ['http', 'https', 'socks4', 'socks5']:
            return False
        
        return True
    
    def _simple_url_validation(self, url: str) -> bool:
        """简单的URL验证"""
        try:
            result = urlparse(url)
            return bool(result.scheme and result.netloc)
        except Exception:
            return False
    
    def _is_valid_domain(self, domain: str) -> bool:
        """验证域名格式"""
        try:
            # 简单的域名验证
            if not domain or len(domain) > 253:
                return False
            
            # 检查域名格式
            import re
            domain_pattern = re.compile(
                r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)*(com|org|net|edu|gov|mil|int|arpa|[a-z]{2})$'
            )
            return bool(domain_pattern.match(domain))
        except Exception:
            return False


class DataValidator:
    """数据验证器"""
    
    @staticmethod
    def validate_target_data(data: Dict[str, Any]) -> Dict[str, List[str]]:
        """验证目标站数据"""
        errors = {}
        
        # 验证URL
        if 'url' not in data or not data['url']:
            errors.setdefault('url', []).append('URL字段必填')
        elif not DataValidator._simple_url_validation(data['url']):
            errors.setdefault('url', []).append('URL格式无效')
        
        # 验证名称
        if 'name' not in data or not data['name']:
            errors.setdefault('name', []).append('名称字段必填')
        elif len(data['name']) > 100:
            errors.setdefault('name', []).append('名称长度不能超过100字符')
        
        # 验证描述长度
        if 'description' in data and len(data['description']) > 500:
            errors.setdefault('description', []).append('描述长度不能超过500字符')
        
        return errors
    
    @staticmethod
    def _simple_url_validation(url: str) -> bool:
        """简单的URL验证"""
        try:
            result = urlparse(url)
            return bool(result.scheme and result.netloc and result.scheme in ['http', 'https'])
        except Exception:
            return False
    
    @staticmethod
    def validate_credential_data(data: Dict[str, Any]) -> Dict[str, List[str]]:
        """验证凭据数据"""
        errors = {}
        
        # 验证用户名
        if 'username' not in data or not data['username']:
            errors.setdefault('username', []).append('用户名字段必填')
        elif len(data['username']) > 50:
            errors.setdefault('username', []).append('用户名长度不能超过50字符')
        
        # 验证密码
        if 'password' not in data or not data['password']:
            errors.setdefault('password', []).append('密码字段必填')
        elif len(data['password']) > 100:
            errors.setdefault('password', []).append('密码长度不能超过100字符')
        
        return errors


# 数据清洗工具函数
def clean_csv_data(file_path: str, data_type: str = 'urls') -> Tuple[List[Any], Dict[str, Any]]:
    """
    清洗CSV文件数据
    
    Args:
        file_path: CSV文件路径
        data_type: 数据类型 ('urls', 'credentials', 'proxies')
        
    Returns:
        (清洗后的数据, 统计信息)
    """
    cleaner = DataCleaner()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            raw_data = list(reader)
        
        if data_type == 'urls':
            urls = [row.get('url', '') for row in raw_data]
            return cleaner.clean_urls(urls)
        
        elif data_type == 'credentials':
            credentials = []
            for row in raw_data:
                credentials.append({
                    'username': row.get('username', ''),
                    'password': row.get('password', '')
                })
            return cleaner.clean_credentials(credentials)
        
        elif data_type == 'proxies':
            proxies = [row.get('proxy', '') for row in raw_data]
            return cleaner.clean_proxies(proxies)
        
        else:
            raise ValueError(f"不支持的数据类型: {data_type}")
            
    except Exception as e:
        logger.error(f"CSV数据清洗失败 {file_path}: {str(e)}")
        return [], {'error': str(e)}


def batch_clean_data(data_list: List[Dict[str, Any]], data_type: str) -> Tuple[List[Any], Dict[str, Any]]:
    """
    批量清洗数据
    
    Args:
        data_list: 数据列表
        data_type: 数据类型
        
    Returns:
        (清洗后的数据, 统计信息)
    """
    cleaner = DataCleaner()
    
    if data_type == 'urls':
        urls = [item.get('url', '') for item in data_list]
        return cleaner.clean_urls(urls)
    
    elif data_type == 'credentials':
        return cleaner.clean_credentials(data_list)
    
    elif data_type == 'proxies':
        proxies = [item.get('proxy', '') for item in data_list]
        return cleaner.clean_proxies(proxies)
    
    else:
        raise ValueError(f"不支持的数据类型: {data_type}")