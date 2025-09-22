# AutoCrack Docker镜像
FROM python:3.11-slim

LABEL maintainer="AutoCrack Team"
LABEL description="AutoCrack 自动化撞库工具"

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV FLASK_APP=backend/app.py
ENV FLASK_ENV=production

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .
COPY backend/ ./backend/
COPY data/ ./data/
COPY *.py ./

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 创建必要的目录
RUN mkdir -p /app/logs /app/uploads

# 设置权限
RUN chmod +x backend/app.py

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# 启动命令
CMD ["python", "backend/app.py"]