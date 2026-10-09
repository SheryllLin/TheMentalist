import { useParams, Routes, Route, NavLink, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { casesApi } from '../services/api'
import { Case, CaseStatus } from '../types'
import {
  ArrowLeft, Loader2, Activity, CheckCircle, Archive,
  Hash, Calendar, AlertTriangle,
} from 'lucide-react'
import { format } from 'date-fns'
import CaseOverviewTab   from '../components/case/CaseOverviewTab'
import CaseGraphTab      from '../components/case/CaseGraphTab'
import CaseEntitiesTab   from '../components/case/CaseEntitiesTab'
import CaseTimelineTab   from '../components/case/CaseTimelineTab'
import CaseDocumentsTab  from '../components/case/CaseDocumentsTab'
import CaseAssistantTab  from '../components/case/CaseAssistantTab'

const TABS = [
  { path: 'overview',   label: 'Overview'         },
  { path: 'graph',      label: 'Investigation Board' },
  { path: 'entities',   label: 'Persons & Entities' },
  { path: 'timeline',   label: 'Timeline'          },
  { path: 'documents',  label: 'Evidence Files'    },
  { path: 'assistant',  label: 'Intelligence AI'   },
]

const STATUS_META: Record<CaseStatus, { icon: React.ReactNode; cls: string }> = {
  ACTIVE:   { icon: <Activity   className="w-3 h-3" />, cls: 'badge-active'   },
  CLOSED:   { icon: <CheckCircle className="w-3 h-3" />, cls: 'badge-closed'  },
  ARCHIVED: { icon: <Archive    className="w-3 h-3" />, cls: 'badge-archived' },
}

export default function CaseWorkspacePage() {
  const { caseId } = useParams<{ caseId: string }>()
  const navigate = useNavigate()

  const { data, isLoading, error } = useQuery({
    queryKey: ['case', caseId],
    queryFn: () => casesApi.get(caseId!),
    enabled: !!caseId,
  })
  const caseData: Case | undefined = data?.data

  /* ── Loading ─────────────────────────────────────────────── */
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <Loader2 className="w-6 h-6 animate-spin text-brass mx-auto mb-3" />
          <p className="text-xs font-mono text-sepia">Loading case file…</p>
        </div>
      </div>
    )
  }

  /* ── Error ───────────────────────────────────────────────── */
  if (error || !caseData) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="card text-center max-w-sm">
          <AlertTriangle className="w-8 h-8 text-burgundy-light mx-auto mb-3" />
          <p className="font-serif text-base text-parchment mb-1">Case file not found</p>
          <p className="text-xs text-sepia mb-4">This record may have been archived or does not exist.</p>
          <button onClick={() => navigate('/cases')} className="btn-secondary text-xs">
            Return to Case Library
          </button>
        </div>
      </div>
    )
  }

  const statusMeta = STATUS_META[caseData.status]

  return (
    <div className="flex flex-col h-full bg-espresso">

      {/* ── Case file header ─────────────────────────────────── */}
      <div
        className="flex-shrink-0 border-b border-wire"
        style={{ background: '#2C1F1A' }}
      >
        {/* Breadcrumb row */}
        <div className="flex items-center gap-2 px-6 pt-3 pb-0">
          <button
            onClick={() => navigate('/cases')}
            className="flex items-center gap-1.5 text-sepia hover:text-parchment
                       transition-colors text-xs font-sans"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            Case Library
          </button>
          <span className="text-sepia/30 text-xs">/</span>
          <span className="text-xs font-mono text-brass">{caseData.case_number}</span>
        </div>

        {/* Title row */}
        <div className="flex items-start gap-4 px-6 pt-2.5 pb-3">
          {/* Left: case number stamp */}
          <div
            className="hidden sm:flex flex-col items-center justify-center
                       w-12 h-12 rounded-file border border-wire-strong
                       bg-walnut flex-shrink-0"
          >
            <Hash className="w-3.5 h-3.5 text-sepia/60 mb-0.5" />
            <span className="text-[8px] font-mono text-sepia/60 tracking-widest text-center leading-none px-0.5 break-all">
              {caseData.case_number.replace('CASE-', '')}
            </span>
          </div>

          {/* Title + meta */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2.5 flex-wrap mb-1">
              <span className={`${statusMeta.cls} flex items-center gap-1`}>
                {statusMeta.icon}
                {caseData.status}
              </span>
              <span className="text-sepia/40 text-xs">·</span>
              <span className="text-xs font-mono text-sepia/70 flex items-center gap-1">
                <Calendar className="w-3 h-3" />
                Opened {format(new Date(caseData.created_at), 'dd MMM yyyy')}
              </span>
            </div>
            <h1 className="font-serif text-lg font-bold text-cream leading-snug">
              {caseData.title}
            </h1>
            {caseData.description && (
              <p className="text-xs text-sepia mt-1 font-sans leading-relaxed line-clamp-1">
                {caseData.description}
              </p>
            )}
          </div>
        </div>

        {/* Tab bar */}
        <div
          className="flex items-end gap-0 px-6 overflow-x-auto"
          style={{ scrollbarWidth: 'none' }}
        >
          {TABS.map((tab) => (
            <NavLink
              key={tab.path}
              to={`/cases/${caseId}/${tab.path}`}
              className={({ isActive }) =>
                isActive ? 'workspace-tab-active' : 'workspace-tab-inactive'
              }
            >
              {tab.label}
            </NavLink>
          ))}
        </div>
      </div>

      {/* ── Tab content ──────────────────────────────────────── */}
      <div className="flex-1 overflow-auto">
        <Routes>
          <Route path="overview"  element={<CaseOverviewTab  caseData={caseData} />} />
          <Route path="graph"     element={<CaseGraphTab     caseId={caseId!} />} />
          <Route path="entities"  element={<CaseEntitiesTab  caseId={caseId!} />} />
          <Route path="timeline"  element={<CaseTimelineTab  caseId={caseId!} />} />
          <Route path="documents" element={<CaseDocumentsTab caseId={caseId!} />} />
          <Route path="assistant" element={<CaseAssistantTab caseId={caseId!} />} />
          <Route path="*"         element={<CaseOverviewTab  caseData={caseData} />} />
        </Routes>
      </div>
    </div>
  )
}
