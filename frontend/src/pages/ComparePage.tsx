import { useMemo } from 'react'
import { diff_match_patch } from 'diff-match-patch'
import { ArrowLeftRight, GitCompare, Loader2 } from 'lucide-react'
import { useCompareStore } from '@/store/compareStore'
import { useReport, useReports } from '@/hooks/useReports'
import { pct, scoreColor, formatDate } from '@/lib/utils'
import ScoreBadge from '@/components/reports/ScoreBadge'
import type { ReportDetail, ReportListItem } from '@/types/api'

// ── Diff renderer ────────────────────────────────────────────────────────────

function DiffView({ leftText, rightText }: { leftText: string; rightText: string }) {
  const { leftHtml, rightHtml } = useMemo(() => {
    const dmp    = new diff_match_patch()
    const diffs  = dmp.diff_main(leftText, rightText)
    dmp.diff_cleanupSemantic(diffs)

    let left  = ''
    let right = ''

    for (const [op, text] of diffs) {
      const escaped = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/\n/g, '<br/>')

      if (op === 0) {        // equal
        left  += escaped
        right += escaped
      } else if (op === -1) { // delete (only on left)
        left += `<mark class="diff-del">${escaped}</mark>`
      } else {                // insert (only on right)
        right += `<mark class="diff-ins">${escaped}</mark>`
      }
    }
    return { leftHtml: left, rightHtml: right }
  }, [leftText, rightText])

  return (
    <>
      <div
        className="diff-pane flex-1 overflow-y-auto"
        dangerouslySetInnerHTML={{ __html: leftHtml }}
      />
      <div className="w-px bg-white/5 shrink-0" />
      <div
        className="diff-pane flex-1 overflow-y-auto"
        dangerouslySetInnerHTML={{ __html: rightHtml }}
      />
    </>
  )
}

// ── Report selector ──────────────────────────────────────────────────────────

function ReportSelector({
  value,
  onChange,
  exclude,
  label,
}: {
  value: string | null
  onChange: (id: string | null) => void
  exclude?: string | null
  label: string
}) {
  const { data } = useReports({ limit: 50, sort: 'newest' })
  const items = (data?.items ?? []).filter((r: ReportListItem) => r.id !== exclude)

  return (
    <div className="flex-1 min-w-0">
      <p className="text-xs text-zinc-500 mb-1.5 font-medium uppercase tracking-wide">{label}</p>
      <select
        value={value ?? ''}
        onChange={(e) => onChange(e.target.value || null)}
        className="w-full rounded-lg border border-white/10 bg-[#0D1117] px-3 py-2 text-sm text-zinc-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 cursor-pointer truncate"
      >
        <option value="">Select a report…</option>
        {items.map((r: ReportListItem) => (
          <option key={r.id} value={r.id}>
            {r.topic} · {r.depth}
          </option>
        ))}
      </select>
    </div>
  )
}

// ── Score comparison row ─────────────────────────────────────────────────────

function ScoreRow({
  label,
  left,
  right,
}: {
  label: string
  left: number | null
  right: number | null
}) {
  const winner =
    left !== null && right !== null
      ? left > right ? 'left' : right > left ? 'right' : 'tie'
      : null

  return (
    <div className="flex items-center gap-3 py-1.5 border-b border-white/5 last:border-0">
      <span className={`text-xs tabular-nums w-12 text-right font-semibold ${left !== null ? scoreColor(left) : 'text-zinc-600'}`}>
        {left !== null ? pct(left) : '—'}
        {winner === 'left' && ' ↑'}
      </span>
      <span className="flex-1 text-center text-xs text-zinc-500">{label}</span>
      <span className={`text-xs tabular-nums w-12 text-left font-semibold ${right !== null ? scoreColor(right) : 'text-zinc-600'}`}>
        {winner === 'right' && '↑ '}
        {right !== null ? pct(right) : '—'}
      </span>
    </div>
  )
}

// ── Side header ──────────────────────────────────────────────────────────────

function SideHeader({ report }: { report: ReportDetail }) {
  return (
    <div className="px-5 py-3 border-b border-white/5 bg-white/[0.02]">
      <p className="text-sm font-medium text-zinc-200 line-clamp-1">{report.topic}</p>
      <p className="text-xs text-zinc-500 mt-0.5">
        {report.depth} · {report.num_sources} sources · {formatDate(report.created_at)}
      </p>
    </div>
  )
}

// ── Main page ────────────────────────────────────────────────────────────────

export default function ComparePage() {
  const { leftId, rightId, setLeft, setRight, swap } = useCompareStore()

  const { data: leftReport,  isLoading: loadingLeft  } = useReport(leftId  ?? undefined)
  const { data: rightReport, isLoading: loadingRight } = useReport(rightId ?? undefined)

  const ready = leftReport && rightReport

  return (
    <div className="flex flex-col h-full overflow-hidden">

      {/* ── Control bar ───────────────────────────────────────────────── */}
      <div className="shrink-0 flex items-end gap-3 px-6 py-4 border-b border-white/5">
        <ReportSelector value={leftId}  onChange={setLeft}  exclude={rightId} label="Report A" />

        <button
          onClick={swap}
          disabled={!leftId && !rightId}
          title="Swap reports"
          className="shrink-0 mb-0.5 rounded-lg border border-white/10 p-2 text-zinc-400 hover:text-zinc-200 hover:border-white/20 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
        >
          <ArrowLeftRight className="h-4 w-4" />
        </button>

        <ReportSelector value={rightId} onChange={setRight} exclude={leftId}  label="Report B" />
      </div>

      {/* ── Body ──────────────────────────────────────────────────────── */}
      {!leftId && !rightId ? (
        /* Empty state */
        <div className="flex-1 flex flex-col items-center justify-center gap-3 text-zinc-500">
          <GitCompare className="h-12 w-12 text-zinc-700" />
          <p className="text-sm">Select two reports above to compare them side-by-side.</p>
        </div>
      ) : loadingLeft || loadingRight ? (
        <div className="flex-1 flex items-center justify-center gap-3 text-zinc-400">
          <Loader2 className="h-5 w-5 animate-spin" />
          Loading reports…
        </div>
      ) : (
        <div className="flex-1 flex flex-col overflow-hidden">

          {/* Score comparison strip */}
          {(leftReport || rightReport) && (
            <div className="shrink-0 border-b border-white/5 px-6 py-3">
              <div className="max-w-lg mx-auto space-y-0">
                <ScoreRow
                  label="Overall Quality"
                  left={leftReport?.overall_score ?? null}
                  right={rightReport?.overall_score ?? null}
                />
                <ScoreRow
                  label="Source Coverage"
                  left={leftReport?.quality_score?.source_coverage ?? null}
                  right={rightReport?.quality_score?.source_coverage ?? null}
                />
                <ScoreRow
                  label="Citation Accuracy"
                  left={leftReport?.quality_score?.citation_accuracy ?? null}
                  right={rightReport?.quality_score?.citation_accuracy ?? null}
                />
                <ScoreRow
                  label="Coherence"
                  left={leftReport?.quality_score?.synthesis_coherence ?? null}
                  right={rightReport?.quality_score?.synthesis_coherence ?? null}
                />
                <ScoreRow
                  label="Confidence"
                  left={leftReport?.overall_confidence ?? null}
                  right={rightReport?.overall_confidence ?? null}
                />
              </div>
            </div>
          )}

          {/* Column headers */}
          <div className="shrink-0 flex border-b border-white/5">
            <div className="flex-1 min-w-0">
              {leftReport
                ? <SideHeader report={leftReport} />
                : <div className="px-5 py-3 text-sm text-zinc-600 italic">No report selected</div>}
            </div>
            <div className="w-px bg-white/5 shrink-0" />
            <div className="flex-1 min-w-0">
              {rightReport
                ? <SideHeader report={rightReport} />
                : <div className="px-5 py-3 text-sm text-zinc-600 italic">No report selected</div>}
            </div>
          </div>

          {/* Badge row */}
          <div className="shrink-0 flex border-b border-white/5">
            <div className="flex-1 px-5 py-2 flex items-center gap-2">
              <ScoreBadge score={leftReport?.overall_score ?? null} size="sm" />
              <span className="text-xs text-zinc-600">{leftReport?.num_sources ?? '—'} sources</span>
            </div>
            <div className="w-px bg-white/5 shrink-0" />
            <div className="flex-1 px-5 py-2 flex items-center gap-2">
              <ScoreBadge score={rightReport?.overall_score ?? null} size="sm" />
              <span className="text-xs text-zinc-600">{rightReport?.num_sources ?? '—'} sources</span>
            </div>
          </div>

          {/* Diff content */}
          <div className="flex-1 flex overflow-hidden font-mono text-[12px] text-zinc-300 leading-relaxed">
            {ready ? (
              <DiffView
                leftText={leftReport.report_markdown}
                rightText={rightReport.report_markdown}
              />
            ) : (
              <>
                <div className="diff-pane flex-1 overflow-y-auto">
                  {leftReport && (
                    <pre className="whitespace-pre-wrap break-words px-5 py-4">
                      {leftReport.report_markdown}
                    </pre>
                  )}
                </div>
                <div className="w-px bg-white/5 shrink-0" />
                <div className="diff-pane flex-1 overflow-y-auto">
                  {rightReport && (
                    <pre className="whitespace-pre-wrap break-words px-5 py-4">
                      {rightReport.report_markdown}
                    </pre>
                  )}
                </div>
              </>
            )}
          </div>

        </div>
      )}
    </div>
  )
}
