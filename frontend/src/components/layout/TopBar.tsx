import { useLocation } from 'react-router-dom'
import { Moon, Sun } from 'lucide-react'
import { useUiStore } from '@/store/uiStore'

const ROUTE_LABELS: Record<string, string> = {
  '/':           'Home',
  '/research':   'Research',
  '/history':    'History',
  '/analytics':  'Analytics',
  '/compare':    'Compare',
}

export default function TopBar() {
  const { pathname } = useLocation()
  const { theme, setTheme } = useUiStore()

  const label = ROUTE_LABELS[pathname] ?? 'Report'

  return (
    <header className="h-14 border-b border-zinc-800 bg-[#0F1117]/80 backdrop-blur-sm
      flex items-center justify-between px-6 shrink-0">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm">
        <span className="text-zinc-500">ResearchAgent</span>
        <span className="text-zinc-700">/</span>
        <span className="text-zinc-200 font-medium">{label}</span>
      </div>

      {/* Theme toggle */}
      <button
        onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
        className="w-8 h-8 rounded-lg flex items-center justify-center
          text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
        aria-label="Toggle theme"
      >
        {theme === 'dark' ? <Sun size={15} /> : <Moon size={15} />}
      </button>
    </header>
  )
}
