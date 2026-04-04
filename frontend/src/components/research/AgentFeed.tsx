import { useEffect, useRef, useState, useCallback } from 'react'
import { ChevronDown } from 'lucide-react'
import { useResearchStore } from '@/store/researchStore'
import AgentFeedEntry from './AgentFeedEntry'

/**
 * Scrollable terminal-style feed of live agent messages.
 *
 * Auto-scrolls to the bottom as new messages arrive UNLESS the user
 * has manually scrolled up — in that case a "scroll to bottom" button appears.
 */
export default function AgentFeed() {
  const messages  = useResearchStore((s) => s.messages)
  const status    = useResearchStore((s) => s.status)

  const bottomRef   = useRef<HTMLDivElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const [userScrolled, setUserScrolled] = useState(false)

  // Detect manual upward scroll
  const handleScroll = useCallback(() => {
    const el = containerRef.current
    if (!el) return
    const atBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 40
    setUserScrolled(!atBottom)
  }, [])

  // Auto-scroll unless user scrolled up
  useEffect(() => {
    if (!userScrolled) {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, userScrolled])

  const scrollToBottom = () => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    setUserScrolled(false)
  }

  const isLive = status === 'streaming' || status === 'queued' || status === 'reconnecting'

  return (
    <div className="relative flex flex-col h-full">
      {/* Terminal header */}
      <div className="flex items-center gap-2 px-4 py-2.5 border-b border-white/5 bg-[#0D1117] shrink-0">
        {/* Traffic-light dots */}
        <span className="h-3 w-3 rounded-full bg-red-500/80" />
        <span className="h-3 w-3 rounded-full bg-amber-400/80" />
        <span className="h-3 w-3 rounded-full bg-emerald-500/80" />
        <span className="ml-3 font-mono text-xs text-zinc-500 select-none">agent-terminal</span>

        {isLive && (
          <span className="ml-auto flex items-center gap-1.5 text-xs text-emerald-400 font-mono">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
            LIVE
          </span>
        )}
      </div>

      {/* Messages area */}
      <div
        ref={containerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto bg-[#0D1117] px-4 py-3 font-mono"
      >
        {messages.length === 0 ? (
          <p className="font-mono text-xs text-zinc-600 italic">
            Waiting for agents…
          </p>
        ) : (
          messages.map((msg) => <AgentFeedEntry key={msg.id} message={msg} />)
        )}

        {/* Blinking cursor when live */}
        {isLive && (
          <span className="inline-block h-3 w-2 bg-zinc-400 animate-pulse ml-1 align-middle" />
        )}

        <div ref={bottomRef} />
      </div>

      {/* Jump-to-bottom button */}
      {userScrolled && (
        <button
          type="button"
          onClick={scrollToBottom}
          className="absolute bottom-4 right-4 flex items-center gap-1 rounded-full border border-white/10 bg-zinc-800 px-3 py-1.5 text-xs text-zinc-300 shadow-lg hover:bg-zinc-700 transition-colors"
        >
          <ChevronDown className="h-3.5 w-3.5" />
          Latest
        </button>
      )}
    </div>
  )
}
