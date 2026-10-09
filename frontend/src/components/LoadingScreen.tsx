/**
 * LoadingScreen — shown on initial app boot while the API token is being fetched.
 * Uses the Red John SVG mark with a slow fade / pulse animation.
 * Dismissed automatically once the parent signals ready.
 */
import { useEffect, useState } from 'react'

export default function LoadingScreen({ onReady }: { onReady: () => void }) {
  const [phase, setPhase] = useState<'enter' | 'hold' | 'exit'>('enter')

  useEffect(() => {
    // enter → hold after 600 ms
    const t1 = setTimeout(() => setPhase('hold'), 600)
    // exit starts at 1.6 s
    const t2 = setTimeout(() => setPhase('exit'), 1600)
    // unmount at 2 s
    const t3 = setTimeout(() => onReady(), 2000)
    return () => { clearTimeout(t1); clearTimeout(t2); clearTimeout(t3) }
  }, [onReady])

  return (
    <div
      className="fixed inset-0 z-[9999] flex flex-col items-center justify-center"
      style={{
        background: '#211A17',
        opacity:    phase === 'exit' ? 0 : 1,
        transition: phase === 'exit' ? 'opacity 0.4s ease' : 'opacity 0.3s ease',
      }}
    >
      {/* Red John mark */}
      <div
        style={{
          opacity:   phase === 'enter' ? 0 : 1,
          transform: phase === 'enter' ? 'scale(0.85)' : 'scale(1)',
          transition: 'opacity 0.5s ease, transform 0.5s ease',
        }}
      >
        <img
          src="/assets/red-john.svg"
          alt="THE MENTALIST"
          style={{
            width: 88,
            height: 88,
            filter: 'drop-shadow(0 0 18px rgba(204,26,26,0.35))',
            animation: phase === 'hold' ? 'slowPulse 2s ease-in-out infinite' : 'none',
          }}
        />
      </div>

      {/* Title block */}
      <div
        className="mt-7 text-center"
        style={{
          opacity:   phase === 'enter' ? 0 : 1,
          transform: phase === 'enter' ? 'translateY(6px)' : 'translateY(0)',
          transition: 'opacity 0.6s ease 0.15s, transform 0.6s ease 0.15s',
        }}
      >
        <p
          style={{
            fontFamily: '"Playfair Display", Georgia, serif',
            fontSize: 22,
            fontWeight: 700,
            letterSpacing: '0.22em',
            color: '#E9DFC9',
            lineHeight: 1,
          }}
        >
          THE MENTALIST
        </p>
        <p
          style={{
            fontFamily: '"IBM Plex Mono", monospace',
            fontSize: 9,
            letterSpacing: '0.3em',
            color: 'rgba(169,144,100,0.55)',
            marginTop: 8,
            textTransform: 'uppercase',
          }}
        >
          Criminal Intelligence &amp; Network Analysis
        </p>
      </div>

      {/* Thin red rule */}
      <div
        style={{
          width: phase === 'enter' ? 0 : 64,
          height: 1,
          background: 'linear-gradient(90deg, transparent, #CC1A1A, transparent)',
          marginTop: 20,
          transition: 'width 0.7s ease 0.3s',
        }}
      />

      {/* Initialising label */}
      <p
        style={{
          fontFamily: '"IBM Plex Mono", monospace',
          fontSize: 9,
          letterSpacing: '0.25em',
          color: 'rgba(169,144,100,0.3)',
          marginTop: 16,
          textTransform: 'uppercase',
          opacity: phase === 'hold' ? 1 : 0,
          transition: 'opacity 0.4s ease',
        }}
      >
        Initialising…
      </p>
    </div>
  )
}
