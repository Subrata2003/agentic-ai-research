import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  FlaskConical, Zap, BookOpen, ShieldCheck,
  BarChart3, FileDown, ArrowRight, CheckCircle2,
} from 'lucide-react'
import { useAnalytics } from '@/hooks/useReports'
import { pct } from '@/lib/utils'

// ── Feature card data ────────────────────────────────────────────────────────
const FEATURES = [
  {
    icon: Zap,
    title: 'Multi-Agent Pipeline',
    description: 'Planner → Parallel Researcher → Synthesizer → Fact-Checker → Critic → Scorer — all running autonomously.',
    color: 'text-amber-400',
    bg: 'bg-amber-400/10',
  },
  {
    icon: FlaskConical,
    title: 'Live Agent Terminal',
    description: 'Watch every agent narrate their work in real time. Reconnects automatically on network drops.',
    color: 'text-indigo-400',
    bg: 'bg-indigo-400/10',
  },
  {
    icon: BookOpen,
    title: 'Inline Citations',
    description: 'Every claim ends with a [n] marker. Click it to jump directly to the verbatim source quote.',
    color: 'text-sky-400',
    bg: 'bg-sky-400/10',
  },
  {
    icon: ShieldCheck,
    title: 'Fact Checking',
    description: 'Fuzzy-match verifier cross-references every citation against raw source material (70% threshold).',
    color: 'text-emerald-400',
    bg: 'bg-emerald-400/10',
  },
  {
    icon: BarChart3,
    title: 'Quality Scoring',
    description: 'Four-dimension score: Source Coverage, Citation Accuracy, Synthesis Coherence, Factual Density.',
    color: 'text-violet-400',
    bg: 'bg-violet-400/10',
  },
  {
    icon: FileDown,
    title: 'PDF Export & History',
    description: 'Every report is persisted to SQLite and ChromaDB. Past research improves future planning.',
    color: 'text-rose-400',
    bg: 'bg-rose-400/10',
  },
]

const PIPELINE_STEPS = [
  { label: 'Plan',        color: 'bg-violet-500' },
  { label: 'Research',    color: 'bg-sky-500'    },
  { label: 'Synthesize',  color: 'bg-indigo-500' },
  { label: 'Fact-check',  color: 'bg-emerald-500'},
  { label: 'Critique',    color: 'bg-amber-500'  },
  { label: 'Score',       color: 'bg-rose-500'   },
  { label: 'Report',      color: 'bg-teal-500'   },
]

// ── Animation variants ───────────────────────────────────────────────────────
const fadeUp = {
  initial:   { opacity: 0, y: 20 },
  animate:   { opacity: 1, y: 0  },
}

export default function LandingPage() {
  const navigate   = useNavigate()
  const { data }   = useAnalytics()

  return (
    <div className="overflow-y-auto h-full">
      <div className="max-w-5xl mx-auto px-6 py-16 space-y-24">

        {/* ── Hero ──────────────────────────────────────────────────────── */}
        <motion.section
          className="text-center space-y-6"
          initial="initial"
          animate="animate"
          transition={{ staggerChildren: 0.1 }}
        >
          {/* Badge */}
          <motion.div variants={fadeUp} className="flex justify-center">
            <span className="inline-flex items-center gap-2 rounded-full border border-indigo-500/30 bg-indigo-500/10 px-4 py-1.5 text-xs font-medium text-indigo-300">
              <span className="h-1.5 w-1.5 rounded-full bg-indigo-400 animate-pulse" />
              Powered by Gemini · LangChain · Tavily
            </span>
          </motion.div>

          {/* Headline */}
          <motion.h1
            variants={fadeUp}
            className="text-5xl font-extrabold tracking-tight text-white leading-tight"
          >
            Research at the speed<br />
            <span className="bg-gradient-to-r from-indigo-400 via-violet-400 to-sky-400 bg-clip-text text-transparent">
              of thought
            </span>
          </motion.h1>

          <motion.p
            variants={fadeUp}
            className="text-lg text-zinc-400 max-w-xl mx-auto leading-relaxed"
          >
            A fully autonomous multi-agent AI that plans, researches, synthesizes,
            fact-checks, and critiques — then delivers a cited, scored report.
          </motion.p>

          {/* CTA buttons */}
          <motion.div variants={fadeUp} className="flex items-center justify-center gap-3 pt-2">
            <button
              onClick={() => navigate('/research')}
              className="flex items-center gap-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-500/25 transition-all active:scale-95"
            >
              Start Researching
              <ArrowRight className="h-4 w-4" />
            </button>
            <button
              onClick={() => navigate('/history')}
              className="rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 px-6 py-3 text-sm font-medium text-zinc-300 transition-all"
            >
              View Reports
            </button>
          </motion.div>

          {/* Live stats */}
          {data && data.total_reports > 0 && (
            <motion.div
              variants={fadeUp}
              className="flex items-center justify-center gap-6 pt-2"
            >
              <Stat label="Reports generated" value={String(data.total_reports)} />
              {data.avg_quality !== null && data.avg_quality !== undefined && (
                <Stat label="Avg quality" value={pct(data.avg_quality)} />
              )}
              {data.total_sources_analysed && (
                <Stat label="Sources analysed" value={String(data.total_sources_analysed)} />
              )}
            </motion.div>
          )}
        </motion.section>

        {/* ── Pipeline visualisation ─────────────────────────────────────── */}
        <motion.section
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.4 }}
          className="space-y-4"
        >
          <p className="text-center text-xs uppercase tracking-widest text-zinc-600 font-medium">
            The pipeline
          </p>
          <div className="flex items-center justify-center gap-1 flex-wrap">
            {PIPELINE_STEPS.map((step, i) => (
              <div key={step.label} className="flex items-center gap-1">
                <span className={`rounded-lg ${step.bg} px-3 py-1.5 text-xs font-semibold text-white`}>
                  {step.label}
                </span>
                {i < PIPELINE_STEPS.length - 1 && (
                  <ArrowRight className="h-3 w-3 text-zinc-700 shrink-0" />
                )}
              </div>
            ))}
          </div>
        </motion.section>

        {/* ── Feature grid ──────────────────────────────────────────────── */}
        <motion.section
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.3, staggerChildren: 0.08 }}
          className="space-y-6"
        >
          <p className="text-center text-xs uppercase tracking-widest text-zinc-600 font-medium">
            What's inside
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {FEATURES.map((f, i) => (
              <motion.div
                key={f.title}
                initial={{ opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.3, delay: i * 0.06 }}
                className="rounded-xl border border-white/5 bg-white/[0.03] p-5 hover:border-white/10 transition-colors"
              >
                <div className={`inline-flex rounded-lg p-2 ${f.bg} mb-3`}>
                  <f.icon className={`h-4 w-4 ${f.color}`} />
                </div>
                <h3 className="text-sm font-semibold text-zinc-200 mb-1">{f.title}</h3>
                <p className="text-xs text-zinc-500 leading-relaxed">{f.description}</p>
              </motion.div>
            ))}
          </div>
        </motion.section>

        {/* ── Bottom CTA ────────────────────────────────────────────────── */}
        <motion.section
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.4 }}
          className="rounded-2xl border border-indigo-500/20 bg-indigo-500/5 p-10 text-center space-y-4"
        >
          <h2 className="text-2xl font-bold text-white">Ready to dive in?</h2>
          <p className="text-sm text-zinc-400">
            Enter any topic and let the agents do the heavy lifting.
          </p>
          <ul className="flex items-center justify-center gap-6 text-xs text-zinc-500">
            {['Parallel web research', 'Inline citations', 'Quality score', 'PDF export'].map((t) => (
              <li key={t} className="flex items-center gap-1.5">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                {t}
              </li>
            ))}
          </ul>
          <button
            onClick={() => navigate('/research')}
            className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 px-8 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-500/20 transition-all active:scale-95"
          >
            Start Researching
            <ArrowRight className="h-4 w-4" />
          </button>
        </motion.section>

      </div>
    </div>
  )
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="text-center">
      <p className="text-lg font-bold text-white tabular-nums">{value}</p>
      <p className="text-xs text-zinc-600">{label}</p>
    </div>
  )
}
