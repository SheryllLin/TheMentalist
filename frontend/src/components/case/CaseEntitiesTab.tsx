import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { graphApi } from '../../services/api'
import { Loader2, Search, ChevronDown, ChevronUp, Users } from 'lucide-react'

const ENTITY_TYPES = [
  'Person', 'Organization', 'Location', 'Phone',
  'BankAccount', 'Transaction', 'Vehicle', 'Event', 'SocialMediaAccount',
]

const TYPE_COLOR: Record<string, string> = {
  Person:             '#AA9164',
  Organization:       '#8B7550',
  Location:           '#6C7C68',
  Phone:              '#7A6A8B',
  BankAccount:        '#6A7E7A',
  Transaction:        '#9A6A5A',
  Event:              '#8B6A4A',
  Vehicle:            '#7A8B5A',
  SocialMediaAccount: '#7A7A8B',
}

function EntityRow({ entity }: { entity: Record<string, unknown> }) {
  const [expanded, setExpanded] = useState(false)
  const name    = String(entity.name || entity.id || '—')
  const labels  = (entity._labels as string[]) || []
  const label   = labels[0] || 'Entity'
  const color   = TYPE_COLOR[label] || '#AA9164'

  const props = Object.entries(entity).filter(
    ([k, v]) => !k.startsWith('_') && k !== 'case_id' && v !== null && v !== '' && v !== undefined
  )

  return (
    <div className="border-b border-wire/60 last:border-0">
      <button
        onClick={() => setExpanded((v) => !v)}
        className="w-full flex items-center gap-3 px-4 py-2.5
                   hover:bg-walnut/40 transition-colors text-left"
      >
        {/* Color dot */}
        <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: color }} />

        {/* Type badge */}
        <span
          className="text-[9px] font-mono uppercase tracking-widest w-24 flex-shrink-0"
          style={{ color }}
        >
          {label}
        </span>

        {/* Name */}
        <span className="text-sm text-parchment flex-1 truncate font-sans">
          {name}
        </span>

        {/* Expand toggle */}
        {props.length > 1 && (
          expanded
            ? <ChevronUp   className="w-3.5 h-3.5 text-sepia/50 flex-shrink-0" />
            : <ChevronDown className="w-3.5 h-3.5 text-sepia/50 flex-shrink-0" />
        )}
      </button>

      {expanded && (
        <div
          className="px-4 pb-3 grid grid-cols-2 gap-x-6 gap-y-1.5 text-xs"
          style={{ background: '#352720' }}
        >
          {props.map(([k, v]) => (
            <div key={k} className="flex gap-2 min-w-0">
              <span className="text-sepia/70 font-sans capitalize flex-shrink-0 w-28 truncate">
                {k.replace(/_/g, ' ')}
              </span>
              <span className="text-parchment font-mono truncate">
                {Array.isArray(v) ? (v as unknown[]).join(', ') || '—' : String(v)}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default function CaseEntitiesTab({ caseId }: { caseId: string }) {
  const [selectedType, setSelectedType] = useState<string | null>(null)
  const [searchQ, setSearchQ] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['entities', caseId, selectedType],
    queryFn:  () => graphApi.entities(caseId, selectedType || undefined),
  })

  const entities = (data?.data?.entities ?? []) as Record<string, unknown>[]
  const filtered = searchQ
    ? entities.filter((e) =>
        String(e.name || '').toLowerCase().includes(searchQ.toLowerCase())
      )
    : entities

  return (
    <div className="p-6">

      {/* Toolbar */}
      <div className="flex items-center gap-3 mb-4 flex-wrap">
        <div
          className="flex items-center gap-2 rounded-file border border-wire px-2 py-1.5 w-52"
          style={{ background: '#352720' }}
        >
          <Search className="w-3.5 h-3.5 text-sepia/60 flex-shrink-0" />
          <input
            value={searchQ}
            onChange={(e) => setSearchQ(e.target.value)}
            placeholder="Search entities…"
            className="bg-transparent text-sm text-cream placeholder-sepia/50 outline-none flex-1 font-sans"
          />
        </div>

        {/* Type pills */}
        <div className="flex gap-1.5 flex-wrap">
          <button
            onClick={() => setSelectedType(null)}
            className={`text-xs font-mono px-2.5 py-0.5 rounded-stamp border transition-colors ${
              !selectedType
                ? 'bg-brass/20 border-brass/50 text-brass'
                : 'border-wire text-sepia hover:text-parchment'
            }`}
          >
            All
          </button>
          {ENTITY_TYPES.map((t) => {
            const active = selectedType === t
            const color  = TYPE_COLOR[t] || '#AA9164'
            return (
              <button
                key={t}
                onClick={() => setSelectedType(active ? null : t)}
                className="text-[10px] font-mono px-2 py-0.5 rounded-stamp border transition-all"
                style={{
                  background:  active ? color + '25' : 'transparent',
                  borderColor: active ? color + '70' : 'rgba(169,144,100,0.2)',
                  color:       active ? color       : 'rgba(169,144,100,0.5)',
                }}
              >
                {t}
              </button>
            )
          })}
        </div>
      </div>

      {/* Count */}
      <p className="text-label mb-2">{filtered.length} entities</p>

      {/* Table */}
      <div className="card p-0 overflow-hidden">
        {isLoading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="w-5 h-5 animate-spin text-brass" />
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-12">
            <Users className="w-8 h-8 text-sepia/20 mx-auto mb-2" />
            <p className="text-sm font-serif text-parchment">No entities found</p>
            <p className="text-xs text-sepia mt-1">
              {entities.length === 0
                ? 'Process a document to extract entities'
                : 'Try a different filter'}
            </p>
          </div>
        ) : (
          filtered.map((e, i) => (
            <EntityRow key={(e.id as string) || String(i)} entity={e} />
          ))
        )}
      </div>
    </div>
  )
}
