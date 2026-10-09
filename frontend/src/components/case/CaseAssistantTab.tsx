import { useState, useRef, useEffect } from 'react'
import { investigationApi } from '../../services/api'
import { InvestigationAnswer } from '../../types'
import {
  Send, Loader2, ChevronDown, ChevronUp, AlertCircle, Scroll,
} from 'lucide-react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  answer?: InvestigationAnswer
  error?: string
}

const SUGGESTED = [
  'Who is the most connected person in this case?',
  'Show all persons of interest.',
  'What financial transactions are recorded?',
  'Summarise the case network.',
]

function EvidenceDrawer({ evidence, total }: {
  evidence: Record<string, unknown>[]; total: number
}) {
  const [open, setOpen] = useState(false)
  if (evidence.length === 0) return null
  return (
    <div className="mt-3 border border-wire rounded-file overflow-hidden">
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between px-3 py-2
                   text-xs font-mono text-sepia hover:text-parchment transition-colors"
        style={{ background: '#352720' }}
      >
        <span className="flex items-center gap-1.5">
          <Scroll className="w-3 h-3" />
          Source evidence · {total} record{total !== 1 ? 's' : ''}
        </span>
        {open ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
      </button>
      {open && (
        <div
          className="px-3 py-2 space-y-1.5 max-h-52 overflow-y-auto"
          style={{ background: '#2C1F1A' }}
        >
          {evidence.slice(0, 10).map((row, i) => (
            <div
              key={i}
              className="rounded-file border border-wire px-2 py-1.5 text-[10px] font-mono"
              style={{ background: '#352720' }}
            >
              {Object.entries(row)
                .filter(([, v]) => v !== null && v !== '' && v !== undefined)
                .slice(0, 5)
                .map(([k, v]) => (
                  <span key={k} className="mr-3 inline-block">
                    <span className="text-sepia/60">{k}: </span>
                    <span className="text-parchment">{String(v).slice(0, 60)}</span>
                  </span>
                ))}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function Bubble({ msg }: { msg: Message }) {
  if (msg.role === 'user') {
    return (
      <div className="flex justify-end">
        <div
          className="max-w-md px-4 py-2.5 rounded-file border"
          style={{
            background: '#5C2028',
            borderColor: 'rgba(122,45,53,0.5)',
          }}
        >
          <p className="text-sm text-cream font-sans">{msg.content}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex items-start gap-3">
      {/* Avatar */}
      <div
        className="w-7 h-7 rounded-full flex items-center justify-center
                   border flex-shrink-0 mt-0.5"
        style={{ background: '#352720', borderColor: 'rgba(169,144,100,0.3)' }}
      >
        <img
          src="/assets/red-john.svg"
          alt="AI"
          className="w-4 h-4 opacity-70"
        />
      </div>

      <div className="flex-1 max-w-2xl min-w-0">
        {msg.error ? (
          <div
            className="flex items-center gap-2 text-sm px-4 py-2.5 rounded-file border"
            style={{ background: '#3D1A1A', borderColor: 'rgba(122,45,53,0.4)' }}
          >
            <AlertCircle className="w-4 h-4 text-burgundy-light flex-shrink-0" />
            <span className="text-burgundy-light text-xs">{msg.error}</span>
          </div>
        ) : (
          <div className="card">
            {msg.answer?.query_strategy && (
              <p className="text-[10px] font-mono text-sepia/50 mb-2 tracking-wide uppercase">
                Query: {msg.answer.query_strategy}
              </p>
            )}
            <p className="text-sm text-parchment whitespace-pre-wrap leading-relaxed font-sans">
              {msg.content}
            </p>
            {msg.answer && (
              <EvidenceDrawer
                evidence={msg.answer.evidence}
                total={msg.answer.total_evidence_rows}
              />
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default function CaseAssistantTab({ caseId }: { caseId: string }) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput]       = useState('')
  const [loading, setLoading]   = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async (question: string) => {
    const q = question.trim()
    if (!q || loading) return
    setInput('')
    setLoading(true)
    setMessages((prev) => [...prev, { id: Date.now() + 'u', role: 'user', content: q }])
    try {
      const { data } = await investigationApi.ask(caseId, q)
      setMessages((prev) => [
        ...prev,
        { id: Date.now() + 'a', role: 'assistant', content: data.answer, answer: data },
      ])
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })
        ?.response?.data?.detail
      setMessages((prev) => [
        ...prev,
        { id: Date.now() + 'e', role: 'assistant', content: '', error: msg || 'Query failed' },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full">

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-5">

        {/* Welcome state */}
        {messages.length === 0 && (
          <div className="max-w-xl mx-auto">
            <div className="text-center mb-7">
              <img
                src="/assets/red-john.svg"
                alt="AI"
                className="w-10 h-10 opacity-30 mx-auto mb-3 animate-slow-pulse"
              />
              <h2 className="font-serif text-lg font-bold text-cream mb-1">
                Intelligence AI
              </h2>
              <p className="text-sm text-sepia font-garamond italic">
                Ask questions grounded in the case evidence.
                Answers are drawn from the knowledge graph only.
              </p>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {SUGGESTED.map((q) => (
                <button
                  key={q}
                  onClick={() => send(q)}
                  className="card-hover text-left text-xs text-sepia leading-relaxed
                             hover:text-parchment py-2.5"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m) => <Bubble key={m.id} msg={m} />)}

        {loading && (
          <div className="flex items-start gap-3">
            <div
              className="w-7 h-7 rounded-full border flex items-center justify-center flex-shrink-0"
              style={{ background: '#352720', borderColor: 'rgba(169,144,100,0.3)' }}
            >
              <img src="/assets/red-john.svg" alt="" className="w-4 h-4 opacity-50" />
            </div>
            <div className="card flex items-center gap-2.5 py-3">
              <Loader2 className="w-3.5 h-3.5 animate-spin text-brass" />
              <span className="text-xs font-mono text-sepia">
                Querying knowledge graph…
              </span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div
        className="flex-shrink-0 px-6 py-4 border-t border-wire"
        style={{ background: '#2C1F1A' }}
      >
        <div className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && send(input)}
            placeholder="Ask about persons, transactions, connections…"
            className="input-field flex-1"
            disabled={loading}
          />
          <button
            onClick={() => send(input)}
            disabled={!input.trim() || loading}
            className="btn-primary flex items-center gap-1.5 disabled:opacity-40
                       disabled:cursor-not-allowed"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        <p className="text-[10px] text-sepia/40 mt-2 font-mono">
          Answers are grounded in extracted case evidence · Confidence scores reflect extraction quality
        </p>
      </div>
    </div>
  )
}
