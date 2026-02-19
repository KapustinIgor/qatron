/** Shape of API/axios error for extracting message in catch handlers */
export type ApiErrorShape = {
  response?: { data?: { detail?: string | string[] } }
  message?: string
}

export function getErrorMessage(err: unknown, fallback: string): string {
  const e = err as ApiErrorShape
  const detail = e?.response?.data?.detail ?? e?.message
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) return detail.join(', ')
  return fallback
}
