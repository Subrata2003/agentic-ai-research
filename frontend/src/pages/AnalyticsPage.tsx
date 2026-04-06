import { useNavigate } from 'react-router-dom'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts'
import { FileText, Layers, Star, BookOpen, Loader2 } from 'lucide-react'
import { useAnalytics } from '@/hooks/useReports'
import { pct, scoreColor, timeAgo } from '@/lib/utils'
import ScoreBadge from '@/components/reports/ScoreBadge'

// ── Colour palettes ──────────────────────────────────────────────────────────
const DEPTH_COLORS: Record<string, string> = {
  shallow: '#818cf8',
  medium:  '#6366f1',
  deep:    '#4338ca',
}

const FACT_COLORS: Record<string, string> = {
  SUPPORTED:    '#34d399',
  UNVERIFIABLE: '#fbbf24',
  CONTRADICTED: '#f87171',
}

// ── Stat card ────────────────────────────────────────────────────────────────
function StatCard({
  icon: Icon,
  label,
  value,
  sub,
  valueClass = 'text-white',
}: {
  icon: React.ElementType
  label: string
  value: string
  sub?: string
  valueClass?: string
}) {
  return (
    <div className="card-hover rounded-xl border border-white/5 bg-white/[0.04] p-5 glass-light">
      <div className="flex items-center gap-2 mb-3">
        <Icon className="h-4 w-4 text-zinc-500" />
        <span className="text-xs text-zinc-500 uppercase tracking-wide font-medium">{label}</span>
      </div>
      <p className={`text-3xl font-bold tabular-nums ${valueClass}`}>{value}</p>
      {sub && <p className="text-xs text-zinc-600 mt-1">{sub}</p>}
    </div>
  )
}

// ── Custom tooltip ────────────────────────────────────────────────────────────
function ChartTooltip({ active, payload, label }: {
  active?: boolean
  payload?: Array<{ value: number; name?: string; fill?: string }>
  label?: string
}) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded-lg border border-white/10 bg-[#0D1117] px-3 py-2 text-xs shadow-xl">
      {label && <p className="text-zinc-400 mb-1 capitalize">{label}</p>}
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.fill ?? '#a1a1aa' }}>
          {p.name ?? label}: <span className="font-semibold">{p.value}</span>
        </p>
      ))}
    </div>
  )
}

export default function AnalyticsPage() {
  const navigate   = useNavigate()
  const { data, isLoading } = useAnalytics()

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center gap-3 text-zinc-400">
        <Loader2 className="h-5 w-5 animate-spin" />
        Loading analytics…
      </div>
    )
  }

  if (!data) return null

  // Build chart data
  const depthData = Object.entries(data.depth_distribution).map(([key, count]) => ({
    name: key.charAt(0).toUpperCase() + key.slice(1),
    count,
    fill: DEPTH_COLORS[key] ?? '#6366f1',
  }))

  const factData = Object.entries(data.fact_check_distribution).map(([key, count]) => ({
    name: key.charAt(0) + key.slice(1).toLowerCase(),
    value: count,
    fill: FACT_COLORS[key] ?? '#a1a1aa',
  }))

  const avgQuality = data.avg_quality !== null && data.avg_quality !== undefined
    ? data.avg_quality : null

  return (
    <div className="flex flex-col h-full overflow-y-auto">
      <div className="px-8 pt-8 pb-6 space-y-8 max-w-6xl w-full mx-auto">

        {/* Page title */}
        <div>
          <h1 className="text-xl font-bold text-white">Analytics</h1>
          <p className="text-sm text-zinc-500 mt-0.5">Research quality across all reports</p>
        </div>

        {/* ── Stat cards ──────────────────────────────────────────────────── */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            icon={FileText}
            label="Total Reports"
            value={String(data.total_reports)}
            sub={data.total_sources_analysed ? `${data.total_sources_analysed} sources analysed` : undefined}
          />
          <StatCard
            icon={Star}
            label="Avg Quality"
            value={avgQuality !== null ? pct(avgQuality) : '—'}
            valueClass={avgQuality !== null ? scoreColor(avgQuality) : 'text-zinc-500'}
            sub="across all reports"
          />
          <StatCard
            icon={Layers}
            label="Avg Sources"
            value={data.avg_sources !== null && data.avg_sources !== undefined
              ? String(Math.round(data.avg_sources)) : '—'}
            sub="per report"
          />
          <StatCard
            icon={BookOpen}
            label="Avg Confidence"
            value={data.avg_confidence !== null && data.avg_confidence !== undefined
              ? pct(data.avg_confidence) : '—'}
            valueClass={data.avg_confidence !== null && data.avg_confidence !== undefined
              ? scoreColor(data.avg_confidence) : 'text-zinc-500'}
            sub="synthesizer confidence"
          />
        </div>

        {/* ── Charts row ──────────────────────────────────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

          {/* Depth distribution */}
          <div className="card-hover rounded-xl border border-white/5 bg-white/[0.04] p-5 glass-light">
            <h3 className="text-sm font-semibold text-zinc-300 mb-4">Reports by Depth</h3>
            {depthData.length === 0 ? (
              <p className="text-xs text-zinc-600 text-center py-8">No data yet.</p>
            ) : (
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={depthData} barSize={40}>
                  <XAxis
                    dataKey="name"
                    tick={{ fill: '#71717a', fontSize: 12 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    allowDecimals={false}
                    tick={{ fill: '#52525b', fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                    width={24}
                  />
                  <Tooltip content={<ChartTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
                  <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                    {depthData.map((entry, i) => (
                      <Cell key={i} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>

          {/* Fact-check distribution */}
          <div className="card-hover rounded-xl border border-white/5 bg-white/[0.04] p-5 glass-light">
            <h3 className="text-sm font-semibold text-zinc-300 mb-4">Fact-Check Verdicts</h3>
            {factData.length === 0 ? (
              <p className="text-xs text-zinc-600 text-center py-8">No data yet.</p>
            ) : (
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={factData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={75}
                    innerRadius={42}
                    paddingAngle={3}
                  >
                    {factData.map((entry, i) => (
                      <Cell key={i} fill={entry.fill} />
                    ))}
                  </Pie>
                  <Tooltip content={<ChartTooltip />} />
                  <Legend
                    iconType="circle"
                    iconSize={8}
                    formatter={(value) => (
                      <span style={{ color: '#a1a1aa', fontSize: 12 }}>{value}</span>
                    )}
                  />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* ── Recent reports ──────────────────────────────────────────────── */}
        {data.recent_reports.length > 0 && (
          <div>
            <h3 className="text-sm font-semibold text-zinc-300 mb-4">Recent Reports</h3>
            <div className="rounded-xl border border-white/5 overflow-hidden glass-light">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/5 bg-white/[0.02]">
                    <th className="text-left px-5 py-3 text-xs font-medium text-zinc-500">Topic</th>
                    <th className="text-right px-5 py-3 text-xs font-medium text-zinc-500">Quality</th>
                    <th className="text-right px-5 py-3 text-xs font-medium text-zinc-500">When</th>
                  </tr>
                </thead>
                <tbody>
                  {data.recent_reports.map((r) => (
                    <tr
                      key={r.id}
                      onClick={() => navigate(`/reports/${r.id}`)}
                      className="border-b border-white/5 last:border-0 cursor-pointer hover:bg-white/[0.03] transition-colors"
                    >
                      <td className="px-5 py-3 text-zinc-300 max-w-xs truncate">{r.topic}</td>
                      <td className="px-5 py-3 text-right">
                        <ScoreBadge score={r.overall_score} size="sm" />
                      </td>
                      <td className="px-5 py-3 text-right text-zinc-500 text-xs tabular-nums">
                        {timeAgo(r.created_at)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

      </div>
    </div>
  )
}
