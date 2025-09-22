#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoCrack 系统验证和测试脚本
用于验证系统各个组件是否正常运行
"""

import requests
import time
import sys
import json
from datetime import datetime

class AutoCrackTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
    
    def log(self, message, level="INFO"):
        """记录测试日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [{level}] {message}")
    
    def test_api_health(self):
        """测试API健康状态"""
        self.log("🔍 测试API健康状态...")
        try:
            response = self.session.get(f"{self.base_url}/api/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ API健康检查通过 - 状态: {data.get('status')}")
                return True
            else:
                self.log(f"❌ API健康检查失败 - 状态码: {response.status_code}", "ERROR")
                return False
        except requests.exceptions.RequestException as e:
            self.log(f"❌ API连接失败: {str(e)}", "ERROR")
            return False
    
    def test_api_version(self):
        """测试版本信息接口"""
        self.log("🔍 测试版本信息接口...")
        try:
            response = self.session.get(f"{self.base_url}/api/version", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ 版本信息获取成功 - 版本: {data.get('version')}")
                return True
            else:
                self.log(f"❌ 版本信息获取失败 - 状态码: {response.status_code}", "ERROR")
                return False
        except requests.exceptions.RequestException as e:
            self.log(f"❌ 版本信息请求失败: {str(e)}", "ERROR")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        self.log("🚀 开始AutoCrack系统测试...")
        self.log("=" * 60)
        
        tests = [
            ("API健康状态", self.test_api_health),
            ("版本信息接口", self.test_api_version),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            self.log(f"\n📋 运行测试: {test_name}")
            if test_func():
                passed += 1
                self.test_results.append((test_name, "PASS"))
            else:
                self.test_results.append((test_name, "FAIL"))
        
        # 生成测试报告
        self.generate_report(passed, total)
        
        return passed == total
    
    def generate_report(self, passed, total):
        """生成测试报告"""
        self.log("\n" + "=" * 60)
        self.log("📊 测试结果汇总")
        self.log("=" * 60)
        
        for test_name, result in self.test_results:
            status_icon = "✅" if result == "PASS" else "❌"
            self.log(f"{status_icon} {test_name}: {result}")
        
        self.log("\n" + "=" * 60)
        success_rate = (passed / total) * 100
        self.log(f"📈 测试通过率: {passed}/{total} ({success_rate:.1f}%)")
        
        if passed == total:
            self.log("🎉 所有测试通过！系统运行正常。")
        else:
            self.log("⚠️  部分测试失败，请检查系统配置。")
        
        self.log("=" * 60)

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AutoCrack系统测试工具")
    parser.add_argument(
        "--url", 
        default="http://localhost:5000", 
        help="API服务器地址 (默认: http://localhost:5000)"
    )
    parser.add_argument(
        "--wait", 
        type=int, 
        default=0, 
        help="测试前等待时间(秒) (默认: 0)"
    )
    
    args = parser.parse_args()
    
    if args.wait > 0:
        print(f"⏳ 等待 {args.wait} 秒后开始测试...")
        time.sleep(args.wait)
    
    tester = AutoCrackTester(args.url)
    success = tester.run_all_tests()
    
    # 根据测试结果设置退出码
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()