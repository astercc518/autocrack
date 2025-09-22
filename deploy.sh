#!/bin/bash

# AutoCrack Docker 部署脚本

set -e

echo "=============================================="
echo "🐳 AutoCrack Docker 一键部署脚本"
echo "=============================================="

# 检查Docker环境
check_docker() {
    echo "🔍 检查Docker环境..."
    
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker未安装，请先安装Docker"
        echo "📋 安装指南: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose未安装，请先安装Docker Compose"
        echo "📋 安装指南: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    echo "✅ Docker环境检查完成"
}

# 构建镜像
build_images() {
    echo "🔨 构建AutoCrack Docker镜像..."
    
    docker-compose build --no-cache
    
    if [ $? -eq 0 ]; then
        echo "✅ 镜像构建成功"
    else
        echo "❌ 镜像构建失败"
        exit 1
    fi
}

# 启动服务
start_services() {
    echo "🚀 启动AutoCrack服务..."
    
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        echo "✅ 服务启动成功"
    else
        echo "❌ 服务启动失败"
        exit 1
    fi
}

# 检查服务状态
check_services() {
    echo "🔍 检查服务状态..."
    
    sleep 10
    
    echo "📊 服务状态:"
    docker-compose ps
    
    echo ""
    echo "🌐 健康检查:"
    
    # 检查后端API
    if curl -f -s http://localhost:5000/api/health > /dev/null; then
        echo "✅ 后端API服务正常 - http://localhost:5000"
    else
        echo "⚠️  后端API服务可能未就绪，请稍后再试"
    fi
    
    # 检查Nginx
    if curl -f -s http://localhost:80/health > /dev/null; then
        echo "✅ Nginx代理服务正常 - http://localhost"
    else
        echo "⚠️  Nginx代理服务可能未就绪，请稍后再试"
    fi
}

# 显示访问信息
show_access_info() {
    echo ""
    echo "=============================================="
    echo "🎉 AutoCrack 部署完成！"
    echo "=============================================="
    echo "📡 API服务地址: http://localhost:5000"
    echo "🌐 Web界面地址: http://localhost"
    echo "📚 API文档: http://localhost:5000/api/health"
    echo "💾 Redis管理: localhost:6379"
    echo ""
    echo "🔧 管理命令:"
    echo "  查看日志: docker-compose logs -f"
    echo "  停止服务: docker-compose down"
    echo "  重启服务: docker-compose restart"
    echo "  查看状态: docker-compose ps"
    echo ""
    echo "📁 数据目录:"
    echo "  数据文件: ./data/"
    echo "  日志文件: ./logs/"
    echo "=============================================="
}

# 主要部署流程
main() {
    case "${1:-deploy}" in
        "build")
            check_docker
            build_images
            ;;
        "start")
            start_services
            check_services
            show_access_info
            ;;
        "deploy")
            check_docker
            build_images
            start_services
            check_services
            show_access_info
            ;;
        "stop")
            echo "🛑 停止AutoCrack服务..."
            docker-compose down
            echo "✅ 服务已停止"
            ;;
        "restart")
            echo "🔄 重启AutoCrack服务..."
            docker-compose restart
            check_services
            ;;
        "logs")
            echo "📋 查看服务日志..."
            docker-compose logs -f
            ;;
        "clean")
            echo "🧹 清理Docker资源..."
            docker-compose down -v
            docker system prune -f
            echo "✅ 清理完成"
            ;;
        *)
            echo "用法: $0 {deploy|build|start|stop|restart|logs|clean}"
            echo ""
            echo "命令说明:"
            echo "  deploy  - 完整部署 (构建+启动)"
            echo "  build   - 仅构建镜像"
            echo "  start   - 仅启动服务"
            echo "  stop    - 停止服务"
            echo "  restart - 重启服务"
            echo "  logs    - 查看日志"
            echo "  clean   - 清理资源"
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"