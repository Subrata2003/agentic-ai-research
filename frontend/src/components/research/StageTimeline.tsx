import { CheckCircle2, Circle, Loader2 } from 'lucide-react'
import { AGENT_STAGES } from '@/lib/constants'

// Exclude the sentinel 'done' entry — it's not a visual pipeline step
const STAGES = AGENT_STAGES.filter((s) => s.key !== 'done')

interface StageTimelineProps {
  currentStage: string
  progress: number
}

export default function StageTimeline({ currentStage, progress }: StageTimelineProps) {
  return (
    <ol className="space-y-1">
      {STAGES.map((stage, i) => {
        const isDone    = progress > stage.pct + 0.01 && currentStage !== stage.key
        const isActive  = currentStage === stage.key || (
          progress >= stage.pct && progress < (STAGES[i + 1]?.pct ?? 1)
        )
        const isPending = !isDone && !isActive

        return (
          <li key={stage.key} className="flex items-center gap-3 py-1">
            {/* Icon */}
            {isDone ? (
              <CheckCircle2 className="h-4 w-4 text-emerald-500 shrink-0" />
            ) : isActive ? (
              <Loader2 className="h-4 w-4 text-indigo-400 animate-spin shrink-0" />
            ) : (
              <Circle className="h-4 w-4 text-zinc-700 shrink-0" />
            )}

            {/* Label */}
            <span
              className={[
                'text-sm',
                isDone   ? 'text-zinc-400 line-through decoration-zinc-600' :
                isActive ? 'text-white font-medium' :
                           'text-zinc-600',
              ].join(' ')}
            >
              {stage.label}
            </span>
          </li>
        )
      })}
    </ol>
  )
}
