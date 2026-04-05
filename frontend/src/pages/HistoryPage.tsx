import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, SortAsc, FileText, Loader2, ChevronLeft, ChevronRight } from 'lucide-react'
import { useReports } from '@/hooks/useReports'
import { formatDate, timeAgo, scoreColor } from '@/lib/utils'
import ScoreBadge from '@/components/reports/ScoreBadge'
import type { ReportListItem } from '@/types/api'

type SortOption = 'newest' | 'oldest' | 'quality_desc' | 'quality_asc'

const SORT_OPTIONS: { value: SortOption; label: string }[] = [
  { value: 'newest',       label: 'Newest first'     },
  { value: 'oldest',       label: 'Oldest first'     },
  { value: 'quality_desc', label: 'Highest quality'  },
  { value: 'quality_asc',  label: 'Lowest quality'   },
]

const DEPTH_LABEL: Record<string, string> = {
  shallow: 'Quick',
  medium:  'Standard',
  deep:    'Deep Dive',
}

function ReportCard({ report }: { report: ReportListItem }) {
  const navigate = useNavigate()
  return (
    <div
      onClick={() => navigate(`/reports/${report.id}`)}
      className="group card-hover rounded-xl border border-white/5 bg-white/[0.03] p-5 cursor-pointer hover:border-indigo-500/30 hover:bg-white/[0.05]"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <h3 className="font-medium text-zinc-200 leading-snug group-hover:text-white transition-colors line-clamp-2">
            {report.topic}
          </h3>
          <div className="flex items-center gap-2 mt-2 text-xs text-zinc-500">
            <span>{DEPTH_LABEL[report.depth] ?? report.depth}</span>
            <span>·</span>
            <span>{report.num_sources} sources</span>
            <span>·</span>
            <span title={formatDate(report.created_at)}>{timeAgo(report.created_at)}</span>
          </div>
        </div>
        <ScoreBadge score={report.overall_score} size="sm" />
      </div>

      {/* Score bar */}
      {report.overall_score !== null && report.overall_score !== undefined && (
        <div className="mt-3 h-1 rounded-full bg-white/5 overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-700"
            style={{
              width: `${Math.round(report.overall_score * 100)}%`,
              background: report.overall_score >= 0.8 ? '#34d399' : report.overall_score >= 0.6 ? '#fbbf24' : '#f87171',
            }}
          />
        </div>
      )}

      {/* Confidence */}
      {report.overall_confidence !== null && report.overall_confidence !== undefined && (
        <p className="mt-2 text-xs text-zinc-600">
          Confidence{' '}
          <span className={scoreColor(report.overall_confidence)}>
            {Math.round(report.overall_confidence * 100)}%
          </span>
        </p>
      )}
    </div>
  )
}

export default function HistoryPage() {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const [sort,   setSort]   = useState<SortOption>('newest')
  const [page,   setPage]   = useState(1)

  const { data, isLoading, isFetching } = useReports({ page, limit: 12, search, sort })

  const handleSearch = (v: string) => {
    setSearch(v)
    setPage(1)
  }

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Header */}
      <div className="shrink-0 px-8 pt-8 pb-5 border-b border-white/5">
        <div className="flex items-center justify-between mb-5">
          <div>
            <h1 className="text-xl font-bold text-white">Research History</h1>
            <p className="text-sm text-zinc-500 mt-0.5">
              {data?.total ?? '…'} reports
            </p>
          </div>

          <button
            onClick={() => navigate('/research')}
            className="rounded-lg bg-indigo-600 hover:bg-indigo-500 px-4 py-2 text-sm font-medium text-white transition-colors"
          >
            + New Research
          </button>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-3">
          {/* Search */}
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500 pointer-events-none" />
            <input
              type="text"
              value={search}
              onChange={(e) => handleSearch(e.target.value)}
              placeholder="Search reports…"
              className="w-full rounded-lg border border-white/10 bg-white/5 pl-9 pr-4 py-2 text-sm text-zinc-200 placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors"
            />
          </div>

          {/* Sort */}
          <div className="relative">
            <SortAsc className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500 pointer-events-none" />
            <select
              value={sort}
              onChange={(e) => { setSort(e.target.value as SortOption); setPage(1) }}
              className="appearance-none rounded-lg border border-white/10 bg-[#0D1117] pl-9 pr-8 py-2 text-sm text-zinc-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 cursor-pointer"
            >
              {SORT_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto px-8 py-6">
        {isLoading ? (
          <div className="flex h-40 items-center justify-center gap-3 text-zinc-400">
            <Loader2 className="h-5 w-5 animate-spin" />
            Loading…
          </div>
        ) : !data || data.items.length === 0 ? (
          <div className="flex h-40 flex-col items-center justify-center gap-3 text-zinc-500">
            <FileText className="h-10 w-10 text-zinc-700" />
            <p className="text-sm">{search ? 'No reports match your search.' : 'No reports yet.'}</p>
            {!search && (
              <button
                onClick={() => navigate('/research')}
                className="text-sm text-indigo-400 hover:text-indigo-300 transition-colors"
              >
                Run your first research →
              </button>
            )}
          </div>
        ) : (
          <>
            {/* Grid */}
            <div className={[
              'grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
              isFetching ? 'opacity-60' : '',
            ].join(' ')}>
              {data.items.map((r) => <ReportCard key={r.id} report={r} />)}
            </div>

            {/* Pagination */}
            {data.pages > 1 && (
              <div className="flex items-center justify-center gap-3 mt-8">
                <button
                  disabled={page <= 1}
                  onClick={() => setPage((p) => p - 1)}
                  className="flex items-center gap-1 rounded-lg border border-white/10 px-3 py-1.5 text-sm text-zinc-400 disabled:opacity-40 disabled:cursor-not-allowed hover:border-white/20 hover:text-zinc-200 transition-colors"
                >
                  <ChevronLeft className="h-4 w-4" />
                  Prev
                </button>

                <span className="text-sm text-zinc-500">
                  {page} / {data.pages}
                </span>

                <button
                  disabled={page >= data.pages}
                  onClick={() => setPage((p) => p + 1)}
                  className="flex items-center gap-1 rounded-lg border border-white/10 px-3 py-1.5 text-sm text-zinc-400 disabled:opacity-40 disabled:cursor-not-allowed hover:border-white/20 hover:text-zinc-200 transition-colors"
                >
                  Next
                  <ChevronRight className="h-4 w-4" />
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
