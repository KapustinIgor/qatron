import './Configuration.css'

export default function Configuration() {
  return (
    <div className="configuration-page">
      <h1>Configuration</h1>
      <div className="config-section">
        <h2>Project Settings</h2>
        <p>Configure project settings, suites, and environments.</p>
      </div>
      <div className="config-section">
        <h2>Integrations</h2>
        <p>Configure webhooks, Slack, Teams, and other integrations.</p>
      </div>
      <div className="config-section">
        <h2>Coverage Thresholds</h2>
        <p>Set coverage thresholds per layer.</p>
      </div>
    </div>
  )
}
