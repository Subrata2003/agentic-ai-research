import React from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import rehypeSlug from 'rehype-slug'
import { ArrowLeft, Download, Loader2, FileText, BookOpen, FlaskConical } from 'lucide-react'
import { useReport } from '@/hooks/useReports'
import { usePdfExport } from '@/hooks/usePdfExport'
import { formatDate, pct, scoreColor } from '@/lib/utils'
import ScoreBadge from '@/components/reports/ScoreBadge'
import QualityBreakdown from '@/components/reports/QualityBreakdown'
import SourceCard from '@/components/reports/SourceCard'
import FactCheckSummaryCard from '@/components/reports/FactCheckSummaryCard'

const DEPTH_LABEL: Record<string, string> = {
  shallow: 'Quick Scan',
  medium:  'Standard',
  deep:    'Deep Dive',
}

export default function ReportDetailPage() {
  const { id }     = useParams<{ id: string }>()
  const navigate   = useNavigate()
  const { data: report, isLoading, isError } = useReport(id)
  const { mutate: exportPdf, isPending: exporting } = usePdfExport()

  // ── Loading ──────────────────────────────────────────────────────────────
  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center gap-3 text-zinc-400">
        <Loader2 className="h-5 w-5 animate-spin" />
        Loading report…
      </div>
    )
  }

  // ── Error ────────────────────────────────────────────────────────────────
  if (isError || !report) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-4 text-zinc-400">
        <FileText className="h-10 w-10 text-zinc-600" />
        <p>Report not found.</p>
        <button
          onClick={() => navigate('/history')}
          className="text-sm text-indigo-400 hover:text-indigo-300 transition-colors"
        >
          ← Back to History
        </button>
      </div>
    )
  }

  return (
    <div className="flex h-full overflow-hidden">

      {/* ── Main content ─────────────────────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto">
        {/* Top bar */}
        <div className="sticky top-0 z-10 flex items-center gap-3 px-6 py-3 border-b border-white/5 glass">
          <button
            onClick={() => navigate('/history')}
            className="flex items-center gap-1.5 text-sm text-zinc-400 hover:text-zinc-200 transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            History
          </button>

          <span className="text-zinc-700">/</span>

          <span className="text-sm text-zinc-300 truncate max-w-xs">{report.topic}</span>

          <div className="ml-auto flex items-center gap-2">
            <ScoreBadge score={report.overall_score} />

            <button
              onClick={() => exportPdf(report.id)}
              disabled={exporting}
              className={[
                'flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium transition-all',
                exporting
                  ? 'cursor-not-allowed border-white/5 text-zinc-600'
                  : 'border-white/10 text-zinc-300 hover:border-indigo-500/50 hover:text-indigo-300',
              ].join(' ')}
            >
              {exporting ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <Download className="h-3.5 w-3.5" />
              )}
              Export PDF
            </button>
          </div>
        </div>

        {/* Report header */}
        <div className="px-8 pt-8 pb-4">
          <div className="flex items-center gap-2 mb-3 text-xs text-zinc-500">
            <span>{DEPTH_LABEL[report.depth] ?? report.depth}</span>
            <span>·</span>
            <span>{report.num_sources} sources</span>
            <span>·</span>
            <span>{formatDate(report.created_at)}</span>
          </div>
          <h1 className="text-2xl font-bold text-white leading-snug">{report.topic}</h1>
        </div>

        {/* Markdown body */}
        <div className="px-8 pb-16">
          <div className="prose prose-invert prose-sm max-w-none
            prose-headings:text-white prose-headings:font-semibold
            prose-p:text-zinc-300 prose-p:leading-relaxed
            prose-a:text-indigo-400 prose-a:no-underline hover:prose-a:underline
            prose-blockquote:border-indigo-500/50 prose-blockquote:text-zinc-400
            prose-code:text-indigo-300 prose-code:bg-white/5 prose-code:rounded prose-code:px-1
            prose-pre:bg-[#0D1117] prose-pre:border prose-pre:border-white/5
            prose-strong:text-zinc-200
            prose-li:text-zinc-300
            prose-hr:border-white/10
          ">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeHighlight, rehypeSlug]}
              components={{
                // Render [n] citation superscripts
                p: ({ children }) => (
                  <p>
                    {typeof children === 'string'
                      ? renderCitations(children)
                      : children}
                  </p>
                ),
              }}
            >
              {report.report_markdown}
            </ReactMarkdown>
          </div>
        </div>
      </div>

      {/* ── Right sidebar ────────────────────────────────────────────────── */}
      <div className="w-80 shrink-0 border-l border-white/5 overflow-y-auto flex flex-col gap-0 glass">

        {/* Quality score */}
        {report.quality_score && (
          <section className="p-5 border-b border-white/5">
            <h3 className="flex items-center gap-2 text-xs font-semibold text-zinc-400 uppercase tracking-wide mb-4">
              <FlaskConical className="h-3.5 w-3.5" />
              Quality Score
            </h3>
            <QualityBreakdown score={report.quality_score} />
          </section>
        )}

        {/* Fact-check summary */}
        {report.fact_check_summary && (
          <section className="p-5 border-b border-white/5">
            <h3 className="flex items-center gap-2 text-xs font-semibold text-zinc-400 uppercase tracking-wide mb-4">
              <BookOpen className="h-3.5 w-3.5" />
              Fact Check
            </h3>
            <FactCheckSummaryCard summary={report.fact_check_summary} />
          </section>
        )}

        {/* Confidence */}
        {report.overall_confidence !== null && report.overall_confidence !== undefined && (
          <section className="px-5 py-3 border-b border-white/5">
            <div className="flex items-center justify-between">
              <span className="text-xs text-zinc-500">Confidence</span>
              <span className={`text-sm font-semibold tabular-nums ${scoreColor(report.overall_confidence)}`}>
                {pct(report.overall_confidence)}
              </span>
            </div>
          </section>
        )}

        {/* Sources */}
        {report.sources.length > 0 && (
          <section className="p-5">
            <h3 className="text-xs font-semibold text-zinc-400 uppercase tracking-wide mb-4">
              Sources ({report.sources.length})
            </h3>
            <div className="space-y-3">
              {report.sources.map((src) => (
                <SourceCard key={src.source_index} source={src} />
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  )
}

/** Replace [n] markers in plain text with styled superscript spans. */
function renderCitations(text: string): React.ReactNode {
  const parts = text.split(/(\[\d+\])/g)
  return parts.map((part, i) => {
    const match = part.match(/^\[(\d+)\]$/)
    if (match) {
      return (
        <sup
          key={i}
          className="mx-0.5 cursor-pointer rounded bg-indigo-500/20 px-1 py-0.5 text-[10px] font-semibold text-indigo-400 hover:bg-indigo-500/40 transition-colors"
          title={`Source ${match[1]}`}
          onClick={() => {
            document.getElementById(`source-${match[1]}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' })
          }}
        >
          {match[1]}
        </sup>
      )
    }
    return part
  })
}
