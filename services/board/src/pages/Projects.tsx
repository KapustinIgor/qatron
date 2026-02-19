import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { projectsApi, Project } from '../api/projects'
import { authApi } from '../api/auth'
import { getErrorMessage } from '../types'
import './Projects.css'

export default function Projects() {
  const navigate = useNavigate()
  const [showModal, setShowModal] = useState(false)
  const [editingProject, setEditingProject] = useState<Project | null>(null)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    repo_url: '',
    repo_auth_method: 'token',
    organization_id: 1,
  })
  const [error, setError] = useState('')

  const queryClient = useQueryClient()

  const { data: projects, isLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: () => projectsApi.list(),
  })

  const { data: currentUser } = useQuery({
    queryKey: ['currentUser'],
    queryFn: () => authApi.getCurrentUser(),
  })

  const createMutation = useMutation<Project, unknown, typeof formData>({
    mutationFn: (data: typeof formData) => projectsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      setShowModal(false)
      setEditingProject(null)
      setFormData({
        name: '',
        description: '',
        repo_url: '',
        repo_auth_method: 'token',
        organization_id: currentUser?.organization_id || 1,
      })
      setError('')
    },
    onError: (err: unknown) => {
      setError(getErrorMessage(err, 'Failed to create project'))
    },
  })

  const updateMutation = useMutation<
    Project,
    unknown,
    { id: number; data: Partial<typeof formData> }
  >({
    mutationFn: ({ id, data }: { id: number; data: Partial<typeof formData> }) =>
      projectsApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      setShowModal(false)
      setEditingProject(null)
      setFormData({
        name: '',
        description: '',
        repo_url: '',
        repo_auth_method: 'token',
        organization_id: currentUser?.organization_id || 1,
      })
      setError('')
    },
    onError: (err: unknown) => {
      setError(getErrorMessage(err, 'Failed to update project'))
    },
  })

  const handleEdit = (project: Project) => {
    setEditingProject(project)
    setFormData({
      name: project.name,
      description: project.description || '',
      repo_url: project.repo_url,
      repo_auth_method: project.repo_auth_method,
      organization_id: project.organization_id,
    })
    setShowModal(true)
  }

  const handleViewRuns = (projectId: number) => {
    navigate(`/runs?project_id=${projectId}`)
  }

  const handleViewFeatures = (projectId: number) => {
    navigate(`/projects/${projectId}/features`)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (!formData.name || !formData.repo_url) {
      setError('Name and Repository URL are required')
      return
    }
    if (editingProject) {
      updateMutation.mutate({
        id: editingProject.id,
        data: {
          name: formData.name,
          description: formData.description,
          repo_url: formData.repo_url,
          repo_auth_method: formData.repo_auth_method,
        },
      })
    } else {
      createMutation.mutate({
        ...formData,
        organization_id: currentUser?.organization_id || 1,
      })
    }
  }

  const handleCloseModal = () => {
    setShowModal(false)
    setEditingProject(null)
    setFormData({
      name: '',
      description: '',
      repo_url: '',
      repo_auth_method: 'token',
      organization_id: currentUser?.organization_id || 1,
    })
    setError('')
  }

  if (isLoading) {
    return <div className="loading">Loading projects...</div>
  }

  return (
    <div className="projects-page">
      <div className="page-header">
        <h1>Projects</h1>
        <button className="btn-primary" onClick={() => setShowModal(true)}>
          New Project
        </button>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={handleCloseModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editingProject ? 'Edit Project' : 'Create New Project'}</h2>
              <button className="modal-close" onClick={handleCloseModal}>
                ×
              </button>
            </div>
            <form onSubmit={handleSubmit}>
              {error && <div className="error-message">{error}</div>}
              <div className="form-group">
                <label htmlFor="name">Project Name *</label>
                <input
                  id="name"
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  placeholder="My Test Project"
                />
              </div>
              <div className="form-group">
                <label htmlFor="description">Description</label>
                <textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Project description"
                  rows={3}
                />
              </div>
              <div className="form-group">
                <label htmlFor="repo_url">Repository URL *</label>
                <input
                  id="repo_url"
                  type="url"
                  value={formData.repo_url}
                  onChange={(e) => setFormData({ ...formData, repo_url: e.target.value })}
                  required
                  placeholder="https://github.com/org/repo"
                />
              </div>
              <div className="form-group">
                <label htmlFor="repo_auth_method">Authentication Method *</label>
                <select
                  id="repo_auth_method"
                  value={formData.repo_auth_method}
                  onChange={(e) => setFormData({ ...formData, repo_auth_method: e.target.value })}
                  required
                >
                  <option value="token">Token</option>
                  <option value="ssh">SSH</option>
                </select>
              </div>
              <div className="form-actions">
                <button type="button" className="btn-secondary" onClick={handleCloseModal}>
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-primary"
                  disabled={createMutation.isPending || updateMutation.isPending}
                >
                  {createMutation.isPending || updateMutation.isPending
                    ? editingProject
                      ? 'Updating...'
                      : 'Creating...'
                    : editingProject
                      ? 'Update Project'
                      : 'Create Project'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="projects-grid">
        {projects?.map((project) => (
          <div key={project.id} className="project-card">
            <h3>{project.name}</h3>
            <p>{project.description || 'No description'}</p>
            <div className="project-meta">
              <div className="meta-item">
                <label>Repo:</label>
                <span>{project.repo_url}</span>
              </div>
              <div className="meta-item">
                <label>Auth:</label>
                <span>{project.repo_auth_method}</span>
              </div>
              <div className="meta-item">
                <label>Created:</label>
                <span>{new Date(project.created_at).toLocaleDateString()}</span>
              </div>
            </div>
            <div className="project-actions">
              <button onClick={() => handleEdit(project)}>Configure</button>
              <button onClick={() => handleViewFeatures(project.id)}>Features</button>
              <button onClick={() => handleViewRuns(project.id)}>View Runs</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
