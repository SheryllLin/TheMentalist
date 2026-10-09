import { useState, useCallback, useRef, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { graphApi } from '../../services/api'
import { GraphNode, GraphEdge, GraphData } from '../../types'
import {
  Loader2, Search, X, ZoomIn, ZoomOut, Maximize2,
  Network, Info, ChevronDown, ChevronUp,
} from 'lucide-react'
// @ts-ignore — react-force-graph-2d ships loose types
import ForceGraph2D from 'react-force-graph-2d'

// ── Mentalist investigation-board palette ─────────────────────
const NODE_PALETTE: Record<string, { bg: string; border: string; label: string }> = {
  Person:             { bg: '#8B6B47', border: '#AA9164', label: 'Person'         },
  Organization:       { bg: '#6B5A3E', border: '#8B7550', label: 'Organisation'   },
  Location:           { bg: '#4A5E47', border: '#6C7C68', label: 'Location'        },
  Phone:              { bg: '#5A4A6B', border: '#7A6A8B', label: 'Phone'           },
  BankAccount:        { bg: '#4A5E5A', border: '#6A7E7A', label: 'Bank Account'    },
  Transaction:        { bg: '#7A4A3A', border: '#9A6A5A', label: 'Transaction'     },
  Event:              { bg: '#6B4A2A', border: '#8B6A4A', label: 'Event'           },
  Vehicle:            { bg: '#5A6B3A', border: '#7A8B5A', label: 'Vehicle'         },
  SocialMediaAccount: { bg: '#5A5A6B', border: '#7A7A8B', label: 'Social Media'   },
  Document:           { bg: '#6B5A3E', border: '#8B7550', label: 'Document'        },
}
const DEFAULT_NODE = { bg: '#5A4A3A', border: '#7A6A5A', label: 'Entity' }

function nodeColor(n: GraphNode, selected: GraphNode | null, highlighted: Set<string>): string {
  const label = (n._labels as string[])?.[0] || 'Entity'
  const palette = NODE_PALETTE[label] || DEFAULT_NODE
  if (selected?.id === n.id) return '#CC1A1A'  // Red John red for selected
  if (highlighted.size > 0 && !highlighted.has(n.id as string)) return '#3D2820'
  return palette.bg
}

// ── NodeDetailPanel ───────────────────────────────────────────
function NodeDetailPanel({ node, caseId, onClose }: {
  node: GraphNode; caseId: string; onClose: () => void
}) {
  const { data, isLoading } = useQuery({
    queryKey: ['node', caseId, node.id],
    queryFn: () => graphApi.getNode(caseId, node.id as string),
    enabled: !!node.id,
  })
  const detail = data?.data
  const label = (node._labels as string[])?.[0] || 'Entity'
  const palette = NODE_PALETTE[label] || DEFAULT_NODE
  const [showEvidence, setShowEvidence] = useState(false)

  return (
    <div
      className="absolute right-0 top-0 bottom-0 w-72 flex flex-col z-10 border-l border-wire"
      style={{ background: '#2C1F1A' }}
    >
      {/* Header */}
      <div
        className="flex items-start justify-between px-4 py-3 border-b border-wire flex-shrink-0"
        style={{ borderTop: `2px solid ${palette.border}` }}
      >
        <div className="min-w-0 flex-1">
          <span
            className="text-[10px] font-mono uppercase tracking-widest mb-1 block"
            style={{ color: palette.border }}
          >
            {palette.label}
          </span>
          <p className="font-serif text-sm font-semibold text-cream leading-snug">
            {String(node.name || node.id || '—')}
          </p>
        </div>
        <button
          onClick={onClose}
          className="text-sepia hover:text-parchment transition-colors ml-2 flex-shrink-0"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs">
        {isLoading ? (
          <div className="flex items-center gap-2 text-sepia">
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
            <span className="font-mono">Loading profile…</span>
          </div>
        ) : (
          <>
            {/* Properties */}
            <div>
              <p className="text-label mb-2">Properties</p>
              <div className="space-y-1.5">
                {Object.entries(detail || node)
                  .filter(([k, v]) =>
                    !k.startsWith('_') &&
                    k !== 'connections' &&
                    k !== 'case_id' &&
                    v !== null && v !== '' && v !== undefined
                  )
                  .map(([k, v]) => (
                    <div key={k} className="flex gap-2 items-start">
                      <span className="text-sepia w-24 flex-shrink-0 capitalize font-sans">
                        {k.replace(/_/g, ' ')}
                      </span>
                      <span className="text-parchment break-all font-mono">
                        {Array.isArray(v) ? v.join(', ') || '—' : String(v || '—')}
                      </span>
                    </div>
                  ))}
              </div>
            </div>

            {/* Connections */}
            {detail?.connections?.length > 0 && (
              <div>
                <div className="divider" />
                <p className="text-label mb-2">
                  Connections ({detail.connections.length})
                </p>
                <div className="space-y-2">
                  {(detail.connections as Record<string, unknown>[]).slice(0, 12).map((c, i) => {
                    const nLabel = ((c.neighbor_labels as string[]) || [])[0] || 'Entity'
                    const nPalette = NODE_PALETTE[nLabel] || DEFAULT_NODE
                    const relProps = (c.rel_props as Record<string, unknown>) || {}
                    return (
                      <div
                        key={i}
                        className="rounded-file border border-wire p-2"
                        style={{ background: '#352720' }}
                      >
                        <div className="flex items-center gap-1.5 mb-1">
                          <span
                            className="w-2 h-2 rounded-full flex-shrink-0"
                            style={{ background: nPalette.border }}
                          />
                          <span className="text-parchment font-sans truncate">
                            {String(c.neighbor_name ?? '—')}
                          </span>
                        </div>
                        <p
                          className="font-mono text-[10px] tracking-wide uppercase mb-1"
                          style={{ color: palette.border }}
                        >
                          {String(c.rel_type ?? '')}
                        </p>
                        {!!relProps.evidence_text && (
                          <button
                            className="w-full text-left"
                            onClick={() => setShowEvidence((v) => !v)}
                          >
                            <div className="flex items-center gap-1 text-sepia/60">
                              <Info className="w-2.5 h-2.5 flex-shrink-0" />
                              <span className="text-[10px] font-mono">Evidence</span>
                              {showEvidence
                                ? <ChevronUp className="w-2.5 h-2.5" />
                                : <ChevronDown className="w-2.5 h-2.5" />}
                            </div>
                            {showEvidence && (
                              <p className="mt-1 text-[10px] text-sepia/80 font-garamond italic
                                            leading-relaxed line-clamp-3">
                                {String(relProps.evidence_text)}
                              </p>
                            )}
                          </button>
                        )}
                        {!!relProps.confidence && (
                          <div className="flex items-center gap-1.5 mt-1">
                            <div className="flex-1 h-0.5 bg-walnut rounded-full">
                              <div
                                className="h-full rounded-full"
                                style={{
                                  width: `${Number(relProps.confidence) * 100}%`,
                                  background: palette.border,
                                }}
                              />
                            </div>
                            <span className="text-[9px] font-mono text-sepia/60">
                              {(Number(relProps.confidence) * 100).toFixed(0)}%
                            </span>
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

// ── Main graph tab ────────────────────────────────────────────
export default function CaseGraphTab({ caseId }: { caseId: string }) {
  const graphRef = useRef<any>() // eslint-disable-line @typescript-eslint/no-explicit-any
  const containerRef = useRef<HTMLDivElement>(null)
  const [dims, setDims] = useState({ w: 800, h: 600 })
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [visibleLabels, setVisibleLabels] = useState<Set<string>>(new Set())
  const [highlightNodes, setHighlightNodes] = useState<Set<string>>(new Set())
  const prevLenRef = useRef(0)

  // Track container dimensions
  useEffect(() => {
    const el = containerRef.current
    if (!el) return
    const ro = new ResizeObserver((entries) => {
      const { width, height } = entries[0].contentRect
      setDims({
        w: width  - (selectedNode ? 288 : 0),
        h: height,
      })
    })
    ro.observe(el)
    return () => ro.disconnect()
  }, [selectedNode])

  const { data, isLoading, error } = useQuery({
    queryKey: ['graph', caseId],
    queryFn:  () => graphApi.getGraph(caseId),
    staleTime: 15_000,
  })

  const graphData: GraphData = data?.data ?? { nodes: [], edges: [] }
  const allLabels = Array.from(new Set(graphData.nodes.flatMap((n) => n._labels || [])))

  // Initialise visible labels once data arrives
  if (graphData.nodes.length > 0 && prevLenRef.current === 0) {
    prevLenRef.current = graphData.nodes.length
    setVisibleLabels(new Set(allLabels))
  }

  const filteredNodes = graphData.nodes.filter(
    (n) => visibleLabels.size === 0 || (n._labels || []).some((l) => visibleLabels.has(l))
  )
  const filteredIds = new Set(filteredNodes.map((n) => n.id))
  const filteredEdges = graphData.edges.filter(
    (e) => filteredIds.has(e.source as string) && filteredIds.has(e.target as string)
  )

  const handleSearch = useCallback((q: string) => {
    setSearchQuery(q)
    if (!q.trim()) { setHighlightNodes(new Set()); return }
    const ql = q.toLowerCase()
    setHighlightNodes(new Set(
      graphData.nodes
        .filter((n) => String(n.name || '').toLowerCase().includes(ql))
        .map((n) => n.id as string)
    ))
  }, [graphData.nodes])

  const toggleLabel = (label: string) => {
    setVisibleLabels((prev) => {
      const next = new Set(prev)
      next.has(label) ? next.delete(label) : next.add(label)
      return next
    })
  }

  /* ── Loading ─────────────────────────────────────────────── */
  if (isLoading) return (
    <div className="flex flex-col items-center justify-center h-full gap-3">
      <Loader2 className="w-6 h-6 animate-spin text-brass" />
      <p className="text-xs font-mono text-sepia">Building investigation board…</p>
    </div>
  )

  if (error) return (
    <div className="flex flex-col items-center justify-center h-full gap-2 text-burgundy-light">
      <Network className="w-8 h-8 opacity-40" />
      <p className="text-sm font-serif">Failed to load network graph</p>
    </div>
  )

  if (filteredNodes.length === 0) return (
    <div className="flex flex-col items-center justify-center h-full text-center gap-3 px-6">
      <Network className="w-12 h-12 text-sepia/20" />
      <div>
        <p className="font-serif text-base text-parchment mb-1">
          Investigation board is empty
        </p>
        <p className="text-xs text-sepia font-sans">
          Upload evidence files and process them to populate the network.
        </p>
      </div>
    </div>
  )

  return (
    <div className="relative flex flex-col h-full" style={{ background: '#1A1210' }}>

      {/* ── Toolbar ──────────────────────────────────────────── */}
      <div
        className="flex items-center gap-3 px-4 py-2 border-b border-wire flex-wrap flex-shrink-0"
        style={{ background: '#2C1F1A' }}
      >
        {/* Search */}
        <div
          className="flex items-center gap-2 rounded-file border border-wire px-2 py-1 w-52"
          style={{ background: '#352720' }}
        >
          <Search className="w-3.5 h-3.5 text-sepia/60 flex-shrink-0" />
          <input
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            placeholder="Find entity…"
            className="bg-transparent text-sm text-cream placeholder-sepia/50
                       outline-none flex-1 font-sans"
          />
          {searchQuery && (
            <button onClick={() => handleSearch('')}>
              <X className="w-3 h-3 text-sepia/60 hover:text-sepia" />
            </button>
          )}
        </div>

        {/* Entity type filters */}
        <div className="flex items-center gap-1 flex-wrap">
          {allLabels.map((label) => {
            const p = NODE_PALETTE[label] || DEFAULT_NODE
            const active = visibleLabels.has(label)
            return (
              <button
                key={label}
                onClick={() => toggleLabel(label)}
                className="flex items-center gap-1 px-2 py-0.5 rounded-stamp
                           text-[10px] font-mono uppercase tracking-wide
                           border transition-opacity duration-150"
                style={{
                  background: active ? p.bg + '40' : 'transparent',
                  borderColor: active ? p.border + '80' : 'rgba(169,144,100,0.15)',
                  color: active ? p.border : 'rgba(169,144,100,0.35)',
                  opacity: active ? 1 : 0.5,
                }}
              >
                <span
                  className="w-1.5 h-1.5 rounded-full flex-shrink-0"
                  style={{ background: active ? p.border : 'rgba(169,144,100,0.3)' }}
                />
                {label}
              </button>
            )
          })}
        </div>

        {/* Right controls */}
        <div className="ml-auto flex items-center gap-2">
          <button
            className="btn-ghost py-1 px-2 flex items-center gap-1 text-xs"
            onClick={() => graphRef.current?.zoomToFit(400)}
            title="Fit to view"
          >
            <Maximize2 className="w-3.5 h-3.5" />
            Fit
          </button>
          <button
            className="btn-ghost py-1 px-1.5"
            onClick={() => graphRef.current?.zoom(1.4, 300)}
            title="Zoom in"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
          <button
            className="btn-ghost py-1 px-1.5"
            onClick={() => graphRef.current?.zoom(0.7, 300)}
            title="Zoom out"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <span className="text-[10px] font-mono text-sepia/60 ml-1">
            {filteredNodes.length} nodes · {filteredEdges.length} edges
          </span>
        </div>
      </div>

      {/* ── Canvas + detail panel ─────────────────────────────── */}
      <div className="relative flex-1" ref={containerRef}>
        <ForceGraph2D
          ref={graphRef}
          graphData={{
            nodes: filteredNodes as never[],
            links: filteredEdges as never[],
          }}
          nodeId="id"
          linkSource="source"
          linkTarget="target"
          width={dims.w}
          height={dims.h}
          backgroundColor="#1A1210"
          /* ── node rendering ── */
          nodeCanvasObject={(node: unknown, ctx: CanvasRenderingContext2D, globalScale: number) => {
            const n = node as GraphNode & { x?: number; y?: number }
            const x = n.x ?? 0
            const y = n.y ?? 0
            const label = (n._labels as string[])?.[0] || 'Entity'
            const palette = NODE_PALETTE[label] || DEFAULT_NODE
            const isSelected = selectedNode?.id === n.id
            const isDimmed = highlightNodes.size > 0 && !highlightNodes.has(n.id as string)
            const r = isSelected ? 8 : 6

            // Node circle
            ctx.beginPath()
            ctx.arc(x, y, r, 0, Math.PI * 2)
            ctx.fillStyle = isDimmed ? '#2C1F1A' : (isSelected ? '#CC1A1A' : palette.bg)
            ctx.fill()
            // Border
            ctx.strokeStyle = isDimmed ? '#3D2820' : (isSelected ? '#E84040' : palette.border)
            ctx.lineWidth = isSelected ? 2 : 1.5
            ctx.stroke()

            // Label (only at reasonable zoom)
            if (globalScale > 0.8 && !isDimmed) {
              const name = String(n.name || n.id || '')
              const display = name.length > 18 ? name.slice(0, 16) + '…' : name
              ctx.font = isSelected
                ? `bold ${11 / globalScale}px "IBM Plex Mono"`
                : `${10 / globalScale}px "IBM Plex Mono"`
              ctx.textAlign = 'center'
              ctx.textBaseline = 'top'
              ctx.fillStyle = isDimmed ? '#5A4A3A' : (isSelected ? '#F5E6D0' : '#D7C7A8')
              ctx.fillText(display, x, y + r + 3 / globalScale)
            }
          }}
          nodePointerAreaPaint={(node: unknown, color: string, ctx: CanvasRenderingContext2D) => {
            const n = node as GraphNode & { x?: number; y?: number }
            ctx.beginPath()
            ctx.arc(n.x ?? 0, n.y ?? 0, 10, 0, Math.PI * 2)
            ctx.fillStyle = color
            ctx.fill()
          }}
          /* ── link rendering ── */
          linkCanvasObject={(link: unknown, ctx: CanvasRenderingContext2D) => {
            const l = link as GraphEdge & {
              source: { x?: number; y?: number; id?: string }
              target: { x?: number; y?: number; id?: string }
            }
            const sx = (l.source as { x?: number }).x ?? 0
            const sy = (l.source as { y?: number }).y ?? 0
            const tx = (l.target as { x?: number }).x ?? 0
            const ty = (l.target as { y?: number }).y ?? 0

            const conf = typeof l.confidence === 'number' ? l.confidence : 0.8
            const alpha = 0.15 + conf * 0.35

            ctx.beginPath()
            ctx.moveTo(sx, sy)
            ctx.lineTo(tx, ty)
            ctx.strokeStyle = `rgba(170,145,100,${alpha})`
            ctx.lineWidth = conf > 0.85 ? 1.5 : 1
            // Dashed for lower-confidence links
            if (conf < 0.6) ctx.setLineDash([3, 4])
            else ctx.setLineDash([])
            ctx.stroke()
            ctx.setLineDash([])
          }}
          linkDirectionalArrowLength={4}
          linkDirectionalArrowRelPos={1}
          linkDirectionalArrowColor={() => 'rgba(170,145,100,0.45)'}
          onNodeClick={(node: unknown) => setSelectedNode(node as GraphNode)}
          onBackgroundClick={() => setSelectedNode(null)}
          cooldownTicks={120}
          linkLabel={(l: unknown) => {
            const edge = l as GraphEdge
            return `${edge.type || ''}${edge.confidence ? ` (${(Number(edge.confidence)*100).toFixed(0)}%)` : ''}`
          }}
        />

        {/* Node detail panel */}
        {selectedNode && (
          <NodeDetailPanel
            node={selectedNode}
            caseId={caseId}
            onClose={() => setSelectedNode(null)}
          />
        )}
      </div>
    </div>
  )
}
