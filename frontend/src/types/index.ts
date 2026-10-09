// ============================================================
// Domain types matching the backend Pydantic schemas
// ============================================================

export type UserRole = 'ADMIN' | 'INVESTIGATOR' | 'ANALYST' | 'VIEWER'

export interface User {
  id: string
  name: string
  email: string
  role: UserRole
  is_active: boolean
  created_at: string
}

export interface AuthToken {
  access_token: string
  token_type: string
  user: User
}

export type CaseStatus = 'ACTIVE' | 'CLOSED' | 'ARCHIVED'
export type CasePriority = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW'

export interface Case {
  id: string
  case_number: string
  title: string
  description: string | null
  status: CaseStatus
  priority: CasePriority
  created_by: string
  created_at: string
  updated_at: string
}

export interface CaseListResponse {
  cases: Case[]
  total: number
}

export type DocumentType = 'PDF' | 'TXT' | 'DOCX' | 'CSV' | 'JSON' | 'UNKNOWN'
export type ProcessingStatus = 'UPLOADED' | 'PROCESSING' | 'PROCESSED' | 'FAILED'

export interface Document {
  id: string
  case_id: string
  filename: string
  original_filename: string
  document_type: DocumentType
  file_size_bytes: number | null
  processing_status: ProcessingStatus
  processing_error: string | null
  uploaded_by: string
  uploaded_at: string
  processed_at: string | null
}

export interface DocumentUploadResponse {
  document: Document
  job_id: string
  message: string
}

export type JobStatus = 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'CANCELLED'

export interface ProcessingJob {
  id: string
  case_id: string
  document_id: string | null
  job_type: string
  status: JobStatus
  progress_pct: number
  result_summary: Record<string, unknown> | null
  error_message: string | null
  started_at: string | null
  completed_at: string | null
  created_at: string
}

// Graph types
export interface GraphNode {
  id: string
  name?: string
  _labels: string[]
  [key: string]: unknown
}

export interface GraphEdge {
  source: string
  target: string
  type: string
  confidence?: number
  evidence_text?: string
  source_document_id?: string
  [key: string]: unknown
}

export interface GraphData {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

export interface TimelineEvent {
  id: string
  name: string
  event_type: string
  timestamp: string
  description: string
  location: string
  participants: string[]
}

export interface AuditLog {
  id: string
  user_id: string | null
  case_id: string | null
  action: string
  metadata: Record<string, unknown> | null
  ip_address: string | null
  timestamp: string
}

export interface InvestigationAnswer {
  answer: string
  query_strategy: string
  evidence: Record<string, unknown>[]
  total_evidence_rows: number
}
