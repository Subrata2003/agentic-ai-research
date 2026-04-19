import { Outlet } from 'react-router-dom'
import { Toaster } from 'sonner'
import Sidebar from './Sidebar'
import TopBar from './TopBar'
import PageTransition from './PageTransition'
import GlobalProgressBar from './GlobalProgressBar'
import { useUiStore } from '@/store/uiStore'
import { useResearchToast } from '@/hooks/useResearchToast'

export default function AppShell() {
  const sidebarOpen = useUiStore((s) => s.sidebarOpen)

  // Fire toasts on every page when research status changes
  useResearchToast()

  return (
    <div className="flex h-dvh overflow-hidden bg-transparent">
      {/* Global 3px progress bar — fixed to top of viewport */}
      <GlobalProgressBar />

      <Sidebar />

      {/* Main area */}
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

      {/* Sonner toast container */}
      <Toaster
        position="bottom-right"
        theme="dark"
        toastOptions={{
          style: {
            background: 'rgba(15, 17, 23, 0.92)',
            backdropFilter: 'blur(16px)',
            border: '1px solid rgba(255,255,255,0.08)',
            color: '#f4f4f5',
          },
        }}
      />
    </div>
  )
}
