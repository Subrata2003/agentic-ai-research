import { EXAMPLE_TOPICS as EXAMPLES } from '@/lib/constants'

interface ExampleTopicsProps {
  onSelect: (topic: string) => void
  disabled?: boolean
}

export default function ExampleTopics({ onSelect, disabled }: ExampleTopicsProps) {
  return (
    <div className="flex flex-wrap gap-2">
      <span className="text-xs text-zinc-500 self-center mr-1">Try:</span>
      {EXAMPLES.map((topic) => (
        <button
          key={topic}
          type="button"
          disabled={disabled}
          onClick={() => onSelect(topic)}
          className={[
            'rounded-full border border-white/10 bg-white/5 px-3 py-1',
            'text-xs text-zinc-400 transition-all duration-150',
            disabled
              ? 'cursor-not-allowed opacity-40'
              : 'cursor-pointer hover:border-indigo-500/50 hover:bg-indigo-500/10 hover:text-indigo-300',
          ].join(' ')}
        >
          {topic}
        </button>
      ))}
    </div>
  )
}
