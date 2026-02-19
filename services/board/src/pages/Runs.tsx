import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link, useSearchParams } from 'react-router-dom'
import { runsApi, RunFilters } from '../api/runs'
import { getErrorMessage } from '../types'
import './Runs.css'

export default function Runs() {
  const [searchParams] = useSearchParams()
  const projectIdParam = searchParams.get('project_id')
  
  const [filters, setFilters] = useState<RunFilters>({
    status: '',
    branch: '',
    project_id: projectIdParam ? parseInt(projectIdParam, 10) : undefined,
  })

  useEffect(() => {
    if (projectIdParam) {
      setFilters((prev) => ({
        ...prev,
        project_id: parseInt(projectIdParam, 10),
      }))
    }
  }, [projectIdParam])

  const queryClient = useQueryClient()
  const { data: runs, isLoading } = useQuery({
    queryKey: ['runs', filters],
    queryFn: () => runsApi.list(filters),
  })

  const triggerMutation = useMutation<
    { message: string; run_id: number },
    unknown,
    number
  >({
    mutationFn: (runId: number) => runsApi.trigger(runId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['runs'] })
    },
  })

  // mutation.error is typed any by @tanstack/react-query when TError is generic
  const triggerErr = triggerMutation.error as unknown
  const triggerErrorDetail = triggerErr
    ? getErrorMessage(triggerErr, 'Trigger failed')
    : ''

  if (isLoading) {
    return <div className="loading">Loading runs...</div>
  }

  return (
    <div className="runs-page">
      <div className="page-header">
        <h1>Test Runs</h1>
        <Link to="/runs/new" className="btn-primary">
          New Run
        </Link>
      </div>

      {triggerErrorDetail && (
        <div className="runs-trigger-error" role="alert">
          Trigger failed: {triggerErrorDetail}
        </div>
      )}

      <div className="filters">
        {filters.project_id && (
          <div className="filter-info">
            Filtered by Project ID: {filters.project_id}
            <button
              onClick={() => {
                setFilters({ ...filters, project_id: undefined })
                window.history.replaceState({}, '', '/runs')
              }}
              className="btn-clear-filter"
            >
              Clear
            </button>
          </div>
        )}
        <div className="filters-row">
          <select
            value={filters.status || ''}
            onChange={(e) => setFilters({ ...filters, status: e.target.value || undefined })}
          >
            <option value="">All Status</option>
            <option value="queued">Queued</option>
            <option value="running">Running</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
          </select>
          <input
            type="text"
            placeholder="Branch"
            value={filters.branch || ''}
            onChange={(e) => setFilters({ ...filters, branch: e.target.value || undefined })}
          />
        </div>
      </div>

      {!runs?.length ? (
        <div className="runs-empty-state">
          <p className="runs-empty-title">No runs yet</p>
          <p className="runs-empty-text">
            Test runs will appear here when you create them. You can trigger a run via the API
            or from your CI pipeline; once a run exists, you’ll see its status (queued, running,
            completed, failed) and can open it for details.
          </p>
          <p className="runs-empty-hint">
            To create a run via API: <code>POST /api/v1/runs</code> with{" "}
            <code>project_id</code>, <code>suite_id</code>, and <code>environment_id</code>.
          </p>
        </div>
      ) : (
        <table className="runs-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Status</th>
              <th>Project</th>
              <th>Suite</th>
              <th>Branch</th>
              <th>Tests</th>
              <th>Duration</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {runs.map((run) => (
              <tr key={run.id}>
                <td>{run.id}</td>
                <td>
                  <span className={`status-badge status-${run.status}`}>
                    {run.status}
                  </span>
                </td>
                <td>{run.project_id}</td>
                <td>{run.suite_id}</td>
                <td>{run.branch || 'N/A'}</td>
                <td>
                  {run.passed_tests}/{run.total_tests}
                </td>
                <td>
                  {run.duration_seconds ? `${run.duration_seconds}s` : 'N/A'}
                </td>
              <td>{new Date(run.created_at).toLocaleString()}</td>
              <td>
                {run.status === 'queued' && (
                  <button
                    type="button"
                    className="btn-trigger"
                    onClick={() => triggerMutation.mutate(run.id)}
                    disabled={triggerMutation.isPending}
                  >
                    {triggerMutation.isPending ? 'Triggering...' : 'Trigger'}
                  </button>
                )}
                <Link to={`/runs/${run.id}`} className="link">
                  View
                </Link>
              </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {runs?.some((r) => r.status === 'queued') && (
        <p className="runs-queued-hint">
          If runs stay in Queued after clicking Trigger, ensure <strong>orchestrator-worker</strong> and <strong>worker</strong> services are running (User Guide → Troubleshooting).
        </p>
      )}
    </div>
  )
}
