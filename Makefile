# AutoCrack Makefile
# 简化常用的 Docker 操作命令

.PHONY: help build start stop restart logs clean deploy deploy-prod test

# 默认目标
help:
	@echo "AutoCrack Docker 管理命令:"
	@echo ""
	@echo "  make build      - 构建 Docker 镜像"
	@echo "  make start      - 启动开发环境"
	@echo "  make stop       - 停止所有服务"
	@echo "  make restart    - 重启所有服务"
	@echo "  make logs       - 查看实时日志"
	@echo "  make clean      - 清理所有资源"
	@echo "  make deploy     - 完整部署 (构建+启动)"
	@echo "  make deploy-prod - 生产环境部署"
	@echo "  make test       - 运行 API 测试"
	@echo "  make backup     - 备份数据"
	@echo "  make restore    - 恢复数据"
	@echo ""

# 构建镜像
build:
	@echo "🔨 构建 AutoCrack Docker 镜像..."
	docker-compose build --no-cache

# 启动开发环境
start:
	@echo "🚀 启动 AutoCrack 开发环境..."
	docker-compose up -d
	@echo "✅ 服务已启动，访问 http://localhost"

# 停止服务
stop:
	@echo "🛑 停止 AutoCrack 服务..."
	docker-compose down

# 重启服务
restart:
	@echo "🔄 重启 AutoCrack 服务..."
	docker-compose restart

# 查看日志
logs:
	@echo "📋 查看 AutoCrack 服务日志..."
	docker-compose logs -f

# 清理资源
clean:
	@echo "🧹 清理 AutoCrack 资源..."
	docker-compose down -v
	docker system prune -f
	@echo "✅ 清理完成"

# 完整部署
deploy: build start
	@echo "🎉 AutoCrack 部署完成！"
	@echo "📡 API服务: http://localhost:5000"
	@echo "🌐 Web界面: http://localhost"

# 生产环境部署
deploy-prod:
	@echo "🚀 部署 AutoCrack 生产环境..."
	docker-compose -f docker-compose.prod.yml up -d --build
	@echo "✅ 生产环境部署完成"

# 运行测试
test:
	@echo "🧪 运行 API 测试..."
	python test_api.py

# 备份数据
backup:
	@echo "💾 备份 AutoCrack 数据..."
	docker run --rm \
		-v autocrack_autocrack-db:/data \
		-v $(PWD):/backup \
		alpine tar czf /backup/autocrack-backup-$(shell date +%Y%m%d-%H%M%S).tar.gz /data
	@echo "✅ 备份完成"

# 恢复数据
restore:
	@echo "🔄 恢复 AutoCrack 数据..."
	@echo "请指定备份文件: make restore FILE=backup-file.tar.gz"
	@if [ -z "$(FILE)" ]; then \
		echo "❌ 请指定备份文件"; \
		exit 1; \
	fi
	docker run --rm \
		-v autocrack_autocrack-db:/data \
		-v $(PWD):/backup \
		alpine tar xzf /backup/$(FILE) -C /
	@echo "✅ 恢复完成"

# 查看服务状态
status:
	@echo "📊 AutoCrack 服务状态:"
	docker-compose ps

# 进入后端容器
shell:
	@echo "🐚 进入 AutoCrack 后端容器..."
	docker-compose exec autocrack-backend /bin/bash

# 查看资源使用
stats:
	@echo "📈 容器资源使用情况:"
	docker stats --no-stream

# 更新镜像
update:
	@echo "🔄 更新 AutoCrack 镜像..."
	docker-compose pull
	docker-compose up -d

# 扩展后端服务
scale:
	@echo "📈 扩展后端服务..."
	@if [ -z "$(REPLICAS)" ]; then \
		echo "使用方法: make scale REPLICAS=3"; \
		exit 1; \
	fi
	docker-compose up -d --scale autocrack-backend=$(REPLICAS)

# 健康检查
health:
	@echo "🩺 AutoCrack 健康检查..."
	@curl -f http://localhost:5000/api/health > /dev/null 2>&1 && \
		echo "✅ 后端服务正常" || \
		echo "❌ 后端服务异常"
	@curl -f http://localhost/health > /dev/null 2>&1 && \
		echo "✅ 代理服务正常" || \
		echo "❌ 代理服务异常"