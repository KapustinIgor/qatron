import { useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { runsApi } from '../api/runs'
import { getErrorMessage } from '../types'
import './RunDetail.css'

export default function RunDetail() {
  const { runId } = useParams<{ runId: string }>()
  const runIdNum = parseInt(runId || '0', 10)

  const queryClient = useQueryClient()
  const { data: run, isLoading } = useQuery({
    queryKey: ['runs', runIdNum],
    queryFn: () => runsApi.get(runIdNum),
  })

  const triggerMutation = useMutation<
    { message: string; run_id: number },
    unknown,
    void
  >({
    mutationFn: () => runsApi.trigger(runIdNum),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['runs', runIdNum] })
      queryClient.invalidateQueries({ queryKey: ['runs'] })
    },
  })

  const triggerErrorMessage = triggerMutation.error
    ? getErrorMessage(triggerMutation.error, 'Trigger failed')
    : ''
  const isTriggerSuccess = triggerMutation.isSuccess && !triggerMutation.isPending

  if (isLoading) {
    return <div className="loading">Loading run details...</div>
  }

  if (!run) {
    return <div className="error">Run not found</div>
  }

  return (
    <div className="run-detail">
      <div className="run-detail-header">
        <h1>Run #{run.id}</h1>
        {run.status === 'queued' && (
          <div className="trigger-block">
            <button
              type="button"
              className="btn-trigger"
              onClick={() => triggerMutation.mutate()}
              disabled={triggerMutation.isPending}
            >
              {triggerMutation.isPending ? 'Triggering...' : 'Trigger run'}
            </button>
            {triggerErrorMessage ? (
              <p className="trigger-error">{triggerErrorMessage}</p>
            ) : null}
            {isTriggerSuccess && (
              <p className="trigger-success">Run triggered. Status may update shortly.</p>
            )}
            <p className="trigger-info">
              Runs are executed by the worker (clone repo, run pytest). No output appears in your IDE terminal. To see test logs: <code>cd deployment/docker-compose && docker compose logs worker -f</code>. Ensure orchestrator-worker and worker are running; project repo must be cloneable.
            </p>
          </div>
        )}
      </div>

      <div className="run-header">
        <div className="run-info">
          <div className="info-item">
            <label>Status:</label>
            <span className={`status-badge status-${run.status}`}>
              {run.status}
            </span>
          </div>
          <div className="info-item">
            <label>Project:</label>
            <span>{run.project_id}</span>
          </div>
          <div className="info-item">
            <label>Suite:</label>
            <span>{run.suite_id}</span>
          </div>
          <div className="info-item">
            <label>Branch:</label>
            <span>{run.branch || 'N/A'}</span>
          </div>
          <div className="info-item">
            <label>Commit:</label>
            <span>{run.commit || 'N/A'}</span>
          </div>
          <div className="info-item">
            <label>Duration:</label>
            <span>{run.duration_seconds ? `${run.duration_seconds}s` : 'N/A'}</span>
          </div>
        </div>

        <div className="test-stats">
          <div className="stat">
            <div className="stat-value">{run.total_tests}</div>
            <div className="stat-label">Total</div>
          </div>
          <div className="stat success">
            <div className="stat-value">{run.passed_tests}</div>
            <div className="stat-label">Passed</div>
          </div>
          <div className="stat error">
            <div className="stat-value">{run.failed_tests}</div>
            <div className="stat-label">Failed</div>
          </div>
          <div className="stat">
            <div className="stat-value">{run.skipped_tests}</div>
            <div className="stat-label">Skipped</div>
          </div>
        </div>
      </div>

      <div className="run-timeline">
        <h2>Timeline</h2>
        <div className="timeline-item">
          <label>Created:</label>
          <span>{new Date(run.created_at).toLocaleString()}</span>
        </div>
        {run.started_at && (
          <div className="timeline-item">
            <label>Started:</label>
            <span>{new Date(run.started_at).toLocaleString()}</span>
          </div>
        )}
        {run.completed_at && (
          <div className="timeline-item">
            <label>Completed:</label>
            <span>{new Date(run.completed_at).toLocaleString()}</span>
          </div>
        )}
      </div>
    </div>
  )
}
