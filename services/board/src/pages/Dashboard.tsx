import { useQuery } from '@tanstack/react-query'
import { runsApi } from '../api/runs'
import { projectsApi } from '../api/projects'
import './Dashboard.css'

export default function Dashboard() {
  const { data: runs, isLoading: runsLoading } = useQuery({
    queryKey: ['runs', { limit: 20 }],
    queryFn: () => runsApi.list({ limit: 20 }),
  })

  const { data: projects, isLoading: projectsLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: () => projectsApi.list(),
  })

  if (runsLoading || projectsLoading) {
    return <div className="loading">Loading...</div>
  }

  const recentRuns = runs?.slice(0, 10) || []
  const stats = {
    total: runs?.length || 0,
    passed: runs?.filter((r) => r.status === 'completed').length || 0,
    failed: runs?.filter((r) => r.status === 'failed').length || 0,
    running: runs?.filter((r) => r.status === 'running').length || 0,
  }

  return (
    <div className="dashboard">
      <h1>Dashboard</h1>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{stats.total}</div>
          <div className="stat-label">Total Runs</div>
        </div>
        <div className="stat-card success">
          <div className="stat-value">{stats.passed}</div>
          <div className="stat-label">Passed</div>
        </div>
        <div className="stat-card error">
          <div className="stat-value">{stats.failed}</div>
          <div className="stat-label">Failed</div>
        </div>
        <div className="stat-card warning">
          <div className="stat-value">{stats.running}</div>
          <div className="stat-label">Running</div>
        </div>
      </div>

      <div className="dashboard-section">
        <h2>Recent Runs</h2>
        <table className="runs-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Status</th>
              <th>Project</th>
              <th>Branch</th>
              <th>Tests</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            {recentRuns.map((run) => (
              <tr key={run.id}>
                <td>{run.id}</td>
                <td>
                  <span className={`status-badge status-${run.status}`}>
                    {run.status}
                  </span>
                </td>
                <td>{run.project_id}</td>
                <td>{run.branch || 'N/A'}</td>
                <td>
                  {run.passed_tests}/{run.total_tests}
                </td>
                <td>{new Date(run.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="dashboard-section">
        <h2>Projects</h2>
        <div className="projects-grid">
          {projects?.map((project) => (
            <div key={project.id} className="project-card">
              <h3>{project.name}</h3>
              <p>{project.description || 'No description'}</p>
              <div className="project-meta">
                <span>Repo: {project.repo_url}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
