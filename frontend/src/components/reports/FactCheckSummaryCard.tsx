import { CheckCircle2, HelpCircle, XCircle } from 'lucide-react'
import type { FactCheckSummary } from '@/types/api'

interface FactCheckSummaryCardProps {
  summary: FactCheckSummary
}

export default function FactCheckSummaryCard({ summary }: FactCheckSummaryCardProps) {
  const { supported, unverifiable, contradicted, total } = summary
  const supportedPct    = total > 0 ? Math.round((supported    / total) * 100) : 0
  const unverifiablePct = total > 0 ? Math.round((unverifiable / total) * 100) : 0
  const contradictedPct = total > 0 ? Math.round((contradicted / total) * 100) : 0

  return (
    <div className="space-y-3">
      <p className="text-xs text-zinc-500">{total} claims verified</p>

      <div className="space-y-2">
        {/* Supported */}
        <div className="flex items-center gap-2">
          <CheckCircle2 className="h-4 w-4 text-emerald-500 shrink-0" />
          <div className="flex-1 h-2 rounded-full bg-white/5 overflow-hidden">
            <div
              className="h-full rounded-full bg-emerald-500 transition-all duration-700"
              style={{ width: `${supportedPct}%` }}
            />
          </div>
          <span className="text-xs text-emerald-400 tabular-nums w-8 text-right">{supported}</span>
        </div>

        {/* Unverifiable */}
        <div className="flex items-center gap-2">
          <HelpCircle className="h-4 w-4 text-amber-400 shrink-0" />
          <div className="flex-1 h-2 rounded-full bg-white/5 overflow-hidden">
            <div
              className="h-full rounded-full bg-amber-400 transition-all duration-700"
              style={{ width: `${unverifiablePct}%` }}
            />
          </div>
          <span className="text-xs text-amber-400 tabular-nums w-8 text-right">{unverifiable}</span>
        </div>

        {/* Contradicted */}
        <div className="flex items-center gap-2">
          <XCircle className="h-4 w-4 text-red-400 shrink-0" />
          <div className="flex-1 h-2 rounded-full bg-white/5 overflow-hidden">
            <div
              className="h-full rounded-full bg-red-400 transition-all duration-700"
              style={{ width: `${contradictedPct}%` }}
            />
          </div>
          <span className="text-xs text-red-400 tabular-nums w-8 text-right">{contradicted}</span>
        </div>
      </div>

      <div className="flex gap-3 text-[10px] text-zinc-600">
        <span>✓ Supported</span>
        <span>? Unverifiable</span>
        <span>✗ Contradicted</span>
      </div>
    </div>
  )
}
