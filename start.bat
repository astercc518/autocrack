@echo off
:: AutoCrack Windows 启动脚本

echo ============================================
echo 🚀 AutoCrack 自动化撞库工具启动脚本
echo ============================================

:: 检查Python环境
echo 📋 检查运行环境...
python --version
if %ERRORLEVEL% neq 0 (
    echo ❌ Python未安装或未加入PATH
    echo 请安装Python 3.8+并重新运行
    pause
    exit /b 1
)

:: 安装Python依赖
echo 📦 安装Python依赖...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo ⚠️  依赖安装可能存在问题，继续启动...
)

:: 启动后端服务
echo 🔧 启动后端API服务...
cd backend
start "AutoCrack Backend" python app.py
cd ..

echo ✅ 后端服务已启动
echo 📡 API服务地址: http://localhost:5000

:: 检查Node.js环境
echo 🌐 检查前端环境...
node --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    cd frontend
    
    echo 📦 安装前端依赖...
    npm install
    
    echo 🎨 启动前端开发服务器...
    start "AutoCrack Frontend" npm start
    cd ..
    
    echo ✅ 前端服务已启动
    echo 🌐 Web界面地址: http://localhost:3000
) else (
    echo ⚠️  Node.js未安装，跳过前端服务
    echo 📄 可以直接使用API服务或手动安装Node.js
)

echo.
echo ============================================
echo 🎉 AutoCrack 启动完成！
echo ============================================
echo 📡 后端API: http://localhost:5000
echo 🌐 前端界面: http://localhost:3000
echo 📚 API文档: http://localhost:5000/api/health
echo.
echo 按任意键关闭此窗口...
echo ============================================

pause