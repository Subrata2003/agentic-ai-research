import { useEffect, useRef, useState } from 'react'

interface AnimatedScoreProps {
  /** 0–1 value */
  value: number
  duration?: number
  className?: string
  suffix?: string
}

/**
 * Counts up from 0 to `value * 100` when first mounted.
 */
export default function AnimatedScore({
  value,
  duration = 900,
  className = '',
  suffix = '%',
}: AnimatedScoreProps) {
  const [display, setDisplay] = useState(0)
  const rafRef = useRef<number | null>(null)

  useEffect(() => {
    const target  = Math.round(value * 100)
    const start   = performance.now()

    const tick = (now: number) => {
      const elapsed  = now - start
      const progress = Math.min(elapsed / duration, 1)
      // ease-out cubic
      const eased    = 1 - Math.pow(1 - progress, 3)
      setDisplay(Math.round(eased * target))
      if (progress < 1) {
        rafRef.current = requestAnimationFrame(tick)
      }
    }

    rafRef.current = requestAnimationFrame(tick)
    return () => { if (rafRef.current) cancelAnimationFrame(rafRef.current) }
  }, [value, duration])

  return (
    <span className={`tabular-nums animate-counter-in ${className}`}>
      {display}{suffix}
    </span>
  )
}
