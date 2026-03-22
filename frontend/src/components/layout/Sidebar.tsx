import { NavLink } from 'react-router-dom'
import {
  FlaskConical,
  History,
  BarChart3,
  GitCompare,
  Home,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useUiStore } from '@/store/uiStore'

const NAV_ITEMS = [
  { to: '/',          icon: Home,          label: 'Home' },
  { to: '/research',  icon: FlaskConical,  label: 'Research' },
  { to: '/history',   icon: History,       label: 'History' },
  { to: '/analytics', icon: BarChart3,     label: 'Analytics' },
  { to: '/compare',   icon: GitCompare,    label: 'Compare' },
]

export default function Sidebar() {
  const { sidebarOpen, toggleSidebar } = useUiStore()

  return (
    <aside
      className={cn(
        'relative flex flex-col shrink-0 border-r border-zinc-800 bg-[#0F1117]',
        'transition-all duration-200',
        sidebarOpen ? 'w-56' : 'w-14',
      )}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 h-14 border-b border-zinc-800">
        <div className="w-6 h-6 rounded-md bg-indigo-600 flex-shrink-0 flex items-center justify-center">
          <FlaskConical size={14} className="text-white" />
        </div>
        {sidebarOpen && (
          <span className="text-sm font-semibold text-white truncate">
            ResearchAgent
          </span>
        )}
      </div>

      {/* Nav */}
      <nav className="flex-1 py-4 px-2 space-y-1">
        {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors',
                isActive
                  ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30'
                  : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50',
              )
            }
          >
            <Icon size={16} className="flex-shrink-0" />
            {sidebarOpen && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Collapse toggle */}
      <button
        onClick={toggleSidebar}
        className="absolute -right-3 top-1/2 -translate-y-1/2 w-6 h-6 rounded-full
          bg-zinc-800 border border-zinc-700 flex items-center justify-center
          text-zinc-400 hover:text-zinc-200 hover:bg-zinc-700 transition-colors z-10"
      >
        {sidebarOpen ? <ChevronLeft size={12} /> : <ChevronRight size={12} />}
      </button>
    </aside>
  )
}
