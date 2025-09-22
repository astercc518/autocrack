# 🐳 AutoCrack Docker 部署指南

## 概述

AutoCrack 支持完整的 Docker 化部署，提供开箱即用的一键部署方案。支持开发环境、生产环境和 Kubernetes 集群部署。

## 🚀 快速开始

### 1. 环境准备

确保您的系统已安装：
- **Docker** 20.10 或更高版本
- **Docker Compose** 2.0 或更高版本

### 2. 一键部署

#### Windows 用户
```cmd
# 下载项目后，直接运行
deploy.bat

# 或者手动执行
docker-compose up -d
```

#### Linux/macOS 用户
```bash
# 给脚本执行权限
chmod +x deploy.sh

# 一键部署
./deploy.sh

# 或者手动执行
docker-compose up -d
```

### 3. 访问服务

部署完成后，可以通过以下地址访问：

- **🌐 Web界面**: http://localhost
- **📡 API服务**: http://localhost:5000
- **📚 API文档**: http://localhost:5000/api/health
- **💾 Redis服务**: localhost:6379

## 📋 服务架构

### 开发环境 (`docker-compose.yml`)

```yaml
services:
  - autocrack-backend  # Flask API 服务
  - redis             # 缓存和任务队列
  - nginx             # 反向代理 (可选)
```

### 生产环境 (`docker-compose.prod.yml`)

```yaml
services:
  - autocrack-backend  # Flask API 服务 (多实例)
  - postgres          # PostgreSQL 数据库
  - redis             # Redis 缓存 (密码保护)
  - nginx             # Nginx 反向代理 (SSL)
  - prometheus        # 监控服务
  - grafana           # 数据可视化
```

## 🔧 配置说明

### 环境变量

可以通过环境变量自定义配置：

```bash
# 数据库配置
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port/db

# 应用配置
FLASK_ENV=production
SECRET_KEY=your-secret-key
MAX_THREADS=50
RATE_LIMIT_ENABLED=true
```

### 数据持久化

Docker 部署自动配置数据持久化：

```yaml
volumes:
  - ./data:/app/data          # 应用数据
  - ./logs:/app/logs          # 日志文件
  - autocrack-db:/app/database # 数据库文件
  - redis-data:/data          # Redis 数据
```

### 端口映射

默认端口配置：

| 服务 | 容器端口 | 主机端口 | 说明 |
|------|----------|----------|------|
| Backend | 5000 | 5000 | API 服务 |
| Nginx | 80/443 | 80/443 | Web 代理 |
| Redis | 6379 | 6379 | 缓存服务 |
| PostgreSQL | 5432 | - | 数据库 (内部) |
| Prometheus | 9090 | 9090 | 监控 (生产) |
| Grafana | 3000 | 3000 | 可视化 (生产) |

## 🛠️ 管理命令

### 基础操作

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看实时日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f autocrack-backend

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

### 生产环境管理

```bash
# 使用生产配置启动
docker-compose -f docker-compose.prod.yml up -d

# 扩展后端服务实例
docker-compose -f docker-compose.prod.yml up -d --scale autocrack-backend=3

# 更新服务
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

### 备份和恢复

```bash
# 备份数据
docker run --rm -v autocrack_autocrack-db:/data -v $(pwd):/backup alpine tar czf /backup/autocrack-backup.tar.gz /data

# 恢复数据
docker run --rm -v autocrack_autocrack-db:/data -v $(pwd):/backup alpine tar xzf /backup/autocrack-backup.tar.gz -C /
```

## 🔍 监控和调试

### 健康检查

所有服务都配置了健康检查：

```bash
# 检查后端服务健康状态
curl http://localhost:5000/api/health

# 检查 Nginx 代理
curl http://localhost/health

# 查看 Docker 容器健康状态
docker ps
```

### 日志分析

```bash
# 查看错误日志
docker-compose logs --tail=100 autocrack-backend | grep ERROR

# 监控资源使用
docker stats

# 查看容器详细信息
docker inspect autocrack-backend
```

### 性能监控

生产环境包含完整的监控栈：

- **Prometheus**: http://localhost:9090 - 指标收集
- **Grafana**: http://localhost:3000 - 数据可视化
  - 默认用户名/密码: admin/admin_password

## 🚀 Kubernetes 部署

### 前提条件

- Kubernetes 集群 (1.16+)
- kubectl 已配置

### 部署步骤

```bash
# 1. 创建命名空间和应用
kubectl apply -f k8s-deployment.yaml

# 2. 查看部署状态
kubectl get pods -n autocrack

# 3. 查看服务状态
kubectl get svc -n autocrack

# 4. 配置域名访问 (可选)
echo "127.0.0.1 autocrack.local" >> /etc/hosts
```

### 扩展和更新

```bash
# 扩展后端服务
kubectl scale deployment autocrack-backend --replicas=5 -n autocrack

# 滚动更新
kubectl set image deployment/autocrack-backend autocrack-backend=autocrack:v2.0 -n autocrack

# 查看更新状态
kubectl rollout status deployment/autocrack-backend -n autocrack
```

## 🛡️ 安全配置

### 生产环境安全

1. **密码安全**
   ```bash
   # 修改默认密码
   export POSTGRES_PASSWORD=$(openssl rand -base64 32)
   export REDIS_PASSWORD=$(openssl rand -base64 32)
   export SECRET_KEY=$(openssl rand -base64 32)
   ```

2. **SSL 证书**
   ```bash
   # 将 SSL 证书放入 nginx/ssl/ 目录
   mkdir -p nginx/ssl
   cp your-cert.pem nginx/ssl/cert.pem
   cp your-key.pem nginx/ssl/key.pem
   ```

3. **网络隔离**
   - 所有服务运行在独立的 Docker 网络中
   - 只暴露必要的端口
   - 数据库服务不对外暴露

### 防火墙配置

```bash
# 仅允许必要端口
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw allow 5000/tcp  # API (可选)
```

## 🔧 故障排除

### 常见问题

1. **服务启动失败**
   ```bash
   # 检查容器日志
   docker-compose logs autocrack-backend
   
   # 检查端口占用
   netstat -tulpn | grep :5000
   ```

2. **数据库连接失败**
   ```bash
   # 检查数据库状态
   docker-compose exec postgres pg_isready
   
   # 重置数据库
   docker-compose down -v
   docker-compose up -d
   ```

3. **内存不足**
   ```bash
   # 限制容器资源使用
   docker-compose --compatibility up -d
   ```

### 性能优化

1. **调整资源限制**
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '2.0'
         memory: 2G
   ```

2. **启用缓存**
   ```bash
   # Redis 持久化配置
   docker-compose exec redis redis-cli CONFIG SET save "60 1000"
   ```

## 📞 技术支持

如遇问题，请按以下步骤排查：

1. 查看服务日志: `docker-compose logs -f`
2. 检查服务状态: `docker-compose ps`
3. 验证配置文件: `docker-compose config`
4. 重启服务: `docker-compose restart`

---

**部署完成后，您可以立即开始使用 AutoCrack 进行安全测试！** 🎉