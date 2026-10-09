import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { casesApi } from '../services/api'
import { Case, CasePriority, CaseStatus } from '../types'
import {
  Plus, AlertTriangle, Clock, CheckCircle, Archive,
  ChevronRight, Loader2, X, FolderOpen, Activity,
  Calendar, User, Hash,
} from 'lucide-react'
import { format, formatDistanceToNow } from 'date-fns'

// ── helpers ──────────────────────────────────────────────────
const PRIORITY_LABEL: Record<CasePriority, string> = {
  CRITICAL: 'CRITICAL', HIGH: 'HIGH', MEDIUM: 'MEDIUM', LOW: 'LOW',
}
const PRIORITY_CLASS: Record<CasePriority, string> = {
  CRITICAL: 'badge-critical',
  HIGH:     'badge-high',
  MEDIUM:   'badge-medium',
  LOW:      'badge-low',
}
const STATUS_CLASS: Record<CaseStatus, string> = {
  ACTIVE:   'badge-active',
  CLOSED:   'badge-closed',
  ARCHIVED: 'badge-archived',
}
const STATUS_ICON: Record<CaseStatus, React.ReactNode> = {
  ACTIVE:   <Activity className="w-3 h-3" />,
  CLOSED:   <CheckCircle className="w-3 h-3" />,
  ARCHIVED: <Archive className="w-3 h-3" />,
}

// ── CaseFileCard ─────────────────────────────────────────────
function CaseFileCard({ c }: { c: Case }) {
  const navigate = useNavigate()
  const statusClass = c.status === 'CLOSED' ? 'status-closed' :
                      c.status === 'ARCHIVED' ? 'status-archived' : ''

  return (
    <div
      onClick={() => navigate(`/cases/${c.id}/overview`)}
      className={`case-file ${statusClass} group`}
    >
      {/* Top row: case number + priority */}
      <div className="flex items-start justify-between mb-2.5">
        <span className="text-mono-id flex items-center gap-1">
          <Hash className="w-2.5 h-2.5 opacity-60" />
          {c.case_number}
        </span>
        <span className={PRIORITY_CLASS[c.priority]}>
          {PRIORITY_LABEL[c.priority]}
        </span>
      </div>

      {/* Title */}
      <h3 className="font-serif text-sm font-semibold text-cream mb-1.5
                     group-hover:text-white transition-colors leading-snug">
        {c.title}
      </h3>

      {/* Description */}
      {c.description && (
        <p className="text-xs text-sepia leading-relaxed line-clamp-2 mb-3 font-sans">
          {c.description}
        </p>
      )}

      {/* Bottom row */}
      <div className="flex items-center justify-between pt-2 border-t border-wire/60">
        <span className={`${STATUS_CLASS[c.status]} flex items-center gap-1`}>
          {STATUS_ICON[c.status]}
          {c.status}
        </span>
        <div className="flex items-center gap-1.5 text-xs text-sepia/70 font-mono">
          <Calendar className="w-3 h-3 opacity-60" />
          {format(new Date(c.updated_at), 'dd MMM yyyy')}
          <ChevronRight className="w-3 h-3 opacity-0 group-hover:opacity-70
                                   transition-opacity" />
        </div>
      </div>
    </div>
  )
}

// ── StatCard ─────────────────────────────────────────────────
function StatCard({
  label, value, sub, accent = false,
}: { label: string; value: number | string; sub?: string; accent?: boolean }) {
  return (
    <div className={`card relative overflow-hidden ${accent ? 'border-burgundy/40' : ''}`}>
      {accent && (
        <div className="absolute top-0 left-0 right-0 h-px
                        bg-gradient-to-r from-transparent via-burgundy/60 to-transparent" />
      )}
      <p className={`font-mono text-3xl font-semibold tabular-nums
                     ${accent ? 'text-burgundy-light' : 'text-brass'}`}>
        {value}
      </p>
      <p className="text-label mt-1">{label}</p>
      {sub && <p className="text-xs text-sepia/60 font-mono mt-0.5">{sub}</p>}
    </div>
  )
}

// ── CreateCaseModal ───────────────────────────────────────────
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

        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-wire">
          <div>
            <h2 className="font-serif text-base font-semibold text-cream">
              Open New Investigation
            </h2>
            <p className="text-xs text-sepia mt-0.5 font-sans">
              A new case file will be created and assigned a reference number.
            </p>
          </div>
          <button onClick={onClose} className="text-sepia hover:text-parchment transition-colors">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Form */}
        <div className="px-5 py-4 space-y-4">
          <div>
            <label className="text-label block mb-1.5">Case Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="input-field"
              placeholder="e.g. Suspected Organised Fraud Network"
              autoFocus
            />
          </div>
          <div>
            <label className="text-label block mb-1.5">Summary</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="input-field resize-none h-20"
              placeholder="Brief description of the investigation…"
            />
          </div>
          <div>
            <label className="text-label block mb-1.5">Priority Classification</label>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value as CasePriority)}
              className="input-field"
            >
              {(['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'] as CasePriority[]).map((p) => (
                <option key={p} value={p} className="bg-walnut">{p}</option>
              ))}
            </select>
          </div>

          {error && (
            <p className="text-xs text-burgundy-light bg-burgundy/10
                          border border-burgundy/30 rounded-file px-3 py-2">
              Failed to create case. Please try again.
            </p>
          )}
        </div>

        {/* Actions */}
        <div className="flex gap-3 px-5 py-4 border-t border-wire">
          <button onClick={onClose} className="btn-secondary flex-1">Cancel</button>
          <button
            onClick={() => mutate()}
            disabled={!title.trim() || isPending}
            className="btn-primary flex-1 flex items-center justify-center gap-2
                       disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {isPending
              ? <><Loader2 className="w-4 h-4 animate-spin" /> Opening…</>
              : <><Plus className="w-4 h-4" /> Open Case</>
            }
          </button>
        </div>
      </div>
    </div>
  )
}

// ── Main Dashboard ────────────────────────────────────────────
export default function DashboardPage() {
  const [showCreate, setShowCreate] = useState(false)
  const { data, isLoading, error } = useQuery({
    queryKey: ['cases'],
    queryFn: () => casesApi.list(),
  })

  const cases    = data?.data?.cases ?? []
  const total    = data?.data?.total ?? 0
  const active   = cases.filter((c) => c.status === 'ACTIVE').length
  const closed   = cases.filter((c) => c.status === 'CLOSED').length
  const critical = cases.filter((c) => c.priority === 'CRITICAL').length
  const recent   = [...cases]
    .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
    .slice(0, 3)

  return (
    <div className="min-h-full bg-parchment-texture">

      {/* ── Page header ────────────────────────────────────────── */}
      <div className="px-8 pt-7 pb-5 border-b border-wire">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-label mb-1">Intelligence Operations</p>
            <h1 className="font-serif text-2xl font-bold text-cream tracking-tight">
              Investigation Dashboard
            </h1>
            <p className="font-garamond italic text-sm text-sepia mt-1">
              "Every connection leaves a trace."
            </p>
          </div>
          <button
            onClick={() => setShowCreate(true)}
            className="btn-primary flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Open New Case
          </button>
        </div>
      </div>

      <div className="px-8 py-6 space-y-7">

        {/* ── Stat strip ───────────────────────────────────────── */}
        {isLoading ? (
          <div className="grid grid-cols-4 gap-4">
            {[1,2,3,4].map((i) => (
              <div key={i} className="skeleton h-20 rounded-file" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <StatCard label="Total Cases"       value={total}    />
            <StatCard label="Active"            value={active}   sub="under investigation" />
            <StatCard label="Resolved"          value={closed}   />
            <StatCard label="Critical Priority" value={critical} accent />
          </div>
        )}

        {/* ── Two-column layout ────────────────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          {/* Left: case file grid (2/3 width) */}
          <div className="lg:col-span-2">
            <div className="flex items-center justify-between mb-3">
              <h2 className="font-serif text-base font-semibold text-cream">
                Active Case Files
              </h2>
              {total > 6 && (
                <button
                  onClick={() => {/* navigate to /cases */}}
                  className="text-xs text-brass hover:text-parchment font-mono
                             flex items-center gap-1 transition-colors"
                >
                  View all {total} <ChevronRight className="w-3 h-3" />
                </button>
              )}
            </div>

            {isLoading ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {[1,2,3,4].map((i) => (
                  <div key={i} className="skeleton h-36 rounded-file" />
                ))}
              </div>
            ) : error ? (
              <div className="card flex items-center gap-3 text-burgundy-light">
                <AlertTriangle className="w-5 h-5 flex-shrink-0" />
                <div>
                  <p className="text-sm font-medium">Failed to load cases</p>
                  <p className="text-xs text-sepia mt-0.5">Check backend connectivity</p>
                </div>
              </div>
            ) : cases.length === 0 ? (
              <div className="card text-center py-12">
                <FolderOpen className="w-10 h-10 text-sepia/30 mx-auto mb-3" />
                <p className="font-serif text-base text-parchment mb-1">
                  No cases on file
                </p>
                <p className="text-xs text-sepia mb-4 font-sans">
                  Open a new investigation to begin.
                </p>
                <button onClick={() => setShowCreate(true)} className="btn-primary">
                  Open First Case
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {cases.slice(0, 8).map((c) => (
                  <CaseFileCard key={c.id} c={c} />
                ))}
              </div>
            )}
          </div>

          {/* Right: activity feed (1/3 width) */}
          <div className="space-y-4">

            {/* Recent activity */}
            <div>
              <h2 className="font-serif text-base font-semibold text-cream mb-3">
                Recent Activity
              </h2>
              <div className="space-y-1">
                {isLoading ? (
                  [1,2,3].map((i) => <div key={i} className="skeleton h-12 rounded-file" />)
                ) : recent.length === 0 ? (
                  <p className="text-xs text-sepia/60 font-mono px-1">No activity yet</p>
                ) : (
                  recent.map((c) => (
                    <button
                      key={c.id}
                      onClick={() => {
                        const navigate = (window as Window & { __navigate?: (path: string) => void }).__navigate
                        // React Router navigate isn't directly accessible here;
                        // use a simple link-style approach
                        window.location.href = `/cases/${c.id}/overview`
                      }}
                      className="w-full text-left flex items-start gap-3 px-3 py-2.5
                                 rounded-file hover:bg-walnut/60 transition-colors group"
                    >
                      <div className="w-7 h-7 rounded-full bg-mahogany border border-wire
                                      flex items-center justify-center flex-shrink-0 mt-0.5">
                        <User className="w-3.5 h-3.5 text-sepia" />
                      </div>
                      <div className="min-w-0">
                        <p className="text-xs font-medium text-parchment truncate
                                      group-hover:text-cream transition-colors">
                          {c.title}
                        </p>
                        <p className="text-[10px] font-mono text-sepia/60 mt-0.5 flex items-center gap-1">
                          <Clock className="w-2.5 h-2.5" />
                          {formatDistanceToNow(new Date(c.updated_at), { addSuffix: true })}
                        </p>
                      </div>
                    </button>
                  ))
                )}
              </div>
            </div>

            {/* Status breakdown */}
            {!isLoading && cases.length > 0 && (
              <div className="card">
                <h3 className="text-label mb-3">Case Status Overview</h3>
                <div className="space-y-2.5">
                  {[
                    { label: 'Active',   count: active,                     color: 'bg-status-active'   },
                    { label: 'Resolved', count: closed,                     color: 'bg-status-closed'   },
                    { label: 'Archived', count: total - active - closed,    color: 'bg-status-archived' },
                  ].map(({ label, count, color }) => (
                    <div key={label}>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-sepia font-sans">{label}</span>
                        <span className="font-mono text-brass">{count}</span>
                      </div>
                      <div className="h-1 bg-walnut rounded-full overflow-hidden">
                        <div
                          className={`h-full ${color} rounded-full transition-all duration-700`}
                          style={{ width: total > 0 ? `${(count / total) * 100}%` : '0%' }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* CBI notice card */}
            <div className="card border-burgundy/20 bg-burgundy/5">
              <div className="flex items-start gap-2.5">
                <img
                  src="/assets/red-john.svg"
                  alt=""
                  className="w-7 h-7 opacity-40 flex-shrink-0 mt-0.5"
                />
                <div>
                  <p className="text-xs font-serif font-semibold text-parchment mb-1">
                    THE MENTALIST
                  </p>
                  <p className="text-[11px] text-sepia leading-relaxed font-garamond italic">
                    Criminal Intelligence &amp; Network Analysis System. All case data is
                    classified. Authorised access only.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {showCreate && <CreateCaseModal onClose={() => setShowCreate(false)} />}
    </div>
  )
}
