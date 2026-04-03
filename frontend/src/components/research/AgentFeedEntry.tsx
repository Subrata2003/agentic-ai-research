import type { AgentMessage, AgentType } from '@/types/research'
import { memo } from 'react'

const AGENT_STYLES: Record<AgentType | 'system', { label: string; color: string }> = {
  planner:      { label: 'Planner',      color: 'text-violet-400' },
  researcher:   { label: 'Researcher',   color: 'text-sky-400'    },
  synthesizer:  { label: 'Synthesizer',  color: 'text-emerald-400' },
  reporter:     { label: 'Reporter',     color: 'text-amber-400'  },
  system:       { label: 'System',       color: 'text-zinc-400'   },
}

function formatTime(iso: string): string {
  try {
    return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  } catch {
    return ''
  }
}

interface AgentFeedEntryProps {
  message: AgentMessage
}

const AgentFeedEntry = memo(function AgentFeedEntry({ message }: AgentFeedEntryProps) {
  const style = AGENT_STYLES[message.agent] ?? AGENT_STYLES.system

  return (
    <div className="flex gap-3 py-1 group">
      {/* Timestamp */}
      <span className="shrink-0 font-mono text-[11px] text-zinc-600 pt-0.5 w-[72px] text-right select-none">
        {formatTime(message.timestamp)}
      </span>

      {/* Agent badge */}
      <span className={`shrink-0 font-mono text-[11px] font-semibold w-[82px] ${style.color} select-none`}>
        [{style.label}]
      </span>

      {/* Message */}
      <span className="font-mono text-[12px] text-zinc-300 leading-relaxed break-words min-w-0">
        {message.message}
      </span>
    </div>
  )
})

export default AgentFeedEntry
