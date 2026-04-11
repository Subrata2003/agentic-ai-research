import { useEffect, useRef, useState } from 'react'
import { useResearchStore } from '@/store/researchStore'

/**
 * Thin 3px progress bar pinned to the very top of the viewport.
 * Reads live progress from researchStore — visible on every page.
 *
 * Behaviour:
 *  - Appears as soon as a job is queued (fades in)
 *  - Fills smoothly as progress 0 → 1
 *  - On complete: snaps to 100%, holds 600ms, then fades out
 *  - On error:   turns red, holds 800ms, then fades out
 *  - Hidden when idle
 */
export default function GlobalProgressBar() {
  const status   = useResearchStore((s) => s.status)
  const progress = useResearchStore((s) => s.progress)

  const [visible,  setVisible]  = useState(false)
  const [width,    setWidth]    = useState(0)
  const [color,    setColor]    = useState<'indigo' | 'red'>('indigo')
  const hideTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    if (hideTimer.current) clearTimeout(hideTimer.current)

    if (status === 'idle') {
      setVisible(false)
      setWidth(0)
      return
    }

    if (status === 'error' || status === 'failed') {
      setColor('red')
      setWidth(100)
      setVisible(true)
      hideTimer.current = setTimeout(() => {
        setVisible(false)
        setWidth(0)
        setColor('indigo')
      }, 900)
      return
    }

    if (status === 'complete') {
      setColor('indigo')
      setWidth(100)
      setVisible(true)
      hideTimer.current = setTimeout(() => {
        setVisible(false)
        setWidth(0)
      }, 700)
      return
    }

    // queued / streaming / reconnecting
    setColor('indigo')
    setVisible(true)
    // Never let it sit at 0 — show at least 4% immediately
    setWidth(Math.max(4, Math.round(progress * 100)))

    return () => {
      if (hideTimer.current) clearTimeout(hideTimer.current)
    }
  }, [status, progress])

  if (!visible) return null

  const barColor = color === 'red'
    ? 'bg-red-500'
    : 'bg-gradient-to-r from-indigo-500 via-violet-500 to-indigo-400'

  return (
    <div
      className="fixed top-0 left-0 right-0 z-[9999] h-[3px] pointer-events-none"
      style={{ background: 'rgba(0,0,0,0.15)' }}
    >
      {/* Fill */}
      <div
        className={`h-full ${barColor} transition-all duration-300 ease-out`}
        style={{ width: `${width}%` }}
      />

      {/* Shimmer glow at the leading edge */}
      {status !== 'complete' && status !== 'error' && status !== 'failed' && (
        <div
          className="absolute top-0 h-full w-24 pointer-events-none"
          style={{
            left:       `calc(${width}% - 6rem)`,
            background: 'linear-gradient(to right, transparent, rgba(139,92,246,0.7), transparent)',
            transition: 'left 0.3s ease-out',
          }}
        />
      )}
    </div>
  )
}
