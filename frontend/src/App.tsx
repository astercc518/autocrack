// AutoCrack 前端应用
// 请先安装依赖: npm install

const App = () => {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      padding: '20px',
      fontFamily: 'Arial, sans-serif',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    }}>
      <div style={{
        background: 'white',
        padding: '40px',
        borderRadius: '10px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        maxWidth: '600px',
        textAlign: 'center'
      }}>
        <h1 style={{ color: '#333', marginBottom: '20px' }}>
          🚀 AutoCrack 自动化撞库工具
        </h1>
        
        <div style={{ marginBottom: '30px' }}>
          <h3 style={{ color: '#666' }}>🌟 功能特性</h3>
          <ul style={{ textAlign: 'left', color: '#555' }}>
            <li>✅ Web界面操作 - 现代化React前端界面</li>
            <li>✅ 批量目标管理 - 支持导入和管理多个目标站点</li>
            <li>✅ 智能代理池 - 自动IP切换和代理管理</li>
            <li>✅ 多线程并发 - 高性能撞库引擎</li>
            <li>✅ 实时监控 - WebSocket实时进度跟踪</li>
            <li>✅ 结果导出 - 多格式结果导出功能</li>
          </ul>
        </div>

        <div style={{ marginBottom: '30px' }}>
          <h3 style={{ color: '#666' }}>🔧 技术架构</h3>
          <div style={{ display: 'flex', justifyContent: 'space-around', flexWrap: 'wrap' }}>
            <div style={{ margin: '10px', padding: '10px', background: '#f5f5f5', borderRadius: '5px' }}>
              <strong>后端</strong><br/>
              Python Flask + SQLAlchemy + Redis
            </div>
            <div style={{ margin: '10px', padding: '10px', background: '#f5f5f5', borderRadius: '5px' }}>
              <strong>前端</strong><br/>
              React 18 + TypeScript + Ant Design
            </div>
            <div style={{ margin: '10px', padding: '10px', background: '#f5f5f5', borderRadius: '5px' }}>
              <strong>部署</strong><br/>
              Docker + Docker Compose + Kubernetes
            </div>
          </div>
        </div>

        <div style={{ marginBottom: '30px' }}>
          <h3 style={{ color: '#666' }}>🚀 快速开始</h3>
          <div style={{ textAlign: 'left', background: '#f8f9fa', padding: '15px', borderRadius: '5px', fontFamily: 'monospace' }}>
            <div># Docker一键部署</div>
            <div>docker-compose up -d</div>
            <br/>
            <div># 或使用部署脚本</div>
            <div>deploy.bat  # Windows</div>
            <div>./deploy.sh # Linux/macOS</div>
          </div>
        </div>

        <div style={{ padding: '15px', background: '#fff3cd', borderRadius: '5px', marginBottom: '20px' }}>
          <strong>⚠️ 重要提醒</strong><br/>
          本工具仅供安全研究和授权渗透测试使用，请勿用于非法活动。
        </div>

        <div style={{ marginTop: '20px' }}>
          <a 
            href="/api/health" 
            target="_blank" 
            style={{
              display: 'inline-block',
              padding: '10px 20px',
              background: '#007bff',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '5px',
              margin: '0 10px'
            }}
          >
            📊 检查API状态
          </a>
          <a 
            href="https://github.com/astercc518/autocrack" 
            target="_blank" 
            style={{
              display: 'inline-block',
              padding: '10px 20px',
              background: '#28a745',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '5px',
              margin: '0 10px'
            }}
          >
            💾 GitHub仓库
          </a>
        </div>
      </div>

      <div style={{
        marginTop: '20px',
        color: 'white',
        textAlign: 'center'
      }}>
        <p>📚 详细文档请查看 GitHub README.md</p>
        <p>🌟 如果对您有帮助，请给个星标！</p>
      </div>
    </div>
  );
};

export default App;