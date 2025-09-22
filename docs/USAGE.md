# AutoCrack 使用说明

## 📋 项目简介

AutoCrack 是一个基于Sentinel、Snipr、Hydra等工具设计理念的自动化撞库工具，支持Web界面操作、批量导入目标站和撞库数据、代理池自动切换IP等功能。

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Node.js 14+ (可选，用于Web界面)
- 操作系统：Windows/Linux/macOS

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd AutoCrack
```

2. **安装Python依赖**
```bash
pip install -r requirements.txt
```

3. **安装前端依赖（可选）**
```bash
cd frontend
npm install
cd ..
```

4. **启动服务**

Windows:
```cmd
start.bat
```

Linux/macOS:
```bash
chmod +x start.sh
./start.sh
```

## 📚 功能介绍

### 1. 目标站点管理
- 支持批量导入目标站点
- 可配置登录URL、表单字段、成功/失败标识符
- 支持自定义请求头和Cookie

### 2. 攻击任务管理
- 支持组合字典和分离字典两种模式
- 可配置线程数、请求间隔、超时时间
- 实时监控攻击进度和成功率

### 3. 代理池管理
- 支持HTTP/HTTPS/SOCKS4/SOCKS5代理
- 自动验证代理可用性
- 支持代理轮换和负载均衡

### 4. 数据导入功能
- 支持TXT/CSV/JSON格式文件导入
- 批量导入目标站点和代理服务器
- 支持多种字典格式

## 🔧 API使用

### 基础URL
```
http://localhost:5000/api
```

### 主要接口

#### 目标站点管理
- `GET /targets` - 获取所有目标站点
- `POST /targets` - 创建新目标站点
- `PUT /targets/{id}` - 更新目标站点
- `DELETE /targets/{id}` - 删除目标站点

#### 攻击任务管理
- `GET /attacks` - 获取所有攻击任务
- `POST /attacks` - 创建新攻击任务
- `POST /attacks/{id}/start` - 启动攻击任务
- `POST /attacks/{id}/stop` - 停止攻击任务
- `GET /attacks/{id}/results` - 获取攻击结果

#### 代理池管理
- `GET /proxies` - 获取所有代理
- `POST /proxies` - 添加新代理
- `POST /proxies/batch` - 批量导入代理
- `POST /proxies/{id}/test` - 测试单个代理

#### 数据导入
- `POST /import/targets` - 导入目标站点
- `POST /import/proxies` - 导入代理服务器
- `POST /import/wordlists` - 导入字典文件

## 📝 配置说明

### 目标站点配置示例

```json
{
  "name": "示例网站",
  "url": "https://example.com",
  "login_url": "https://example.com/login",
  "method": "POST",
  "username_field": "username",
  "password_field": "password",
  "additional_fields": {
    "csrf_token": ""
  },
  "success_indicators": ["dashboard", "welcome"],
  "failure_indicators": ["error", "invalid"],
  "headers": {
    "User-Agent": "Custom Agent"
  },
  "timeout": 30
}
```

### 代理配置示例

```json
{
  "host": "127.0.0.1",
  "port": 8080,
  "proxy_type": "http",
  "username": "",
  "password": "",
  "country": "CN"
}
```

### 攻击任务配置示例

```json
{
  "name": "网站撞库测试",
  "target_id": 1,
  "wordlist_type": "combo",
  "combo_list": "admin:admin\\nroot:123456",
  "threads": 10,
  "delay": 0.1,
  "timeout": 30,
  "use_proxy": true,
  "proxy_rotation": true
}
```

## 📊 数据格式

### 目标站点导入格式（TXT）
```
网站名称	URL	登录URL
示例网站A	https://example1.com	https://example1.com/login
示例网站B	https://example2.com	https://example2.com/signin
```

### 代理导入格式（TXT）
```
127.0.0.1:8080
192.168.1.100:3128
proxy.example.com:8000:username:password
socks5://proxy.example.com:1080
```

### 组合字典格式（TXT）
```
admin:admin
admin:123456
root:root
user:password
```

## ⚠️ 安全提醒

- 本工具仅供安全研究和授权渗透测试使用
- 请确保拥有目标系统的合法授权
- 使用者需遵守当地法律法规
- 作者不承担任何法律责任

## 🐛 问题排查

### 常见问题

1. **后端启动失败**
   - 检查Python版本是否符合要求
   - 确认所有依赖包已正确安装
   - 检查端口5000是否被占用

2. **前端无法访问**
   - 确认Node.js已正确安装
   - 检查端口3000是否被占用
   - 确认后端服务已启动

3. **代理无法使用**
   - 验证代理服务器地址和端口
   - 检查网络连接
   - 确认代理类型设置正确

4. **攻击无响应**
   - 检查目标站点配置
   - 验证字典文件格式
   - 确认网络连接正常

## 📞 技术支持

如遇到问题，请检查：
1. 日志文件 `autocrack.log`
2. 控制台错误信息
3. 网络连接状态

## 📄 更新日志

### v1.0.0
- 初始版本发布
- 支持基础撞库功能
- 支持代理池管理
- 支持Web界面操作
- 支持批量数据导入

## 🔄 后续计划

- [ ] 支持更多认证方式
- [ ] 增加验证码识别
- [ ] 支持分布式部署
- [ ] 增加结果导出功能
- [ ] 优化性能和稳定性