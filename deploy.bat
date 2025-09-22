@echo off
:: AutoCrack Docker 部署脚本 (Windows版本)

setlocal EnableDelayedExpansion

echo =============================================
echo 🐳 AutoCrack Docker 一键部署脚本 (Windows)
echo =============================================

:: 检查Docker环境
:check_docker
echo 🔍 检查Docker环境...

docker --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Docker未安装，请先安装Docker Desktop
    echo 📋 下载地址: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Docker Compose未安装，请先安装Docker Compose
    echo 📋 安装指南: https://docs.docker.com/compose/install/
    pause
    exit /b 1
)

echo ✅ Docker环境检查完成

:: 解析命令行参数
set "ACTION=%1"
if "%ACTION%"=="" set "ACTION=deploy"

goto %ACTION% 2>nul || goto usage

:build
echo 🔨 构建AutoCrack Docker镜像...
docker-compose build --no-cache
if %ERRORLEVEL% equ 0 (
    echo ✅ 镜像构建成功
) else (
    echo ❌ 镜像构建失败
    pause
    exit /b 1
)
goto end

:start
echo 🚀 启动AutoCrack服务...
docker-compose up -d
if %ERRORLEVEL% equ 0 (
    echo ✅ 服务启动成功
) else (
    echo ❌ 服务启动失败
    pause
    exit /b 1
)
goto check_services

:deploy
call :check_docker
call :build
call :start
goto end

:stop
echo 🛑 停止AutoCrack服务...
docker-compose down
echo ✅ 服务已停止
goto end

:restart
echo 🔄 重启AutoCrack服务...
docker-compose restart
goto check_services

:logs
echo 📋 查看服务日志...
docker-compose logs -f
goto end

:clean
echo 🧹 清理Docker资源...
docker-compose down -v
docker system prune -f
echo ✅ 清理完成
goto end

:check_services
echo 🔍 检查服务状态...
timeout /t 10 /nobreak >nul

echo 📊 服务状态:
docker-compose ps

echo.
echo 🌐 健康检查:

:: 检查后端API
curl -f -s http://localhost:5000/api/health >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo ✅ 后端API服务正常 - http://localhost:5000
) else (
    echo ⚠️  后端API服务可能未就绪，请稍后再试
)

:: 检查Nginx
curl -f -s http://localhost:80/health >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo ✅ Nginx代理服务正常 - http://localhost
) else (
    echo ⚠️  Nginx代理服务可能未就绪，请稍后再试
)

:show_info
echo.
echo =============================================
echo 🎉 AutoCrack 部署完成！
echo =============================================
echo 📡 API服务地址: http://localhost:5000
echo 🌐 Web界面地址: http://localhost
echo 📚 API文档: http://localhost:5000/api/health
echo 💾 Redis管理: localhost:6379
echo.
echo 🔧 管理命令:
echo   查看日志: deploy.bat logs
echo   停止服务: deploy.bat stop
echo   重启服务: deploy.bat restart
echo   清理资源: deploy.bat clean
echo.
echo 📁 数据目录:
echo   数据文件: .\data\
echo   日志文件: .\logs\
echo =============================================
goto end

:usage
echo 用法: %0 {deploy^|build^|start^|stop^|restart^|logs^|clean}
echo.
echo 命令说明:
echo   deploy  - 完整部署 (构建+启动)
echo   build   - 仅构建镜像
echo   start   - 仅启动服务
echo   stop    - 停止服务
echo   restart - 重启服务
echo   logs    - 查看日志
echo   clean   - 清理资源
echo.
pause
exit /b 1

:end
if "%ACTION%"=="deploy" goto show_info
if "%ACTION%"=="start" goto show_info
echo 操作完成！
pause