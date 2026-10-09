import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { casesApi } from '../services/api'
import { Case, CasePriority, CaseStatus } from '../types'
import {
  Plus, Search, Filter, Loader2, AlertTriangle,
  FolderOpen, Hash, Calendar, ChevronRight, Activity,
  CheckCircle, Archive, X,
} from 'lucide-react'
import { format, formatDistanceToNow } from 'date-fns'

// ── helpers ──────────────────────────────────────────────────
const PRIORITY_CLASS: Record<CasePriority, string> = {
  CRITICAL: 'badge-critical', HIGH: 'badge-high',
  MEDIUM: 'badge-medium',     LOW:  'badge-low',
}
const STATUS_ICON: Record<CaseStatus, React.ReactNode> = {
  ACTIVE:   <Activity    className="w-3 h-3" />,
  CLOSED:   <CheckCircle className="w-3 h-3" />,
  ARCHIVED: <Archive     className="w-3 h-3" />,
}
const STATUS_CLASS: Record<CaseStatus, string> = {
  ACTIVE: 'badge-active', CLOSED: 'badge-closed', ARCHIVED: 'badge-archived',
}

// ── CaseRow (table row) ───────────────────────────────────────
function CaseRow({ c }: { c: Case }) {
  const navigate = useNavigate()
  const leftColor = c.status === 'CLOSED' ? '#4A6B4A'
    : c.status === 'ARCHIVED' ? '#6B5A3A' : '#7A2D35'

  return (
    <tr
      onClick={() => navigate(`/cases/${c.id}/overview`)}
      className="border-b border-wire/60 cursor-pointer hover:bg-walnut/40 transition-colors group"
    >
      {/* Left accent */}
      <td className="w-1 p-0">
        <div className="w-1 h-full" style={{ background: leftColor, minHeight: 48 }} />
      </td>
      {/* Case number */}
      <td className="py-3 pl-4 pr-3 w-44">
        <span className="text-[10px] font-mono text-brass flex items-center gap-1">
          <Hash className="w-2.5 h-2.5 opacity-60" />
          {c.case_number}
        </span>
      </td>
      {/* Title */}
      <td className="py-3 px-3 max-w-0">
        <p className="text-sm font-serif font-semibold text-cream truncate
                      group-hover:text-white transition-colors">
          {c.title}
        </p>
        {c.description && (
          <p className="text-xs text-sepia truncate mt-0.5 font-sans">{c.description}</p>
        )}
      </td>
      {/* Priority */}
      <td className="py-3 px-3 w-28">
        <span className={PRIORITY_CLASS[c.priority]}>{c.priority}</span>
      </td>
      {/* Status */}
      <td className="py-3 px-3 w-28">
        <span className={`${STATUS_CLASS[c.status]} flex items-center gap-1 w-fit`}>
          {STATUS_ICON[c.status]}
          {c.status}
        </span>
      </td>
      {/* Last updated */}
      <td className="py-3 px-3 w-36">
        <span className="text-[10px] font-mono text-sepia/70 flex items-center gap-1">
          <Calendar className="w-2.5 h-2.5" />
          {formatDistanceToNow(new Date(c.updated_at), { addSuffix: true })}
        </span>
      </td>
      {/* Arrow */}
      <td className="py-3 pl-0 pr-4 w-8">
        <ChevronRight className="w-3.5 h-3.5 text-sepia/30
                                  group-hover:text-sepia/70 transition-colors" />
      </td>
    </tr>
  )
}

// ── CreateCaseModal (reused from Dashboard) ───────────────────
function CreateCaseModal({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient()
  const navigate = useNavigate()
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [priority, setPriority] = useState<CasePriority>('MEDIUM')

  const { mutate, isPending, error } = useMutation({
    mutationFn: () => casesApi.create({ title: title.trim(), description: description.trim(), priority }),
    onSuccess: (res) => {
      qc.invalidateQueries({ queryKey: ['cases'] })
      onClose()
      navigate(`/cases/${res.data.id}/overview`)
    },
  })

  return (
    <div className="fixed inset-0 bg-espresso/80 flex items-center justify-center z-50 px-4">
      <div className="w-full max-w-md bg-walnut border border-wire-strong rounded-file
                      shadow-card-hover animate-fade-up">
        <div className="flex items-center justify-between px-5 py-4 border-b border-wire">
          <div>
            <h2 className="font-serif text-base font-semibold text-cream">Open New Investigation</h2>
            <p className="text-xs text-sepia mt-0.5 font-sans">A new case file will be assigned a reference number.</p>
          </div>
          <button onClick={onClose} className="text-sepia hover:text-parchment transition-colors">
            <X className="w-4 h-4" />
          </button>
        </div>
        <div className="px-5 py-4 space-y-4">
          <div>
            <label className="text-label block mb-1.5">Case Title</label>
            <input type="text" value={title} onChange={(e) => setTitle(e.target.value)}
              className="input-field" placeholder="e.g. Suspected Organised Fraud Network" autoFocus />
          </div>
          <div>
            <label className="text-label block mb-1.5">Summary</label>
            <textarea value={description} onChange={(e) => setDescription(e.target.value)}
              className="input-field resize-none h-20" placeholder="Brief description…" />
          </div>
          <div>
            <label className="text-label block mb-1.5">Priority Classification</label>
            <select value={priority} onChange={(e) => setPriority(e.target.value as CasePriority)}
              className="input-field">
              {(['CRITICAL','HIGH','MEDIUM','LOW'] as CasePriority[]).map((p) => (
                <option key={p} value={p} className="bg-walnut">{p}</option>
              ))}
            </select>
          </div>
          {error && (
            <p className="text-xs text-burgundy-light bg-burgundy/10 border border-burgundy/30
                          rounded-file px-3 py-2">Failed to create case. Please try again.</p>
          )}
        </div>
        <div className="flex gap-3 px-5 py-4 border-t border-wire">
          <button onClick={onClose} className="btn-secondary flex-1">Cancel</button>
          <button onClick={() => mutate()} disabled={!title.trim() || isPending}
            className="btn-primary flex-1 flex items-center justify-center gap-2
                       disabled:opacity-40 disabled:cursor-not-allowed">
            {isPending
              ? <><Loader2 className="w-4 h-4 animate-spin" />Opening…</>
              : <><Plus className="w-4 h-4" />Open Case</>}
          </button>
        </div>
      </div>
    </div>
  )
}

// ── Main page ─────────────────────────────────────────────────
export default function CasesPage() {
  const [showCreate, setShowCreate] = useState(false)
  const [search, setSearch]         = useState('')
  const [statusFilter, setStatusFilter] = useState<CaseStatus | 'ALL'>('ALL')

  const { data, isLoading, error } = useQuery({
    queryKey: ['cases'],
    queryFn:  () => casesApi.list(),
  })

  const allCases = data?.data?.cases ?? []
  const filtered = allCases.filter((c) => {
    const matchesStatus = statusFilter === 'ALL' || c.status === statusFilter
    const matchesSearch = !search ||
      c.title.toLowerCase().includes(search.toLowerCase()) ||
      c.case_number.toLowerCase().includes(search.toLowerCase()) ||
      (c.description || '').toLowerCase().includes(search.toLowerCase())
    return matchesStatus && matchesSearch
  })

  const counts = {
    ALL:      allCases.length,
    ACTIVE:   allCases.filter((c) => c.status === 'ACTIVE').length,
    CLOSED:   allCases.filter((c) => c.status === 'CLOSED').length,
    ARCHIVED: allCases.filter((c) => c.status === 'ARCHIVED').length,
  }

  return (
    <div className="min-h-full bg-parchment-texture">

      {/* Header */}
      <div className="px-8 pt-7 pb-5 border-b border-wire">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-label mb-1">Investigation Division</p>
            <h1 className="font-serif text-2xl font-bold text-cream tracking-tight">
              Case Library
            </h1>
            <p className="font-garamond italic text-sm text-sepia mt-1">
              {allCases.length} case{allCases.length !== 1 ? 's' : ''} on file
            </p>
          </div>
          <button onClick={() => setShowCreate(true)} className="btn-primary flex items-center gap-2">
            <Plus className="w-4 h-4" />
            Open New Case
          </button>
        </div>
      </div>

      <div className="px-8 py-5">

        {/* Filter bar */}
        <div className="flex items-center gap-3 mb-5 flex-wrap">
          {/* Status tabs */}
          <div className="flex items-center rounded-file border border-wire overflow-hidden">
            {(['ALL', 'ACTIVE', 'CLOSED', 'ARCHIVED'] as const).map((s) => (
              <button
                key={s}
                onClick={() => setStatusFilter(s)}
                className={`px-3 py-1.5 text-xs font-mono uppercase tracking-wide
                            border-r border-wire last:border-0 transition-colors ${
                  statusFilter === s
                    ? 'bg-burgundy/20 text-cream'
                    : 'text-sepia hover:text-parchment hover:bg-walnut/40'
                }`}
              >
                {s}{' '}
                <span className="opacity-60">({counts[s]})</span>
              </button>
            ))}
          </div>

          {/* Search */}
          <div className="flex items-center gap-2 rounded-file border border-wire px-2.5 py-1.5
                          w-64" style={{ background: '#352720' }}>
            <Search className="w-3.5 h-3.5 text-sepia/60 flex-shrink-0" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search title, ID, keywords…"
              className="bg-transparent text-sm text-cream placeholder-sepia/50
                         outline-none flex-1 font-sans"
            />
            {search && (
              <button onClick={() => setSearch('')} className="text-sepia/50 hover:text-sepia">
                <X className="w-3 h-3" />
              </button>
            )}
          </div>

          <div className="ml-auto text-xs font-mono text-sepia/60">
            {filtered.length} result{filtered.length !== 1 ? 's' : ''}
          </div>
        </div>

        {/* Table */}
        {isLoading ? (
          <div className="flex justify-center py-16">
            <Loader2 className="w-5 h-5 animate-spin text-brass" />
          </div>
        ) : error ? (
          <div className="card flex items-center gap-3 text-burgundy-light max-w-md">
            <AlertTriangle className="w-5 h-5 flex-shrink-0" />
            <div>
              <p className="text-sm font-medium">Failed to load case library</p>
              <p className="text-xs text-sepia mt-0.5">Check backend connectivity</p>
            </div>
          </div>
        ) : filtered.length === 0 ? (
          <div className="card text-center py-14 max-w-md mx-auto">
            <FolderOpen className="w-9 h-9 text-sepia/20 mx-auto mb-3" />
            <p className="font-serif text-base text-parchment mb-1">
              {allCases.length === 0 ? 'No cases on file' : 'No matching cases'}
            </p>
            <p className="text-xs text-sepia mb-4 font-sans">
              {allCases.length === 0
                ? 'Open a new investigation to begin.'
                : 'Adjust the filters or search term.'}
            </p>
            {allCases.length === 0 && (
              <button onClick={() => setShowCreate(true)} className="btn-primary">
                Open First Case
              </button>
            )}
          </div>
        ) : (
          <div className="card p-0 overflow-hidden">
            {/* Table header */}
            <table className="w-full">
              <thead>
                <tr className="border-b border-wire" style={{ background: '#352720' }}>
                  <th className="w-1 p-0" />
                  <th className="py-2.5 pl-4 pr-3 text-left text-label w-44">Reference</th>
                  <th className="py-2.5 px-3 text-left text-label">Case Title</th>
                  <th className="py-2.5 px-3 text-left text-label w-28">Priority</th>
                  <th className="py-2.5 px-3 text-left text-label w-28">Status</th>
                  <th className="py-2.5 px-3 text-left text-label w-36">Updated</th>
                  <th className="w-8 p-0" />
                </tr>
              </thead>
              <tbody>
                {filtered.map((c) => <CaseRow key={c.id} c={c} />)}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showCreate && <CreateCaseModal onClose={() => setShowCreate(false)} />}
    </div>
  )
}
