#!/bin/bash
# AutoCrack 启动脚本

echo "============================================"
echo "🚀 AutoCrack 自动化撞库工具启动脚本"
echo "============================================"

# 检查Python环境
echo "📋 检查运行环境..."
python --version

# 安装Python依赖
echo "📦 安装Python依赖..."
pip install -r requirements.txt

# 启动后端服务
echo "🔧 启动后端API服务..."
cd backend
python app.py &
BACKEND_PID=$!

echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"
echo "📡 API服务地址: http://localhost:5000"

# 检查Node.js环境（如果需要）
echo "🌐 检查前端环境..."
cd ../frontend

if command -v npm &> /dev/null; then
    echo "📦 安装前端依赖..."
    npm install
    
    echo "🎨 启动前端开发服务器..."
    npm start &
    FRONTEND_PID=$!
    
    echo "✅ 前端服务已启动 (PID: $FRONTEND_PID)"
    echo "🌐 Web界面地址: http://localhost:3000"
else
    echo "⚠️  Node.js未安装，跳过前端服务"
    echo "📄 可以直接使用API服务或手动安装Node.js"
fi

echo ""
echo "============================================"
echo "🎉 AutoCrack 启动完成！"
echo "============================================"
echo "📡 后端API: http://localhost:5000"
echo "🌐 前端界面: http://localhost:3000"
echo "📚 API文档: http://localhost:5000/api/health"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo "============================================"

# 等待用户中断
wait