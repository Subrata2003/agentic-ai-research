import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import TopBar from './TopBar'
import { useUiStore } from '@/store/uiStore'
import { cn } from '@/lib/utils'

export default function AppShell() {
  const sidebarOpen = useUiStore((s) => s.sidebarOpen)

  return (
    <div className="flex h-dvh overflow-hidden bg-[#080B11]">
      <Sidebar />

      {/* Main area */}
      <div
        className={cn(
          'flex flex-col flex-1 overflow-hidden transition-all duration-200',
          sidebarOpen ? 'ml-0' : 'ml-0',
        )}
      >
        <TopBar />
        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
