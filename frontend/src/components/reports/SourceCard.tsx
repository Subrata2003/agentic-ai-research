import { ExternalLink } from 'lucide-react'
import { extractDomain } from '@/lib/utils'
import type { SourceItem } from '@/types/api'

interface SourceCardProps {
  source: SourceItem
  isActive?: boolean
}

export default function SourceCard({ source, isActive }: SourceCardProps) {
  return (
    <div
      id={`source-${source.source_index}`}
      className={[
        'rounded-xl border p-4 space-y-2 transition-all duration-300',
        isActive
          ? 'border-indigo-500/60 bg-indigo-500/10 shadow-lg shadow-indigo-500/10'
          : 'border-white/5 bg-white/[0.03] hover:border-white/10',
      ].join(' ')}
    >
      {/* Header */}
      <div className="flex items-start gap-2">
        <span className="shrink-0 mt-0.5 h-5 w-5 rounded-full bg-indigo-500/20 text-indigo-400 text-[10px] font-bold flex items-center justify-center">
          {source.source_index}
        </span>
        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium text-zinc-200 leading-snug line-clamp-2">
            {source.title || extractDomain(source.url)}
          </p>
          <a
            href={source.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-xs text-indigo-400 hover:text-indigo-300 mt-0.5 transition-colors"
          >
            {extractDomain(source.url)}
            <ExternalLink className="h-2.5 w-2.5" />
          </a>
        </div>
        {/* Relevance */}
        <span className="shrink-0 text-xs text-zinc-500 tabular-nums">
          {Math.round(source.relevance_score * 100)}%
        </span>
      </div>

      {/* Exact quote */}
      {source.exact_quote && (
        <blockquote className="text-xs text-zinc-400 italic leading-relaxed border-l-2 border-indigo-500/40 pl-3 line-clamp-3">
          "{source.exact_quote}"
        </blockquote>
      )}
    </div>
  )
}
