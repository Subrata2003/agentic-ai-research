import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import { QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { queryClient } from '@/lib/queryClient'
import AppShell from '@/components/layout/AppShell'
import LandingPage from '@/pages/LandingPage'
import ResearchPage from '@/pages/ResearchPage'
import HistoryPage from '@/pages/HistoryPage'
import ReportDetailPage from '@/pages/ReportDetailPage'
import AnalyticsPage from '@/pages/AnalyticsPage'
import ComparePage from '@/pages/ComparePage'

const router = createBrowserRouter([
  {
    path: '/',
    element: <AppShell />,
    children: [
      { index: true,            element: <LandingPage /> },
      { path: 'research',       element: <ResearchPage /> },
      { path: 'history',        element: <HistoryPage /> },
      { path: 'reports/:id',    element: <ReportDetailPage /> },
      { path: 'analytics',      element: <AnalyticsPage /> },
      { path: 'compare',        element: <ComparePage /> },
    ],
  },
])

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}
