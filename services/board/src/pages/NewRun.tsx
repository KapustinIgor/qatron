import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { projectsApi } from '../api/projects'
import { Run, runsApi } from '../api/runs'
import { getErrorMessage } from '../types'
import './NewRun.css'

export default function NewRun() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [projectId, setProjectId] = useState<number | ''>('')
  const [suiteId, setSuiteId] = useState<number | ''>('')
  const [environmentId, setEnvironmentId] = useState<number | ''>('')
  const [branch, setBranch] = useState('')
  const [error, setError] = useState('')

  const { data: projects } = useQuery({
    queryKey: ['projects'],
    queryFn: () => projectsApi.list(),
  })

  const { data: suites } = useQuery({
    queryKey: ['projects', projectId, 'suites'],
    queryFn: () => projectsApi.listSuites(projectId as number),
    enabled: typeof projectId === 'number' && projectId > 0,
  })

  const { data: environments } = useQuery({
    queryKey: ['projects', projectId, 'environments'],
    queryFn: () => projectsApi.listEnvironments(projectId as number),
    enabled: typeof projectId === 'number' && projectId > 0,
  })

  const createMutation = useMutation<
    Run,
    unknown,
    { project_id: number; suite_id: number; environment_id: number; branch?: string }
  >({
    mutationFn: (data: { project_id: number; suite_id: number; environment_id: number; branch?: string }) =>
      runsApi.create(data),
    onSuccess: (run: Run) => {
      queryClient.invalidateQueries({ queryKey: ['runs'] })
      navigate(`/runs/${run.id}`)
    },
    onError: (err) => {
      const e: unknown = err
      setError(getErrorMessage(e, 'Failed to create run'))
    },
  })

  const handleProjectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const id = e.target.value ? parseInt(e.target.value, 10) : ''
    setProjectId(id)
    setSuiteId('')
    setEnvironmentId('')
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (!projectId || !suiteId || !environmentId) {
      setError('Please select project, suite, and environment')
      return
    }
    createMutation.mutate({
      project_id: projectId as number,
      suite_id: suiteId as number,
      environment_id: environmentId as number,
      branch: branch.trim() || undefined,
    })
  }

  const noSuites = projectId && suites?.length === 0
  const noEnvironments = projectId && environments?.length === 0
  const canEnsureDefaults = Boolean(noSuites || noEnvironments)

  const ensureDefaultsMutation = useMutation<
    { message: string; created: string[] },
    unknown,
    void
  >({
    mutationFn: () => projectsApi.ensureDefaults(projectId as number),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['projects', projectId, 'suites'],
      })
      queryClient.invalidateQueries({
        queryKey: ['projects', projectId, 'environments'],
      })
    },
    onError: (err) => {
      const e: unknown = err
      setError(getErrorMessage(e, 'Failed to create defaults'))
    },
  })

  return (
    <div className="new-run-page">
      <div className="page-header">
        <Link to="/runs" className="btn-back">
          ← Runs
        </Link>
        <h1>New Run</h1>
      </div>

      <div className="new-run-card">
        <p className="new-run-intro">
          Create a test run by selecting a project, suite, and environment. The run will be queued
          and appear on the Runs list.
        </p>

        <form onSubmit={handleSubmit}>
          {error && <div className="error-message">{error}</div>}

          <div className="form-group">
            <label htmlFor="project">Project *</label>
            <select
              id="project"
              value={projectId}
              onChange={handleProjectChange}
              required
            >
              <option value="">Select project</option>
              {projects?.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </div>

          {canEnsureDefaults && (
            <div className="form-hint warning">
              This project has no suites.
              <button
                type="button"
                className="btn-ensure-defaults"
                onClick={() => ensureDefaultsMutation.mutate()}
                disabled={ensureDefaultsMutation.isPending}
              >
                {ensureDefaultsMutation.isPending
                  ? 'Creating...'
                  : 'Create default suite & environment'}
              </button>
            </div>
          )}
          <div className="form-group">
            <label htmlFor="suite">Suite *</label>
            <select
              id="suite"
              value={suiteId}
              onChange={(e) => setSuiteId(e.target.value ? parseInt(e.target.value, 10) : '')}
              required
              disabled={!projectId || !suites?.length}
            >
              <option value="">Select suite</option>
              {suites?.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name} ({s.layer})
                </option>
              ))}
            </select>
          </div>

          {noEnvironments && !noSuites && (
            <div className="form-hint warning">
              This project has no environments. Use “Create default suite & environment” above if
              you haven’t yet.
            </div>
          )}
          <div className="form-group">
            <label htmlFor="environment">Environment *</label>
            <select
              id="environment"
              value={environmentId}
              onChange={(e) =>
                setEnvironmentId(e.target.value ? parseInt(e.target.value, 10) : '')
              }
              required
              disabled={!projectId || !environments?.length}
            >
              <option value="">Select environment</option>
              {environments?.map((e) => (
                <option key={e.id} value={e.id}>
                  {e.name}
                  {e.base_url ? ` — ${e.base_url}` : ''}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="branch">Branch (optional)</label>
            <input
              id="branch"
              type="text"
              value={branch}
              onChange={(e) => setBranch(e.target.value)}
              placeholder="main"
            />
          </div>

          <div className="form-actions">
            <Link to="/runs" className="btn-secondary">
              Cancel
            </Link>
            <button
              type="submit"
              className="btn-primary"
              disabled={
                createMutation.isPending ||
                !projectId ||
                !suiteId ||
                !environmentId ||
                !suites?.length ||
                !environments?.length
              }
            >
              {createMutation.isPending ? 'Creating...' : 'Create run'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
