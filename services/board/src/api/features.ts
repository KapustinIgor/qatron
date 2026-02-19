import { apiClient } from './client'

export interface ScenarioStep {
  type: string
  keyword: string
  text: string
}

export interface FeatureScenario {
  id: number
  name: string
  type: string
  tags: string[]
  steps: ScenarioStep[]
}

export interface ProjectFeature {
  id: number
  name: string
  file_path: string
  description: string | null
  tags: string[]
  scenarios: FeatureScenario[]
}

export const featuresApi = {
  list: async (projectId: number): Promise<ProjectFeature[]> => {
    const response = await apiClient.get(`/features/projects/${projectId}/features`)
    return response.data
  },

  ingestFromContent: async (
    projectId: number,
    features: { file_path: string; content: string }[]
  ): Promise<{ message: string; features_count: number }> => {
    const response = await apiClient.post(
      `/features/projects/${projectId}/ingest-features-from-content`,
      { features }
    )
    return response.data
  },
}
