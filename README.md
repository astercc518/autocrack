# AutoCrack - 企业级自动化撞库安全测试平台 🔐

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![React](https://img.shields.io/badge/react-%2320232a.svg?style=flat&logo=react&logoColor=%2361DAFB)](https://reactjs.org/)
[![Security](https://img.shields.io/badge/security-enterprise-green.svg)]()
[![Multi-User](https://img.shields.io/badge/multi--user-RBAC-blue.svg)]()

## 📋 项目简介

AutoCrack是一个基于Sentinel、Snipr、Hydra项目理念开发的**企业级自动化撞库安全测试平台**。它不仅提供了完整的Web操作界面和批量攻击能力，更重要的是集成了**用户权限管理**、**数据清洗**、**智能分配**和**实时反馈**四大企业级功能模块，是支持团队协作的专业安全测试解决方案。

⚠️ **免责声明：本工具仅供安全研究和授权渗透测试使用，请勿用于非法活动。使用者需自行承担相关法律责任。**

## ✨ 核心功能

### 🔐 用户权限管理系统
- **RBAC权限控制**：基于角色的细粒度权限管理
- **JWT令牌认证**：安全的无状态认证机制
- **多级用户角色**：管理员、管理者、操作员、查看者
- **安全审计**：完整的登录日志和行为记录
- **账户安全**：密码加密、账户锁定、会话管理

### 🧹 数据清洗功能
- **多类型数据清洗**：URL、凭据、代理服务器数据清洗
- **智能去重处理**：基于哈希的重复数据检测
- **格式验证**：严格的数据格式校验和标准化
- **批量处理**：支持大量数据的高效清洗
- **统计分析**：详细的清洗统计和质量报告

### 📋 数据分配管理
- **智能任务分配**：基于负载均衡的自动分配
- **资源调度管理**：代理、目标、线程资源统一调度
- **任务队列系统**：多优先级任务队列管理
- **进度监控**：实时任务状态跟踪和进度显示
- **自动化管理**：智能的任务分配和资源优化

### 📊 数据反馈收集
- **实时反馈收集**：攻击结果的实时收集和处理
- **性能指标监控**：系统性能和效率指标跟踪
- **智能告警系统**：基于规则的自动告警机制
- **数据分析报告**：综合性性能分析和趋势报告
- **多维度统计**：成功率、响应时间、代理效率等全面统计

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

### 🎆 新增企业级功能

### 🔐 用户权限管理
- **JWT令牌认证**：无状态安全认证
- **角色权限控制**：管理员、管理者、操作员、查看者
- **细粒度权限**：18种不同类型的权限控制
- **安全审计**：登录日志和行为跟踪

### 🧹 数据清洗系统
- **多类型数据**：URL、凭据、代理服务器清洗
- **智能去重**：基于哈希的高效去重算法
- **格式验证**：严格的数据格式校验和标准化
- **批量处理**：支持大量数据的高效处理

### 📋 数据分配管理
- **智能任务分配**：自动化任务分配和资源调度
- **负载均衡**：动态负载检测和任务重分配
- **任务队列**：多优先级任务队列管理
- **进度监控**：实时任务状态和进度跟踪

### 📊 数据反馈收集
- **实时反馈**：攻击结果的实时收集和分析
- **性能监控**：全面的系统性能监控和指标跟踪
- **智能告警**：基于规则的自动告警系统
- **数据分析**：多维度数据分析和趋势报告

### 📝 API接口
- **用户认证**：`/api/auth/*` - 登录、注册、权限管理
- **数据清洗**：`/api/data-clean/*` - 数据清洗和验证
- **任务分配**：`/api/data-distribution/*` - 任务管理和资源调度
- **反馈收集**：`/api/data-feedback/*` - 结果反馈和分析

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

### 1. 初始登录
- 管理员账户：`admin` / `admin123`
- 登录后请立即修改默认密码

### 2. 用户管理
1. 使用管理员账户登录
2. 進入“用户管理”页面
3. 创建不同角色的用户账户
4. 分配相应的权限和角色

### 3. 数据清洗
1. 选择“数据清洗”功能
2. 上传需要清洗的数据文件
3. 选择数据类型（URL/凭据/代理）
4. 查看清洗结果和统计报告

### 4. 任务分配
1. 创建新的分配任务
2. 配置任务参数和资源需求
3. 选择手动分配或自动分配
4. 监控任务执行进度

5. 选择目标站点
1. 点击“目标站点管理”
2. 选择“批量导入”或“手动添加”
3. 配置目标站点信息（URL、请求方法、参数等）

### 6. 配置代理池
1. 进入“代理设置”页面
2. 批量导入代理列表
3. 配置代理轮换策略

### 7. 导入撞库数据
1. 选择攻击模式（组合字典/分离字典）
2. 上传用户名和密码字典文件
3. 配置攻击参数

### 8. 开始攻击
1. 选择目标站点
2. 配置并发数和超时时间
3. 点击“开始攻击”按钮
4. 实时查看攻击进度和结果

### 9. 结果导出
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
│   │   ├── user.py             # 用户权限模型
│   │   ├── distribution.py     # 数据分配模型
│   │   ├── feedback.py         # 反馈收集模型
│   │   ├── target.py           # 目标站点模型
│   │   └── proxy.py            # 代理模型
│   ├── api/                # API接口
│   │   ├── auth.py             # 认证接口
│   │   ├── data_cleaning.py    # 数据清洗接口
│   │   ├── data_distribution.py # 数据分配接口
│   │   ├── data_feedback.py    # 反馈收集接口
│   │   ├── targets.py          # 目标管理接口
│   │   └── proxies.py          # 代理管理接口
│   ├── utils/              # 工具函数
│   │   ├── validators.py       # 数据验证
│   │   ├── data_cleaner.py     # 数据清洗工具
│   │   ├── task_distributor.py # 任务分配器
│   │   └── feedback_manager.py # 反馈管理器
│   ├── scripts/            # 脚本工具
│   │   └── init_new_features.py # 新功能初始化
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
├── docs/                   # 项目文档
│   ├── NEW_FEATURES_SUMMARY.md # 新功能说明
│   └── USAGE.md           # 使用指南
├── nginx/                  # Nginx配置
├── docker-compose.yml      # 开发环境
├── docker-compose.prod.yml # 生产环境
├── k8s-deployment.yaml     # Kubernetes部署
└── README.md              # 项目说明
```

## 🏢 企业级特性

### 🔒 安全特性
- **多用户支持**：支持多用户同时使用，账户隔离
- **权限细分**：18种不同的权限类型，支持精细化控制
- **安全审计**：完整的操作日志和安全记录
- **请求头随机化**：避免指纹识别
- **速率限制**：防止过度请求
- **错误重试**：智能错误处理

### 📊 数据管理
- **数据质量保障**：智能数据清洗提高攻击数据质量
- **实时监控**：全方位的性能监控和数据分析
- **自动化分配**：智能资源调度和任务分配
- **统计分析**：多维度数据统计和趋势分析

### 🌐 系统架构
- **微服务架构**：模块化设计，易于扩展和维护
- **容器化部署**：Docker + Kubernetes支持
- **分布式支持**：支持集群部署和水平扩展
- **API标准化**：RESTful API设计，便于集成

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

### ✅ 已完成功能
- [x] 基础撞库功能
- [x] 目标站点管理
- [x] 代理池管理
- [x] 数据导入导出
- [x] Web界面操作
- [x] 🆕 **用户权限管理系统**
- [x] 🆕 **数据清洗功能**
- [x] 🆕 **数据分配管理**
- [x] 🆕 **数据反馈收集**
- [x] Docker一键部署
- [x] 企业级安全特性

### 📋 计划中功能
- [ ] 支持更多认证方式（OAuth、SAML等）
- [ ] 机器学习驱动的智能攻击策略
- [ ] 分布式攻击集群
- [ ] 可视化攻击流程图
- [ ] 移动端应用
- [ ] 更多导出格式支持
- [ ] AI驱动的漏洞发现

---

**⭐ 如果这个项目对您有帮助，请给我们一个星标！**