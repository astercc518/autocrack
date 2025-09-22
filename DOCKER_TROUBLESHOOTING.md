# Docker 构建问题解决方案

## 🐛 问题说明

您遇到的错误是Docker构建时无法找到`data/`目录，这通常是由以下原因造成的：

## 🔧 解决方案

### 1. 确保Docker Desktop正在运行
```bash
# Windows: 启动Docker Desktop应用程序
# 或通过命令行检查Docker状态
docker version
```

### 2. 修复Dockerfile（已修复）
已经更新了Dockerfile，采用更安全的方式处理data目录复制：

```dockerfile
# 先创建目录，再复制内容
RUN mkdir -p /app/data /app/logs /app/uploads
COPY data/ ./data/
```

### 3. 确保目录权限正确
```bash
# Linux/macOS
chmod -R 755 data/

# Windows (PowerShell管理员模式)
icacls data /grant Everyone:F /T
```

### 4. 检查.dockerignore文件
已创建.dockerignore文件来排除不需要的文件，避免构建冲突。

### 5. 重新构建Docker镜像
```bash
# 清理Docker缓存
docker system prune -f

# 重新构建
docker-compose build --no-cache autocrack-backend

# 或者使用部署脚本
./deploy.sh build  # Linux/macOS
deploy.bat build   # Windows
```

## 🚀 完整部署流程

### 方法1: 使用部署脚本（推荐）
```bash
# Windows
deploy.bat

# Linux/macOS
chmod +x deploy.sh
./deploy.sh
```

### 方法2: 手动Docker部署
```bash
# 1. 启动Docker Desktop
# 2. 清理缓存
docker system prune -f

# 3. 构建镜像
docker-compose build --no-cache

# 4. 启动服务
docker-compose up -d

# 5. 检查状态
docker-compose ps
```

### 方法3: 如果Docker问题仍然存在
如果Docker构建仍有问题，可以使用Python直接运行：

```bash
# 1. 安装Python依赖
pip install -r requirements.txt

# 2. 启动Redis（可选）
# 使用WSL或独立安装Redis

# 3. 启动后端服务
cd backend
python app.py

# 4. 启动前端服务（另一个终端）
cd frontend
npm install
npm start
```

## 📋 验证部署

部署成功后，检查以下服务：

- 🌐 后端API: http://localhost:5000/api/health
- 🖥️ 前端界面: http://localhost:3000
- 📊 服务状态: `docker-compose ps`

## 🆘 常见问题

### Q: Docker Desktop未启动
**A**: 启动Docker Desktop应用程序，等待其完全启动

### Q: 权限问题
**A**: 以管理员身份运行命令行工具

### Q: 端口占用
**A**: 检查端口5000和3000是否被占用，可在docker-compose.yml中修改端口

### Q: 构建缓存问题
**A**: 使用`--no-cache`参数重新构建

## 📞 获取帮助

如果问题仍然存在，请：
1. 检查Docker Desktop版本（建议4.0+）
2. 查看完整的错误日志
3. 确认系统环境（Windows版本、Docker版本等）
4. 在GitHub项目中提交Issue