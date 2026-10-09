import { useQuery } from '@tanstack/react-query'
import { graphApi } from '../../services/api'
import { TimelineEvent } from '../../types'
import { Loader2, Phone, DollarSign, MapPin, AlertTriangle, Calendar, Clock, Users } from 'lucide-react'

const EVENT_META: Record<string, { icon: React.ReactNode; color: string; borderColor: string }> = {
  MEETING:     { icon: <Users       className="w-4 h-4" />, color: '#8B7550', borderColor: '#AA9164' },
  CALL:        { icon: <Phone       className="w-4 h-4" />, color: '#5A4A6B', borderColor: '#7A6A8B' },
  TRANSACTION: { icon: <DollarSign  className="w-4 h-4" />, color: '#7A4A3A', borderColor: '#9A6A5A' },
  TRAVEL:      { icon: <MapPin      className="w-4 h-4" />, color: '#4A5E47', borderColor: '#6C7C68' },
  ARREST:      { icon: <AlertTriangle className="w-4 h-4" />, color: '#7A2D35', borderColor: '#9B3D46' },
  INCIDENT:    { icon: <AlertTriangle className="w-4 h-4" />, color: '#7A2D35', borderColor: '#9B3D46' },
  OTHER:       { icon: <Clock       className="w-4 h-4" />, color: '#6B5A3E', borderColor: '#8B7550' },
}
const DEFAULT_META = EVENT_META.OTHER

function EventCard({ event }: { event: TimelineEvent }) {
  const meta = EVENT_META[event.event_type] || DEFAULT_META

  return (
    <div className="flex gap-4">
      {/* Timeline stem */}
      <div className="flex flex-col items-center flex-shrink-0">
        <div
          className="w-8 h-8 rounded-full border-2 flex items-center justify-center"
          style={{
            background:   meta.color + '30',
            borderColor:  meta.borderColor,
            color:        meta.borderColor,
          }}
        >
          {meta.icon}
        </div>
        <div className="w-px flex-1 mt-1" style={{ background: 'rgba(169,144,100,0.12)' }} />
      </div>

      {/* Card */}
      <div className="pb-5 flex-1 min-w-0">
        <div
          className="rounded-file border p-3"
          style={{ background: '#352720', borderColor: meta.color + '40' }}
        >
          {/* Header */}
          <div className="flex items-center justify-between gap-2 mb-1.5 flex-wrap">
            <span
              className="text-[9px] font-mono uppercase tracking-widest"
              style={{ color: meta.borderColor }}
            >
              {event.event_type}
            </span>
            {event.timestamp && (
              <span className="text-[10px] font-mono text-sepia/70 flex items-center gap-1">
                <Calendar className="w-2.5 h-2.5" />
                {event.timestamp}
              </span>
            )}
          </div>

          {/* Name */}
          <p className="font-serif text-sm font-semibold text-cream leading-snug mb-1">
            {event.name}
          </p>

          {/* Description */}
          {event.description && (
            <p className="text-xs text-sepia font-sans leading-relaxed">
              {event.description}
            </p>
          )}

          {/* Location */}
          {event.location && (
            <p className="text-xs text-sepia/70 mt-1.5 flex items-center gap-1 font-mono">
              <MapPin className="w-3 h-3 flex-shrink-0" />
              {event.location}
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

export default function CaseTimelineTab({ caseId }: { caseId: string }) {
  const { data, isLoading } = useQuery({
    queryKey: ['timeline', caseId],
    queryFn:  () => graphApi.timeline(caseId),
  })
  const events: TimelineEvent[] = data?.data?.events ?? []

  if (isLoading) return (
    <div className="flex items-center justify-center py-20">
      <Loader2 className="w-5 h-5 animate-spin text-brass" />
    </div>
  )

  if (events.length === 0) return (
    <div className="flex flex-col items-center justify-center py-20 text-center gap-3 px-6">
      <Clock className="w-10 h-10 text-sepia/20" />
      <div>
        <p className="font-serif text-base text-parchment mb-1">No events on record</p>
        <p className="text-xs text-sepia font-sans">
          Events are extracted automatically when you process evidence documents.
        </p>
      </div>
    </div>
  )

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h2 className="font-serif text-base font-semibold text-cream">Event Timeline</h2>
          <p className="text-xs text-sepia font-sans mt-0.5">
            {events.length} events · chronological order
          </p>
        </div>
      </div>
      <div className="max-w-2xl">
        {events.map((e) => <EventCard key={e.id} event={e} />)}
      </div>
    </div>
  )
}
