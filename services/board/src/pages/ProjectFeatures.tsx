import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { featuresApi, ProjectFeature } from '../api/features'
import { projectsApi } from '../api/projects'
import { getErrorMessage } from '../types'
import './ProjectFeatures.css'

export default function ProjectFeatures() {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const id = projectId ? parseInt(projectId, 10) : 0

  const [pasteContent, setPasteContent] = useState('')
  const [filePath, setFilePath] = useState('features/amazon.feature')
  const [ingestError, setIngestError] = useState('')

  const { data: project } = useQuery({
    queryKey: ['project', id],
    queryFn: () => projectsApi.get(id),
    enabled: id > 0,
  })

  const { data: features, isLoading } = useQuery({
    queryKey: ['features', id],
    queryFn: () => featuresApi.list(id),
    enabled: id > 0,
  })

  const ingestMutation = useMutation<
    { message: string; features_count: number },
    unknown,
    { file_path: string; content: string }[]
  >({
    mutationFn: (items: { file_path: string; content: string }[]) =>
      featuresApi.ingestFromContent(id, items),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['features', id] })
      setPasteContent('')
      setIngestError('')
    },
    onError: (err) => {
      const e: unknown = err
      setIngestError(getErrorMessage(e, 'Ingest failed'))
    },
  })

  const handleIngest = (e: React.FormEvent) => {
    e.preventDefault()
    setIngestError('')
    const content = pasteContent.trim()
    if (!content) {
      setIngestError('Paste Gherkin feature content first')
      return
    }
    ingestMutation.mutate([{ file_path: filePath.trim() || 'feature.feature', content }])
  }

  if (!id) {
    return (
      <div className="project-features-page">
        <p>Invalid project.</p>
        <button className="btn-secondary" onClick={() => navigate('/projects')}>
          Back to Projects
        </button>
      </div>
    )
  }

  return (
    <div className="project-features-page">
      <div className="page-header">
        <button className="btn-back" onClick={() => navigate('/projects')}>
          ← Projects
        </button>
        <h1>Features – {project?.name ?? `Project ${id}`}</h1>
      </div>

      <section className="ingest-section">
        <h2>Ingest feature from content</h2>
        <p className="ingest-hint">
          Paste your Gherkin feature file content below and click Ingest to make it visible in
          QAtron.
        </p>
        <form onSubmit={handleIngest} className="ingest-form">
          <div className="form-group">
            <label htmlFor="file_path">File path (e.g. features/amazon.feature)</label>
            <input
              id="file_path"
              type="text"
              value={filePath}
              onChange={(e) => setFilePath(e.target.value)}
              placeholder="features/amazon.feature"
            />
          </div>
          <div className="form-group">
            <label htmlFor="content">Gherkin content</label>
            <textarea
              id="content"
              value={pasteContent}
              onChange={(e) => setPasteContent(e.target.value)}
              placeholder={'Feature: Amazon.com E2E\n  Scenario: Home page\n    Given I am on the home page\n    Then the page title should contain "Amazon"'}
              rows={12}
            />
          </div>
          {ingestError && <div className="error-message">{ingestError}</div>}
          <button
            type="submit"
            className="btn-primary"
            disabled={ingestMutation.isPending || !pasteContent.trim()}
          >
            {ingestMutation.isPending ? 'Ingesting...' : 'Ingest feature'}
          </button>
        </form>
      </section>

      <section className="features-list-section">
        <h2>Ingested features</h2>
        {isLoading ? (
          <div className="loading">Loading features...</div>
        ) : !features?.length ? (
          <p className="empty-state">
            No features yet. Use the form above to paste and ingest a Gherkin feature file.
          </p>
        ) : (
          <div className="features-list">
            {features.map((f) => (
              <FeatureCard key={f.id} feature={f} />
            ))}
          </div>
        )}
      </section>
    </div>
  )
}

function FeatureCard({ feature }: { feature: ProjectFeature }) {
  const [expanded, setExpanded] = useState(false)
  return (
    <div className="feature-card">
      <div className="feature-card-header" onClick={() => setExpanded(!expanded)}>
        <span className="feature-name">{feature.name}</span>
        <span className="feature-path">{feature.file_path}</span>
        <span className="feature-toggle">{expanded ? '▼' : '▶'}</span>
      </div>
      {expanded && (
        <div className="feature-card-body">
          {feature.description && (
            <p className="feature-description">{feature.description}</p>
          )}
          {feature.tags?.length > 0 && (
            <div className="feature-tags">
              {feature.tags.map((t) => (
                <span key={t} className="tag">
                  {t}
                </span>
              ))}
            </div>
          )}
          <div className="scenarios">
            {feature.scenarios?.map((s) => (
              <div key={s.id} className="scenario">
                <strong>{s.name}</strong>
                <ul className="steps">
                  {s.steps?.map((step, i) => (
                    <li key={i}>
                      <span className="step-keyword">{step.keyword}</span> {step.text}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
