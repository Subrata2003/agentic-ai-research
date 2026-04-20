import { useEffect, useMemo, useRef, useState } from 'react'
import { List } from 'lucide-react'

interface TocItem {
  id: string
  text: string
  level: number   // 2 = ##, 3 = ###
}

function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .trim()
}

/** Parse ## and ### headings from raw markdown into TocItem[]. */
function parseHeadings(markdown: string): TocItem[] {
  const lines = markdown.split('\n')
  const items: TocItem[] = []
  for (const line of lines) {
    const m = line.match(/^(#{2,3})\s+(.+)/)
    if (m) {
      const text = m[2].replace(/[*_`]/g, '').trim()
      items.push({ id: slugify(text), text, level: m[1].length })
    }
  }
  return items
}

interface TableOfContentsProps {
  markdown: string
}

export default function TableOfContents({ markdown }: TableOfContentsProps) {
  const items = useMemo(() => parseHeadings(markdown), [markdown])
  const [activeId, setActiveId] = useState<string>('')
  const observerRef = useRef<IntersectionObserver | null>(null)

  // Scroll-spy via IntersectionObserver
  useEffect(() => {
    if (items.length === 0) return

    observerRef.current?.disconnect()

    const headingEls = items
      .map((item) => document.getElementById(item.id))
      .filter(Boolean) as HTMLElement[]

    if (headingEls.length === 0) return

    observerRef.current = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            setActiveId(entry.target.id)
            break
          }
        }
      },
      { rootMargin: '-10% 0px -80% 0px', threshold: 0 },
    )

    headingEls.forEach((el) => observerRef.current!.observe(el))

    return () => observerRef.current?.disconnect()
  }, [items])

  const handleClick = (id: string) => {
    const el = document.getElementById(id)
    if (!el) return
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    setActiveId(id)
  }

  if (items.length === 0) return null

  return (
    <section className="p-5 border-b border-white/5">
      <h3 className="flex items-center gap-2 text-xs font-semibold text-zinc-400 uppercase tracking-wide mb-3">
        <List className="h-3.5 w-3.5" />
        Contents
      </h3>

      <nav className="space-y-0.5">
        {items.map((item) => {
          const isActive = activeId === item.id
          return (
            <button
              key={item.id}
              onClick={() => handleClick(item.id)}
              className={[
                'w-full text-left rounded-md px-2 py-1.5 text-xs leading-snug transition-all duration-150',
                item.level === 3 ? 'pl-5' : '',
                isActive
                  ? 'bg-indigo-500/10 text-indigo-300 font-medium'
                  : 'text-zinc-500 hover:text-zinc-300 hover:bg-white/5',
              ].join(' ')}
            >
              {/* Active indicator dot */}
              {isActive && (
                <span className="inline-block h-1.5 w-1.5 rounded-full bg-indigo-400 mr-1.5 align-middle" />
              )}
              {item.text}
            </button>
          )
        })}
      </nav>
    </section>
  )
}
