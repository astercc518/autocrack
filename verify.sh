#!/bin/bash

# AutoCrack 快速验证脚本

echo "🚀 AutoCrack 系统快速验证"
echo "============================="

# 检查后端API
echo "🔍 检查后端API服务..."
if curl -f -s http://localhost:5000/api/health > /dev/null; then
    echo "✅ 后端API服务正常"
    echo "📊 API详情:"
    curl -s http://localhost:5000/api/health | python3 -m json.tool 2>/dev/null || echo "  - API响应正常但格式可能不是JSON"
else
    echo "❌ 后端API服务不可用"
    echo "   请检查服务是否启动: docker-compose ps"
fi

echo ""

# 检查前端服务
echo "🔍 检查前端服务..."
if curl -f -s http://localhost:3000 > /dev/null; then
    echo "✅ 前端服务正常 - http://localhost:3000"
elif curl -f -s http://localhost:80 > /dev/null; then
    echo "✅ Nginx代理服务正常 - http://localhost"
else
    echo "⚠️  前端服务可能未启动或配置错误"
fi

echo ""

# 检查Docker容器状态
echo "🔍 检查Docker容器状态..."
if command -v docker-compose &> /dev/null; then
    echo "📋 容器状态:"
    docker-compose ps
else
    echo "⚠️  Docker Compose未安装"
fi

echo ""
echo "============================="
echo "🎉 验证完成！"
echo "📚 详细测试请运行: python3 tests/test_system.py"
echo "🌐 访问地址:"
echo "   - API服务: http://localhost:5000"
echo "   - Web界面: http://localhost:3000 或 http://localhost"
echo "=============================="