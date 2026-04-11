import { useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { useResearchStore } from '@/store/researchStore'

/**
 * Fires sonner toasts based on research job status changes.
 * Mount once inside AppShell so toasts fire on every page.
 */
export function useResearchToast() {
  const status          = useResearchStore((s) => s.status)
  const completedId     = useResearchStore((s) => s.completedReportId)
  const hasRedirected   = useResearchStore((s) => s.hasAutoRedirected)
  const prevStatusRef   = useRef<string>('idle')
  const navigate        = useNavigate()

  useEffect(() => {
    const prev = prevStatusRef.current
    prevStatusRef.current = status

    // Avoid firing on first mount (idle → idle)
    if (prev === status) return

    if (status === 'complete' && completedId) {
      toast.success('Research complete!', {
        description: 'Your report is ready to view.',
        duration: 6000,
        action: {
          label: 'View Report',
          onClick: () => navigate(`/reports/${completedId}`),
        },
      })
      return
    }

    if (status === 'error' || status === 'failed') {
      toast.error('Research failed', {
        description: 'Something went wrong. Please try again.',
        duration: 5000,
      })
      return
    }

    if (status === 'reconnecting') {
      toast.warning('Connection lost', {
        description: 'Trying to reconnect to the agent stream…',
        duration: 4000,
      })
      return
    }
  }, [status, completedId, hasRedirected, navigate])
}
