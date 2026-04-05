import { scoreColor } from '@/lib/utils'
import type { QualityScore } from '@/types/api'
import AnimatedScore from './AnimatedScore'

interface DimensionRowProps {
  label: string
  value: number
  weight: string
}

function DimensionRow({ label, value, weight }: DimensionRowProps) {
  const barWidth = `${Math.round(value * 100)}%`
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-xs">
        <span className="text-zinc-400">{label}</span>
        <span className="flex items-center gap-2">
          <span className="text-zinc-600 text-[10px]">{weight}</span>
          <AnimatedScore value={value} className={`font-semibold ${scoreColor(value)}`} />
        </span>
      </div>
      <div className="h-1.5 rounded-full bg-white/5 overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{
            width: barWidth,
            background: value >= 0.8
              ? '#34d399'
              : value >= 0.6
              ? '#fbbf24'
              : '#f87171',
          }}
        />
      </div>
    </div>
  )
}

interface QualityBreakdownProps {
  score: QualityScore
}

export default function QualityBreakdown({ score }: QualityBreakdownProps) {
  return (
    <div className="space-y-3">
      <DimensionRow label="Source Coverage"     value={score.source_coverage}     weight="25%" />
      <DimensionRow label="Citation Accuracy"   value={score.citation_accuracy}   weight="30%" />
      <DimensionRow label="Synthesis Coherence" value={score.synthesis_coherence} weight="25%" />
      <DimensionRow label="Factual Density"     value={score.factual_density}     weight="20%" />

      <div className="pt-2 border-t border-white/5 flex items-center justify-between">
        <span className="text-xs font-medium text-zinc-300">Overall</span>
        <AnimatedScore value={score.overall} className={`text-base font-bold ${scoreColor(score.overall)}`} />
      </div>
    </div>
  )
}
