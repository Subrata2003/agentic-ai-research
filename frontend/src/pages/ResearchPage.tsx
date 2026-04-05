import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { RotateCcw } from 'lucide-react'
import { useResearchStore } from '@/store/researchStore'
import { useResearchStream } from '@/hooks/useResearchStream'
import ResearchForm from '@/components/research/ResearchForm'
import AgentFeed from '@/components/research/AgentFeed'
import ProgressRing from '@/components/research/ProgressRing'
import StageTimeline from '@/components/research/StageTimeline'

const STATUS_LABEL: Record<string, string> = {
  idle:         'Ready',
  queued:       'Queued…',
  streaming:    'Running',
  reconnecting: 'Reconnecting…',
  complete:     'Complete',
  error:        'Error',
  failed:       'Failed',
}

const STATUS_COLOR: Record<string, string> = {
  idle:         'text-zinc-500',
  queued:       'text-amber-400',
  streaming:    'text-indigo-400',
  reconnecting: 'text-amber-400',
  complete:     'text-emerald-400',
  error:        'text-red-400',
  failed:       'text-red-400',
}

export default function ResearchPage() {
  const navigate = useNavigate()

  const jobId              = useResearchStore((s) => s.jobId)
  const status             = useResearchStore((s) => s.status)
  const stage              = useResearchStore((s) => s.stage)
  const progress           = useResearchStore((s) => s.progress)
  const completedReportId  = useResearchStore((s) => s.completedReportId)
  const hasAutoRedirected  = useResearchStore((s) => s.hasAutoRedirected)
  const markRedirected     = useResearchStore((s) => s.markRedirected)
  const reset              = useResearchStore((s) => s.reset)

  // Connect WebSocket while a job is running
  useResearchStream(
    status !== 'idle' && status !== 'complete' && status !== 'error' && status !== 'failed'
      ? jobId
      : null,
  )

  // Auto-navigate to report when done — only fires once per job
  useEffect(() => {
    if (status === 'complete' && completedReportId && !hasAutoRedirected) {
      const timer = setTimeout(() => {
        markRedirected()
        navigate(`/reports/${completedReportId}`)
      }, 1800)
      return () => clearTimeout(timer)
    }
  }, [status, completedReportId, hasAutoRedirected, markRedirected, navigate])

  const isActive = status !== 'idle'

  return (
    <div className="flex h-full gap-0">
      {/* ── Left panel ─────────────────────────────────── */}
      <div className="flex flex-col w-[400px] shrink-0 border-r border-white/5 overflow-y-auto">
        <div className="p-6 space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold text-white">New Research</h1>
              <p className="text-sm text-zinc-500 mt-0.5">Multi-agent AI pipeline</p>
            </div>

            {isActive && (
              <button
                type="button"
                onClick={reset}
                title="Reset"
                className="flex items-center gap-1.5 text-xs text-zinc-500 hover:text-zinc-200 transition-colors"
              >
                <RotateCcw className="h-3.5 w-3.5" />
                Reset
              </button>
            )}
          </div>

          {/* Form — only when not active */}
          <AnimatePresence mode="wait">
            {!isActive ? (
              <motion.div
                key="form"
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.2 }}
              >
                <ResearchForm />
              </motion.div>
            ) : (
              <motion.div
                key="progress"
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.2 }}
                className="space-y-6"
              >
                {/* Progress ring */}
                <div className="flex justify-center py-2">
                  <ProgressRing
                    progress={progress}
                    size={128}
                    strokeWidth={10}
                    label={STATUS_LABEL[status] ?? status}
                  />
                </div>

                {/* Status badge */}
                <div className="text-center">
                  <span className={`text-sm font-medium ${STATUS_COLOR[status] ?? 'text-zinc-400'}`}>
                    {STATUS_LABEL[status] ?? status}
                  </span>
                  {stage && (
                    <span className="ml-2 text-xs text-zinc-600 capitalize">
                      · {stage.replace(/_/g, ' ')}
                    </span>
                  )}
                </div>

                {/* Stage timeline */}
                <div className="rounded-xl border border-white/5 bg-white/[0.03] p-4">
                  <StageTimeline currentStage={stage} progress={progress} />
                </div>

                {/* Auto-redirect notice */}
                {status === 'complete' && completedReportId && (
                  <motion.p
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="text-center text-xs text-emerald-400"
                  >
                    Redirecting to report…
                  </motion.p>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* ── Right panel: Agent Feed ─────────────────────── */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <AgentFeed />
      </div>
    </div>
  )
}
