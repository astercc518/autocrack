# GitHub项目说明文档

## 项目概述

AutoCrack是一个现代化的自动化撞库工具，基于Sentinel、Snipr、Hydra等项目的理念开发。该项目提供了完整的Web操作界面，支持批量管理目标站点和撞库数据，具备智能代理池管理功能。

## 主要特性

### 🎯 核心功能
- **Web界面操作**：现代化的React前端界面
- **批量目标管理**：支持导入和管理多个目标站点
- **智能代理池**：自动IP切换和代理管理
- **多线程并发**：高性能撞库引擎
- **实时监控**：WebSocket实时进度跟踪
- **结果导出**：多格式结果导出功能

### 🔧 技术特点
- **前后端分离**：React + Flask架构
- **容器化部署**：Docker一键部署
- **数据持久化**：SQLite/PostgreSQL支持
- **缓存优化**：Redis缓存机制
- **生产就绪**：完整的生产环境配置

## 部署方式

### 1. Docker一键部署（推荐）
```bash
# 开发环境
docker-compose up -d

# 生产环境
docker-compose -f docker-compose.prod.yml up -d
```

### 2. 便捷脚本部署
```bash
# Windows
deploy.bat && start.bat

# Linux/macOS
./deploy.sh && ./start.sh
```

### 3. Kubernetes集群部署
```bash
kubectl apply -f k8s-deployment.yaml
```

## 安全说明

⚠️ **重要提醒**：
- 本工具仅供安全研究和授权渗透测试使用
- 使用前请确保已获得目标系统的明确授权
- 严禁用于任何非法活动
- 用户需承担使用本工具的全部法律责任

## 项目结构

```
autocrack/
├── backend/           # Python Flask后端
├── frontend/          # React前端
├── data/             # 数据文件目录
├── nginx/            # Nginx配置
├── docker-compose.yml # 开发环境配置
├── docker-compose.prod.yml # 生产环境配置
└── k8s-deployment.yaml # Kubernetes配置
```

## 快速开始

1. **克隆项目**
   ```bash
   git clone https://github.com/your-username/autocrack.git
   cd autocrack
   ```

2. **启动服务**
   ```bash
   docker-compose up -d
   ```

3. **访问界面**
   - 前端界面：http://localhost:3000
   - 后端API：http://localhost:5000

4. **基本使用**
   - 配置目标站点
   - 导入代理列表
   - 上传字典文件
   - 开始攻击任务
   - 查看结果统计

## 技术支持

- **文档**：详细使用说明请参考项目内的文档文件
- **问题反馈**：通过GitHub Issues提交问题
- **功能建议**：通过GitHub Discussions讨论新功能

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

---

**注意**：使用本工具前请仔细阅读法律免责声明，确保合法合规使用。