import type { ResearchDepth } from '@/types/api'

interface DepthOption {
  value: ResearchDepth
  label: string
  description: string
  icon: string
  time: string
}

const DEPTH_OPTIONS: DepthOption[] = [
  {
    value: 'shallow',
    label: 'Quick Scan',
    description: 'Fast overview, 3–5 sources',
    icon: '⚡',
    time: '~30s',
  },
  {
    value: 'medium',
    label: 'Standard',
    description: 'Balanced depth, 8–12 sources',
    icon: '🔍',
    time: '~90s',
  },
  {
    value: 'deep',
    label: 'Deep Dive',
    description: 'Comprehensive, 15+ sources',
    icon: '🔬',
    time: '~3 min',
  },
]

interface DepthSelectorProps {
  value: ResearchDepth
  onChange: (depth: ResearchDepth) => void
  disabled?: boolean
}

export default function DepthSelector({ value, onChange, disabled }: DepthSelectorProps) {
  return (
    <div className="grid grid-cols-3 gap-2">
      {DEPTH_OPTIONS.map((opt) => {
        const selected = value === opt.value
        return (
          <button
            key={opt.value}
            type="button"
            disabled={disabled}
            onClick={() => onChange(opt.value)}
            className={[
              'rounded-xl border px-3 py-3 text-left transition-all duration-150',
              'focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500',
              disabled ? 'cursor-not-allowed opacity-50' : 'cursor-pointer',
              selected
                ? 'border-indigo-500 bg-indigo-500/10 text-indigo-300'
                : 'border-white/10 bg-white/5 text-zinc-400 hover:border-white/20 hover:text-zinc-200',
            ].join(' ')}
          >
            <div className="flex items-center gap-1.5 mb-1.5">
              <span className="text-sm leading-none">{opt.icon}</span>
              <span className="font-semibold text-xs leading-tight">{opt.label}</span>
            </div>
            <p className="text-[11px] text-zinc-500 leading-snug mb-1">{opt.description}</p>
            <span
              className={[
                'text-[10px] font-mono font-medium',
                selected ? 'text-indigo-400' : 'text-zinc-600',
              ].join(' ')}
            >
              {opt.time}
            </span>
          </button>
        )
      })}
    </div>
  )
}
