import { useState, useCallback } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Search, Loader2 } from 'lucide-react'
import { api } from '@/services/api'
import { useResearchStore } from '@/store/researchStore'
import { useSimilarReports } from '@/hooks/useSimilarReports'
import type { ResearchDepth } from '@/types/api'
import DepthSelector from './DepthSelector'
import ExampleTopics from './ExampleTopics'

export default function ResearchForm() {
  const [topic, setTopic]   = useState('')
  const [depth, setDepth]   = useState<ResearchDepth>('medium')

  const startJob  = useResearchStore((s) => s.startJob)
  const status    = useResearchStore((s) => s.status)

  const busy = status !== 'idle' && status !== 'complete' && status !== 'error' && status !== 'failed'

  const { data: similar } = useSimilarReports(topic)

  const mutation = useMutation({
    mutationFn: () => api.startResearch({ topic: topic.trim(), depth, save_report: true }),
    onSuccess: (data) => {
      startJob(data.job_id)
    },
  })

  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault()
      if (!topic.trim() || busy) return
      mutation.mutate()
    },
    [topic, busy, mutation],
  )

  const handleExample = useCallback((t: string) => {
    setTopic(t)
  }, [])

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* Topic input */}
      <div className="relative">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-zinc-500 pointer-events-none" />
        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          disabled={busy}
          placeholder="Enter a research topic…"
          className={[
            'w-full rounded-xl border bg-white/5 pl-12 pr-4 py-4',
            'text-white placeholder:text-zinc-500 text-sm',
            'focus:outline-none focus:ring-2 focus:ring-indigo-500',
            'transition-colors duration-150',
            busy
              ? 'cursor-not-allowed opacity-60 border-white/10'
              : 'border-white/10 hover:border-white/20',
          ].join(' ')}
        />
      </div>

      {/* Example topics */}
      <ExampleTopics onSelect={handleExample} disabled={busy} />

      {/* Depth selector */}
      <DepthSelector value={depth} onChange={setDepth} disabled={busy} />

      {/* Similar reports hint */}
      {similar && similar.length > 0 && (
        <p className="text-xs text-zinc-500 flex items-center gap-1.5">
          <span className="inline-block h-1.5 w-1.5 rounded-full bg-amber-400" />
          {similar.length} similar report{similar.length > 1 ? 's' : ''} already exist for this topic.
        </p>
      )}

      {/* Submit */}
      <button
        type="submit"
        disabled={!topic.trim() || busy}
        className={[
          'w-full rounded-xl py-4 font-semibold text-sm transition-all duration-200',
          'focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500',
          !topic.trim() || busy
            ? 'cursor-not-allowed bg-indigo-600/30 text-indigo-400/50'
            : 'bg-indigo-600 hover:bg-indigo-500 active:scale-[0.99] text-white shadow-lg shadow-indigo-500/20',
        ].join(' ')}
      >
        {mutation.isPending ? (
          <span className="flex items-center justify-center gap-2">
            <Loader2 className="h-4 w-4 animate-spin" />
            Starting research…
          </span>
        ) : (
          'Start Research'
        )}
      </button>

      {mutation.isError && (
        <p className="text-xs text-red-400 text-center">
          Failed to start: {(mutation.error as Error).message}
        </p>
      )}
    </form>
  )
}
