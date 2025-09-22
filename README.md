# AutoCrack - 自动化撞库工具 🔐

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![React](https://img.shields.io/badge/react-%2320232a.svg?style=flat&logo=react&logoColor=%2361DAFB)](https://reactjs.org/)

## 📋 项目简介

AutoCrack是一个基于Sentinel、Snipr、Hydra项目理念开发的现代化自动化撞库工具。它提供了完整的Web操作界面，支持批量导入目标站点和撞库数据，并具备智能代理池管理和IP自动切换功能。

⚠️ **免责声明：本工具仅供安全研究和授权渗透测试使用，请勿用于非法活动。使用者需自行承担相关法律责任。**

## ✨ 核心功能

### 🎯 目标站点管理
- **批量导入**：支持多种格式的目标站点批量导入
- **智能分类**：自动识别和分类不同类型的登录接口
- **状态监控**：实时监控目标站点的可用性和响应状态

### 🔄 智能代理系统
- **代理池管理**：支持HTTP/HTTPS/SOCKS5多种代理协议
- **自动轮换**：智能IP轮换机制，避免频率限制
- **健康检测**：实时检测代理有效性，自动剔除失效代理
- **负载均衡**：支持多种负载均衡策略

### ⚡ 高性能攻击引擎
- **多线程并发**：支持高并发撞库，可自定义线程数
- **多种攻击模式**：
  - 组合字典模式：用户名密码分别指定
  - 分离字典模式：独立的用户名和密码字典
- **智能重试**：支持失败重试和超时处理
- **结果导出**：支持多种格式的结果导出

### 📊 实时监控
- **WebSocket实时通信**：实时获取攻击进度和结果
- **详细统计**：成功率、失败率、进度统计
- **日志记录**：完整的操作日志和错误记录

### 🌐 现代化Web界面
- **响应式设计**：支持桌面端和移动端访问
- **直观操作**：友好的用户界面，操作简单直观
- **数据可视化**：图表展示攻击进度和结果统计

## 🏗️ 技术架构

### 后端技术栈
- **框架**：Python Flask + SQLAlchemy
- **数据库**：SQLite（开发）/ PostgreSQL（生产）
- **缓存**：Redis
- **异步通信**：WebSocket
- **并发处理**：多线程 + 异步处理

### 前端技术栈
- **框架**：React 18 + TypeScript
- **UI组件**：Ant Design
- **状态管理**：React Hooks
- **HTTP客户端**：Axios
- **实时通信**：Socket.IO

### 部署架构
- **容器化**：Docker + Docker Compose
- **负载均衡**：Nginx
- **集群部署**：Kubernetes支持
- **监控**：Prometheus + Grafana（生产环境）

## 🚀 快速开始

### 方式一：Docker一键部署（推荐）

#### 前置要求
- Docker 20.10+
- Docker Compose 2.0+

#### 开发环境部署
```bash
# 克隆项目
git clone https://github.com/astercc518/autocrack.git
cd autocrack

# 启动开发环境
docker-compose up -d

# 验证部署
./verify.sh  # Linux/macOS
verify.bat   # Windows
```

#### 生产环境部署
```bash
# 使用生产配置启动
docker-compose -f docker-compose.prod.yml up -d

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f
```

### 方式二：便捷脚本部署

#### Windows
```cmd
# 运行部署脚本
deploy.bat

# 验证部署
verify.bat
```

#### Linux/macOS
```bash
# 赋予执行权限
chmod +x deploy.sh verify.sh

# 运行部署脚本
./deploy.sh

# 验证部署
./verify.sh
```

### 方式三：手动安装

#### 后端部署
```bash
# 安装Python依赖
pip install -r requirements.txt

# 初始化数据库
python -c "from backend.app import app, db; app.app_context().push(); db.create_all()"

# 启动后端服务
python backend/app.py
```

#### 前端部署
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm start

# 构建生产版本
npm run build
```

## 📖 使用指南

### 1. 访问Web界面
- 开发环境：http://localhost:3000
- 生产环境：http://localhost（或您的域名）

### 2. 目标站点管理
1. 点击"目标站点管理"
2. 选择"批量导入"或"手动添加"
3. 配置目标站点信息（URL、请求方法、参数等）

### 3. 配置代理池
1. 进入"代理设置"页面
2. 批量导入代理列表
3. 配置代理轮换策略

### 4. 导入撞库数据
1. 选择攻击模式（组合字典/分离字典）
2. 上传用户名和密码字典文件
3. 配置攻击参数

### 5. 开始攻击
1. 选择目标站点
2. 配置并发数和超时时间
3. 点击"开始攻击"按钮
4. 实时查看攻击进度和结果

### 6. 结果导出
- 支持导出为CSV、JSON、TXT格式
- 可筛选成功/失败结果
- 包含详细的时间戳和响应信息

## 🔧 配置说明

### 环境变量配置
```env
# 数据库配置
DATABASE_URL=sqlite:///autocrack.db
REDIS_URL=redis://localhost:6379/0

# Flask配置
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# 代理配置
DEFAULT_TIMEOUT=30
MAX_RETRIES=3
CONCURRENT_LIMIT=100
```

### 高级配置
详细的配置选项请参考 [`USAGE.md`](USAGE.md) 文档。

## 📁 项目结构

```
autocrack/
├── backend/                 # 后端代码
│   ├── core/               # 核心功能模块
│   │   ├── attack_engine.py    # 攻击引擎
│   │   ├── proxy_manager.py    # 代理管理
│   │   └── target_manager.py   # 目标管理
│   ├── models/             # 数据模型
│   ├── routes/             # API路由
│   └── app.py              # 应用入口
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── components/     # React组件
│   │   ├── pages/          # 页面组件
│   │   └── services/       # API服务
│   └── package.json
├── data/                   # 数据目录
│   ├── dictionaries/       # 字典文件
│   ├── proxies/           # 代理列表
│   └── targets/           # 目标站点
├── nginx/                  # Nginx配置
├── docker-compose.yml      # 开发环境
├── docker-compose.prod.yml # 生产环境
├── k8s-deployment.yaml     # Kubernetes部署
└── README.md              # 项目说明
```

## 🔒 安全特性

- **请求头随机化**：避免指纹识别
- **速率限制**：防止过度请求
- **错误重试**：智能错误处理
- **日志审计**：完整的操作记录
- **权限控制**：基于角色的访问控制

## 🌟 性能优化

- **连接池**：复用HTTP连接，提高效率
- **缓存机制**：Redis缓存常用数据
- **异步处理**：非阻塞I/O操作
- **资源限制**：防止资源耗尽
- **监控告警**：Prometheus指标监控

## 📊 监控和日志

### 生产环境监控
- **Prometheus**：指标收集
- **Grafana**：可视化监控面板
- **日志聚合**：结构化日志输出

### 健康检查
```bash
# 检查服务健康状态
curl http://localhost:5000/health

# 检查Redis连接
curl http://localhost:5000/health/redis

# 检查数据库连接
curl http://localhost:5000/health/database
```

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证。详情请见 [LICENSE](LICENSE) 文件。

## ⚠️ 法律声明

本工具仅供安全研究和授权渗透测试使用。使用者必须：

1. 仅在获得明确授权的系统上使用
2. 遵守当地法律法规
3. 承担使用本工具的所有法律责任
4. 不得用于任何非法活动

作者不对任何滥用行为承担责任。

## 🆘 支持和帮助

- **问题反馈**：[GitHub Issues](https://github.com/your-username/autocrack/issues)
- **功能请求**：[GitHub Discussions](https://github.com/your-username/autocrack/discussions)
- **文档**：[项目Wiki](https://github.com/your-username/autocrack/wiki)

## 🎯 路线图

- [ ] 支持更多认证方式（OAuth、JWT等）
- [ ] 机器学习驱动的智能攻击策略
- [ ] 分布式攻击集群
- [ ] 可视化攻击流程图
- [ ] 移动端应用
- [ ] 更多导出格式支持

---

**⭐ 如果这个项目对您有帮助，请给我们一个星标！**