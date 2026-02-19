import { apiClient } from './client'

export interface Run {
  id: number
  status: 'queued' | 'running' | 'completed' | 'failed' | 'cancelled'
  project_id: number
  suite_id: number
  environment_id: number
  branch?: string
  commit?: string
  commit_message?: string
  triggered_by?: string
  started_at?: string
  completed_at?: string
  duration_seconds?: number
  total_tests: number
  passed_tests: number
  failed_tests: number
  skipped_tests: number
  dataset_version?: string
  created_at: string
  updated_at?: string
}

export interface RunFilters {
  project_id?: number
  suite_id?: number
  environment_id?: number
  status?: string
  branch?: string
  skip?: number
  limit?: number
}

export const runsApi = {
  list: async (filters?: RunFilters): Promise<Run[]> => {
    const response = await apiClient.get('/runs', { params: filters })
    return response.data
  },

  get: async (id: number): Promise<Run> => {
    const response = await apiClient.get(`/runs/${id}`)
    return response.data
  },

  create: async (data: Partial<Run>): Promise<Run> => {
    const response = await apiClient.post('/runs', data)
    return response.data
  },

  update: async (id: number, data: Partial<Run>): Promise<Run> => {
    const response = await apiClient.put(`/runs/${id}`, data)
    return response.data
  },

  trigger: async (id: number): Promise<{ message: string; run_id: number }> => {
    const response = await apiClient.post(`/runs/${id}/trigger`)
    return response.data
  },
}
