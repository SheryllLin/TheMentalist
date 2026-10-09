import { useState } from 'react'
import { Outlet, NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard, FolderOpen, Network, Users, FileText,
  Search, Settings, ChevronRight, BookOpen, Database,
} from 'lucide-react'

const NAV_SECTIONS = [
  {
    label: 'Operations',
    items: [
      { to: '/dashboard',     icon: LayoutDashboard, label: 'Intelligence Dashboard' },
      { to: '/cases',         icon: FolderOpen,      label: 'Case Library'          },
    ],
  },
  {
    label: 'Investigation',
    items: [
      { to: '/persons',       icon: Users,           label: 'Persons of Interest'   },
      { to: '/graphs',        icon: Network,         label: 'Knowledge Graphs'      },
      { to: '/evidence',      icon: FileText,        label: 'Evidence Repository'   },
    ],
  },
  {
    label: 'Intelligence',
    items: [
      { to: '/reports',       icon: BookOpen,        label: 'Intelligence Reports'  },
      { to: '/sources',       icon: Database,        label: 'Data Sources'          },
    ],
  },
]

// Routes that don't have a dedicated page yet — show as "planned"
const PLANNED = new Set(['/persons', '/graphs', '/evidence', '/reports', '/sources'])

export default function AppLayout() {
  const [searchOpen, setSearchOpen] = useState(false)
  const location = useLocation()

  return (
    <div className="flex h-screen bg-espresso overflow-hidden">

      {/* ── Sidebar ─────────────────────────────────────────── */}
      <aside
        className="w-60 flex-shrink-0 flex flex-col border-r border-wire"
        style={{ background: 'var(--tw-bg-sidebar, #2C1F1A)' }}
      >
        {/* Brand header */}
        <div
          className="px-4 pt-5 pb-4 border-b border-wire"
          style={{ background: '#352720' }}
        >
          {/* Red John mark */}
          <div className="flex items-center gap-3 mb-3">
            <img
              src="/assets/red-john.svg"
              alt="Red John mark"
              className="w-8 h-8 opacity-90 flex-shrink-0"
            />
            <div className="min-w-0">
              <p className="font-serif font-bold text-cream tracking-widest text-sm leading-none">
                THE MENTALIST
              </p>
              <p className="text-[10px] font-mono text-sepia tracking-widest uppercase mt-1 leading-none">
                Criminal Intelligence System
              </p>
            </div>
          </div>
          {/* Divider line with red string feel */}
          <div className="h-px bg-gradient-to-r from-burgundy/60 via-burgundy/20 to-transparent" />
        </div>

        {/* Search bar */}
        <div className="px-3 py-3 border-b border-wire/60">
          <button
            className="w-full flex items-center gap-2 px-3 py-1.5 bg-walnut/80
                       border border-wire rounded-file text-sm text-sepia
                       hover:border-wire-strong hover:text-parchment transition-colors"
            onClick={() => setSearchOpen(true)}
          >
            <Search className="w-3.5 h-3.5 flex-shrink-0" />
            <span className="text-xs">Search cases, entities…</span>
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto px-2 py-3 space-y-4">
          {NAV_SECTIONS.map((section) => (
            <div key={section.label}>
              <p className="text-label px-3 mb-1">{section.label}</p>
              <div className="space-y-0.5">
                {section.items.map(({ to, icon: Icon, label }) => {
                  const isActive = location.pathname === to ||
                    (to !== '/dashboard' && location.pathname.startsWith(to))
                  const isPlanned = PLANNED.has(to)

                  if (isPlanned) {
                    return (
                      <div
                        key={to}
                        className="flex items-center gap-2.5 px-3 py-2 rounded-file
                                   text-sm text-sepia/40 cursor-not-allowed select-none"
                      >
                        <Icon className="w-4 h-4 flex-shrink-0" />
                        <span className="flex-1">{label}</span>
                        <span className="text-[10px] font-mono text-sepia/30 uppercase tracking-wide">
                          soon
                        </span>
                      </div>
                    )
                  }

                  return (
                    <NavLink
                      key={to}
                      to={to}
                      className={isActive ? 'nav-item-active' : 'nav-item'}
                    >
                      <Icon className="w-4 h-4 flex-shrink-0" />
                      <span className="flex-1">{label}</span>
                      {isActive && <ChevronRight className="w-3 h-3 opacity-50" />}
                    </NavLink>
                  )
                })}
              </div>
            </div>
          ))}
        </nav>

        {/* Footer — session info */}
        <div
          className="px-3 py-3 border-t border-wire"
          style={{ background: '#352720' }}
        >
          <div className="flex items-center gap-2.5 px-2 py-1.5">
            <div
              className="w-6 h-6 rounded-full flex items-center justify-center
                         bg-burgundy/30 border border-burgundy/50 flex-shrink-0"
            >
              <span className="text-xs font-mono text-burgundy-light font-bold">DI</span>
            </div>
            <div className="min-w-0">
              <p className="text-xs font-medium text-parchment truncate">Demo Investigator</p>
              <p className="text-[10px] font-mono text-sepia/70">CBI · Senior Analyst</p>
            </div>
          </div>
          <div className="mt-2 px-2">
            <NavLink
              to="/settings"
              className="flex items-center gap-2 text-xs text-sepia/60
                         hover:text-sepia transition-colors"
            >
              <Settings className="w-3 h-3" />
              <span>System Settings</span>
            </NavLink>
          </div>
        </div>
      </aside>

      {/* ── Main content ─────────────────────────────────────── */}
      <main className="flex-1 overflow-auto bg-espresso">
        <Outlet />
      </main>

      {/* ── Global search overlay (placeholder) ──────────────── */}
      {searchOpen && (
        <div
          className="fixed inset-0 bg-espresso/80 z-50 flex items-start justify-center pt-24 px-4"
          onClick={() => setSearchOpen(false)}
        >
          <div
            className="w-full max-w-xl bg-walnut border border-wire-strong rounded-file shadow-card-hover"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center gap-3 px-4 py-3 border-b border-wire">
              <Search className="w-4 h-4 text-brass" />
              <input
                autoFocus
                className="flex-1 bg-transparent text-cream placeholder-sepia/60 text-sm
                           outline-none font-sans"
                placeholder="Search cases, persons, evidence…"
                onKeyDown={(e) => e.key === 'Escape' && setSearchOpen(false)}
              />
              <kbd className="text-[10px] font-mono text-sepia/50 border border-wire
                              rounded px-1 py-0.5">ESC</kbd>
            </div>
            <div className="px-4 py-3 text-xs text-sepia/60 font-mono">
              Type to search across all cases and entities
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
