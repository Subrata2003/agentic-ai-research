interface ProgressRingProps {
  /** 0–1 */
  progress: number
  /** diameter in px */
  size?: number
  strokeWidth?: number
  label?: string
}

/**
 * Circular SVG progress ring.
 * Smoothly animates via CSS transition on the stroke-dashoffset.
 */
export default function ProgressRing({
  progress,
  size = 120,
  strokeWidth = 8,
  label,
}: ProgressRingProps) {
  const r      = (size - strokeWidth) / 2
  const circ   = 2 * Math.PI * r
  const offset = circ * (1 - Math.min(1, Math.max(0, progress)))
  const pct    = Math.round(progress * 100)

  // Colour: indigo → emerald as progress grows
  const stroke = progress >= 0.9 ? '#34d399' : progress >= 0.5 ? '#818cf8' : '#6366f1'

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        {/* Track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="rgba(255,255,255,0.06)"
          strokeWidth={strokeWidth}
        />
        {/* Progress arc */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={stroke}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circ}
          strokeDashoffset={offset}
          style={{ transition: 'stroke-dashoffset 0.4s ease, stroke 0.6s ease' }}
        />
      </svg>

      {/* Centre label */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-2xl font-bold text-white tabular-nums">{pct}%</span>
        {label && <span className="text-[10px] text-zinc-500 mt-0.5 text-center px-2">{label}</span>}
      </div>
    </div>
  )
}
