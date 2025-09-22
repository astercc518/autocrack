@echo off
REM AutoCrack 快速验证脚本 (Windows)

echo 🚀 AutoCrack 系统快速验证
echo =============================

REM 检查后端API
echo 🔍 检查后端API服务...
curl -f -s http://localhost:5000/api/health >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo ✅ 后端API服务正常
    echo 📊 API详情:
    curl -s http://localhost:5000/api/health
) else (
    echo ❌ 后端API服务不可用
    echo    请检查服务是否启动: docker-compose ps
)

echo.

REM 检查前端服务
echo 🔍 检查前端服务...
curl -f -s http://localhost:3000 >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo ✅ 前端服务正常 - http://localhost:3000
) else (
    curl -f -s http://localhost:80 >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        echo ✅ Nginx代理服务正常 - http://localhost
    ) else (
        echo ⚠️  前端服务可能未启动或配置错误
    )
)

echo.

REM 检查Docker容器状态
echo 🔍 检查Docker容器状态...
docker-compose --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo 📋 容器状态:
    docker-compose ps
) else (
    echo ⚠️  Docker Compose未安装
)

echo.
echo =============================
echo 🎉 验证完成！
echo 📚 详细测试请运行: python tests/test_system.py
echo 🌐 访问地址:
echo    - API服务: http://localhost:5000
echo    - Web界面: http://localhost:3000 或 http://localhost
echo =============================
pause