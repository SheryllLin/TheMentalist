import { Case } from '../../types'
import { format } from 'date-fns'
import {
  Calendar, Hash, Flag, Activity, FileText,
  Network, Clock, AlertTriangle,
} from 'lucide-react'

const PRIORITY_CLASS: Record<string, string> = {
  CRITICAL: 'badge-critical', HIGH: 'badge-high',
  MEDIUM: 'badge-medium',    LOW:  'badge-low',
}

function MetaRow({ icon, label, value }: {
  icon: React.ReactNode; label: string; value: React.ReactNode
}) {
  return (
    <div className="flex items-start gap-3 py-2.5 border-b border-wire/60 last:border-0">
      <span className="text-sepia/60 mt-0.5 flex-shrink-0">{icon}</span>
      <span className="text-sepia text-xs font-sans w-32 flex-shrink-0 pt-0.5">{label}</span>
      <span className="text-cream text-xs font-mono flex-1">{value}</span>
    </div>
  )
}

export default function CaseOverviewTab({ caseData }: { caseData: Case }) {
  return (
    <div className="p-6 max-w-4xl">

      {/* ── Section: Case Identity ── */}
      <div className="mb-6">
        <p className="text-label mb-3">Case Identity</p>
        <div className="card">
          <MetaRow
            icon={<Hash className="w-3.5 h-3.5" />}
            label="Reference Number"
            value={<span className="text-brass">{caseData.case_number}</span>}
          />
          <MetaRow
            icon={<Flag className="w-3.5 h-3.5" />}
            label="Priority"
            value={<span className={PRIORITY_CLASS[caseData.priority]}>{caseData.priority}</span>}
          />
          <MetaRow
            icon={<Activity className="w-3.5 h-3.5" />}
            label="Status"
            value={<span className={`badge-${caseData.status.toLowerCase()}`}>{caseData.status}</span>}
          />
          <MetaRow
            icon={<Calendar className="w-3.5 h-3.5" />}
            label="Opened"
            value={format(new Date(caseData.created_at), 'dd MMMM yyyy, HH:mm')}
          />
          <MetaRow
            icon={<Clock className="w-3.5 h-3.5" />}
            label="Last Updated"
            value={format(new Date(caseData.updated_at), 'dd MMMM yyyy, HH:mm')}
          />
        </div>
      </div>

      {/* ── Section: Case Summary ── */}
      {caseData.description && (
        <div className="mb-6">
          <p className="text-label mb-3">Investigation Summary</p>
          <div className="card">
            <p className="font-garamond text-sm text-parchment leading-relaxed italic">
              "{caseData.description}"
            </p>
          </div>
        </div>
      )}

      {/* ── Section: Getting started ── */}
      <div>
        <p className="text-label mb-3">Investigation Workflow</p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {[
            {
              icon: <FileText className="w-4 h-4" />,
              title: 'Upload Evidence',
              desc:  'Upload reports, call records, and financial documents in the Evidence Files tab.',
              tab:   'documents',
            },
            {
              icon: <Network className="w-4 h-4" />,
              title: 'Build the Network',
              desc:  'Once documents are processed, entities and relationships appear on the Investigation Board.',
              tab:   'graph',
            },
            {
              icon: <AlertTriangle className="w-4 h-4" />,
              title: 'Query Intelligence',
              desc:  'Ask the Intelligence AI questions grounded in the extracted evidence.',
              tab:   'assistant',
            },
          ].map(({ icon, title, desc }) => (
            <div key={title} className="card">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-brass">{icon}</span>
                <p className="font-serif text-sm font-semibold text-cream">{title}</p>
              </div>
              <p className="text-xs text-sepia font-sans leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
