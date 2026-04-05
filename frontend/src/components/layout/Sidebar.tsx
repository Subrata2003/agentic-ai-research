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
        'relative flex flex-col shrink-0 border-r border-white/5',
        'glass transition-all duration-200',
        sidebarOpen ? 'w-56' : 'w-14',
      )}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 h-14 border-b border-white/5">
        <div className="w-6 h-6 rounded-md bg-gradient-to-br from-indigo-500 to-violet-600 flex-shrink-0 flex items-center justify-center shadow-lg shadow-indigo-500/30">
          <FlaskConical size={13} className="text-white" />
        </div>
        {sidebarOpen && (
          <span className="text-sm font-semibold text-white truncate tracking-tight">
            ResearchAgent
          </span>
        )}
      </div>

      {/* Nav */}
      <nav className="flex-1 py-4 px-2 space-y-0.5">
        {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              cn(
                'nav-glow flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-150',
                isActive ? 'active' : '',
                isActive
                  ? 'bg-indigo-500/10 text-indigo-300 shadow-sm'
                  : 'text-zinc-400 hover:text-zinc-200 hover:bg-white/5',
              )
            }
          >
            {({ isActive }) => (
              <>
                <Icon
                  size={16}
                  className={cn(
                    'flex-shrink-0 transition-colors',
                    isActive ? 'text-indigo-400' : '',
                  )}
                />
                {sidebarOpen && (
                  <span className={cn('font-medium', isActive ? 'text-indigo-300' : '')}>
                    {label}
                  </span>
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Collapse toggle */}
      <button
        onClick={toggleSidebar}
        className="absolute -right-3 top-1/2 -translate-y-1/2 w-6 h-6 rounded-full
          glass border border-white/10 flex items-center justify-center
          text-zinc-400 hover:text-zinc-200 hover:border-indigo-500/40 transition-all z-10
          shadow-lg shadow-black/30"
      >
        {sidebarOpen ? <ChevronLeft size={12} /> : <ChevronRight size={12} />}
      </button>
    </aside>
  )
}
