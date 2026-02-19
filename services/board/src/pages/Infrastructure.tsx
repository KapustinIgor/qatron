import './Infrastructure.css'

export default function Infrastructure() {
  return (
    <div className="infrastructure-page">
      <h1>Infrastructure</h1>
      <div className="infrastructure-grid">
        <div className="infra-card">
          <h3>Workers</h3>
          <div className="infra-stat">
            <span className="stat-value">0</span>
            <span className="stat-label">Ready</span>
          </div>
          <div className="infra-stat">
            <span className="stat-value">0</span>
            <span className="stat-label">Busy</span>
          </div>
        </div>
        <div className="infra-card">
          <h3>Queue</h3>
          <div className="infra-stat">
            <span className="stat-value">0</span>
            <span className="stat-label">Pending</span>
          </div>
        </div>
        <div className="infra-card">
          <h3>Selenium Grid</h3>
          <div className="infra-stat">
            <span className="stat-value">0</span>
            <span className="stat-label">Nodes</span>
          </div>
          <div className="infra-stat">
            <span className="stat-value">0</span>
            <span className="stat-label">Sessions</span>
          </div>
        </div>
      </div>
    </div>
  )
}
