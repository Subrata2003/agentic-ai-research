import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import TopBar from './TopBar'
import PageTransition from './PageTransition'
import { useUiStore } from '@/store/uiStore'

export default function AppShell() {
  const sidebarOpen = useUiStore((s) => s.sidebarOpen)

  return (
    <div className="flex h-dvh overflow-hidden bg-transparent">
      <Sidebar />

      {/* Main area — shrinks when sidebar collapses */}
      <div
        className="flex flex-col flex-1 overflow-hidden transition-all duration-200"
        style={{ width: `calc(100% - ${sidebarOpen ? '14rem' : '3.5rem'})` }}
      >
        <TopBar />
        <main className="flex-1 overflow-y-auto bg-transparent">
          <PageTransition>
            <Outlet />
          </PageTransition>
        </main>
      </div>
    </div>
  )
}
