/**
 * Axios API client — auto-authenticates with the demo account on startup.
 * No login screen required. Token is fetched once and reused.
 */
import axios from 'axios'
import type {
  AuthToken, User, Case, CaseListResponse, Document,
  DocumentUploadResponse, ProcessingJob, GraphData,
  TimelineEvent, AuditLog, InvestigationAnswer
} from '../types'

const BASE_URL = (import.meta.env.VITE_API_URL || '') + '/api'

// Demo credentials — auto-login, no user-facing form needed
const DEMO_EMAIL = 'demo@crimenet.local'
const DEMO_PASSWORD = 'crimenet2026'

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

// -------------------------------------------------------
// Token management — fetch once, reuse, refresh on 401
// -------------------------------------------------------
let _token: string | null = null
let _tokenPromise: Promise<string> | null = null

async function fetchToken(): Promise<string> {
  const res = await axios.post<AuthToken>(`${BASE_URL}/auth/login`, {
    email: DEMO_EMAIL,
    password: DEMO_PASSWORD,
  })
  return res.data.access_token
}

async function getToken(): Promise<string> {
  if (_token) return _token
  if (_tokenPromise) return _tokenPromise
  _tokenPromise = fetchToken().then(t => { _token = t; _tokenPromise = null; return t })
  return _tokenPromise
}

// Inject token on every request
apiClient.interceptors.request.use(async (config) => {
  const token = await getToken()
  config.headers.Authorization = `Bearer ${token}`
  return config
})

// On 401, clear cached token and retry once
apiClient.interceptors.response.use(
  res => res,
  async error => {
    if (error.response?.status === 401 && !error.config._retried) {
      _token = null
      _tokenPromise = null
      error.config._retried = true
      const token = await getToken()
      error.config.headers.Authorization = `Bearer ${token}`
      return apiClient(error.config)
    }
    return Promise.reject(error)
  }
)

// -------------------------------------------------------
// Auth (kept for compatibility, not shown in UI)
// -------------------------------------------------------
export const authApi = {
  me: () => apiClient.get<User>('/auth/me'),
  logout: () => { _token = null },
}

// -------------------------------------------------------
// Cases
// -------------------------------------------------------
export const casesApi = {
  list: (status?: string) =>
    apiClient.get<CaseListResponse>('/cases', { params: status ? { status } : {} }),

  create: (data: { title: string; description?: string; priority?: string }) =>
    apiClient.post<Case>('/cases', data),

  get: (caseId: string) => apiClient.get<Case>(`/cases/${caseId}`),

  update: (caseId: string, data: Partial<Case>) =>
    apiClient.put<Case>(`/cases/${caseId}`, data),

  audit: (caseId: string) =>
    apiClient.get<AuditLog[]>(`/cases/${caseId}/audit`),
}

// -------------------------------------------------------
// Documents
// -------------------------------------------------------
export const documentsApi = {
  list: (caseId: string) =>
    apiClient.get<Document[]>(`/cases/${caseId}/documents`),

  upload: (caseId: string, file: File) => {
    const form = new FormData()
    form.append('file', file)
    return apiClient.post<DocumentUploadResponse>(
      `/cases/${caseId}/documents`,
      form,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    )
  },

  get: (caseId: string, documentId: string) =>
    apiClient.get<Document>(`/cases/${caseId}/documents/${documentId}`),

  jobStatus: (caseId: string, jobId: string) =>
    apiClient.get<ProcessingJob>(`/cases/${caseId}/jobs/${jobId}`),

  reprocess: (caseId: string, documentId: string) =>
    apiClient.post<ProcessingJob>(`/cases/${caseId}/reprocess/${documentId}`),
}

// -------------------------------------------------------
// Graph
// -------------------------------------------------------
export const graphApi = {
  getGraph: (caseId: string) =>
    apiClient.get<GraphData>(`/cases/${caseId}/graph`),

  getNode: (caseId: string, nodeId: string) =>
    apiClient.get(`/cases/${caseId}/graph/node/${encodeURIComponent(nodeId)}`),

  shortestPath: (caseId: string, fromId: string, toId: string) =>
    apiClient.get(`/cases/${caseId}/graph/path`, {
      params: { from_id: fromId, to_id: toId }
    }),

  search: (caseId: string, query: string) =>
    apiClient.get<{ results: unknown[] }>(`/cases/${caseId}/graph/search`, {
      params: { q: query }
    }),

  centrality: (caseId: string) =>
    apiClient.get(`/cases/${caseId}/graph/analytics/centrality`),

  entities: (caseId: string, label?: string) =>
    apiClient.get<{ entities: unknown[] }>(`/cases/${caseId}/entities`, {
      params: label ? { label } : {}
    }),

  timeline: (caseId: string) =>
    apiClient.get<{ events: TimelineEvent[] }>(`/cases/${caseId}/timeline`),

  deleteGraph: (caseId: string) =>
    apiClient.delete(`/cases/${caseId}/graph`),
}

// -------------------------------------------------------
// Investigation Assistant
// -------------------------------------------------------
export const investigationApi = {
  ask: (caseId: string, question: string) =>
    apiClient.post<InvestigationAnswer>(`/cases/${caseId}/investigate`, { question }),
}
