/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // ── THE MENTALIST colour system ─────────────────────────────
        // Base surfaces
        walnut:    '#352720',   // darkest bg — sidebar, overlays
        espresso:  '#211A17',   // body background
        mahogany:  '#2C1F1A',   // card / panel surface
        rosewood:  '#3D2820',   // elevated card / hover surface
        // Accent — restrained burgundy / blood red
        burgundy: {
          DEFAULT: '#7A2D35',
          light:   '#9B3D46',
          dim:     '#5C2028',
          muted:   '#6F3035',
        },
        // Type & content
        cream:     '#E9DFC9',   // primary text
        parchment: '#D7C7A8',   // secondary text
        sepia:     '#A89070',   // muted/tertiary text
        brass:     '#AA9164',   // accent highlights, icons
        olive:     '#6C7056',   // status / tag colours
        // Borders
        wire: {
          DEFAULT: 'rgba(169,144,100,0.18)',  // brass-tinted subtle border
          strong:  'rgba(169,144,100,0.35)',  // slightly stronger
          muted:   'rgba(169,144,100,0.08)',  // near-invisible
        },
        // Evidence tag colours (used on graph nodes + badges)
        evidence: {
          person:   '#8B6B47',
          org:      '#6B5A3E',
          location: '#4A5E47',
          phone:    '#5A4A6B',
          finance:  '#4A5E5A',
          event:    '#7A4A3A',
          vehicle:  '#5A6B3A',
          doc:      '#6B5A3E',
        },
        // Status colours (desaturated to fit palette)
        status: {
          active:   '#8B7A3A',
          closed:   '#4A6B4A',
          archived: '#6B5A3A',
          critical: '#8B3535',
          high:     '#8B5A35',
          medium:   '#8B7A35',
          low:      '#4A6B4A',
        },
      },
      fontFamily: {
        serif:   ['"Playfair Display"', '"EB Garamond"', 'Georgia', 'serif'],
        garamond:['"EB Garamond"', 'Georgia', 'serif'],
        sans:    ['Inter', 'system-ui', 'sans-serif'],
        mono:    ['"IBM Plex Mono"', '"Fira Code"', 'monospace'],
      },
      backgroundImage: {
        // Subtle paper / corkboard textures built with CSS gradients
        'parchment-texture': `
          radial-gradient(ellipse at 20% 30%, rgba(169,144,100,0.04) 0%, transparent 60%),
          radial-gradient(ellipse at 80% 70%, rgba(110,93,61,0.04) 0%, transparent 60%),
          linear-gradient(135deg, rgba(53,39,32,0) 0%, rgba(44,31,26,0.3) 100%)
        `,
        'corkboard': `
          repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(169,144,100,0.03) 2px, rgba(169,144,100,0.03) 4px),
          repeating-linear-gradient(90deg, transparent, transparent 2px, rgba(169,144,100,0.03) 2px, rgba(169,144,100,0.03) 4px),
          linear-gradient(160deg, #2C1F1A 0%, #211A17 50%, #2C1F1A 100%)
        `,
        'sidebar-texture': `
          repeating-linear-gradient(180deg, transparent 0px, transparent 60px, rgba(169,144,100,0.04) 60px, rgba(169,144,100,0.04) 61px),
          linear-gradient(180deg, #352720 0%, #2C1F1A 100%)
        `,
      },
      boxShadow: {
        'card':       '0 1px 3px rgba(0,0,0,0.4), 0 0 0 1px rgba(169,144,100,0.12)',
        'card-hover': '0 4px 12px rgba(0,0,0,0.5), 0 0 0 1px rgba(169,144,100,0.25)',
        'panel':      '2px 0 12px rgba(0,0,0,0.4)',
        'inset-top':  'inset 0 1px 0 rgba(169,144,100,0.15)',
        'burgundy':   '0 0 0 1px rgba(122,45,53,0.6), 0 2px 8px rgba(122,45,53,0.25)',
      },
      borderRadius: {
        'file':  '2px',   // very sharp — case files, documents
        'stamp': '1px',   // evidence stamps
      },
    },
  },
  plugins: [],
}
