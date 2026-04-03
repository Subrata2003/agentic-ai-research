import { scoreBadgeClass, pct } from '@/lib/utils'

interface ScoreBadgeProps {
  score: number | null
  size?: 'sm' | 'md'
}

/**
 * Compact quality-score badge: emerald ≥80%, amber ≥60%, red <60%.
 */
export default function ScoreBadge({ score, size = 'md' }: ScoreBadgeProps) {
  if (score === null || score === undefined) {
    return (
      <span className="inline-flex items-center rounded-full border bg-zinc-500/10 text-zinc-500 border-zinc-500/20 px-2 py-0.5 text-xs font-medium">
        N/A
      </span>
    )
  }

  const cls = scoreBadgeClass(score)
  const text = size === 'sm' ? pct(score) : `${pct(score)} quality`

  return (
    <span className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-semibold ${cls}`}>
      {text}
    </span>
  )
}
