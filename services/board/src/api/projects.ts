import { apiClient } from './client'

export interface Project {
  id: number
  name: string
  description?: string
  repo_url: string
  repo_auth_method: string
  organization_id: number
  created_at: string
  updated_at?: string
}

export interface SuiteOption {
  id: number
  name: string
  layer: string
}

export interface EnvironmentOption {
  id: number
  name: string
  base_url: string | null
}

export const projectsApi = {
  list: async (): Promise<Project[]> => {
    const response = await apiClient.get('/projects')
    return response.data
  },

  get: async (id: number): Promise<Project> => {
    const response = await apiClient.get(`/projects/${id}`)
    return response.data
  },

  listSuites: async (projectId: number): Promise<SuiteOption[]> => {
    const response = await apiClient.get(`/projects/${projectId}/suites`)
    return response.data
  },

  listEnvironments: async (projectId: number): Promise<EnvironmentOption[]> => {
    const response = await apiClient.get(`/projects/${projectId}/environments`)
    return response.data
  },

  ensureDefaults: async (projectId: number): Promise<{ message: string; created: string[] }> => {
    const response = await apiClient.post(`/projects/${projectId}/ensure-defaults`)
    return response.data
  },

  create: async (data: Partial<Project>): Promise<Project> => {
    const response = await apiClient.post('/projects', data)
    return response.data
  },

  update: async (id: number, data: Partial<Project>): Promise<Project> => {
    const response = await apiClient.put(`/projects/${id}`, data)
    return response.data
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/projects/${id}`)
  },
}
