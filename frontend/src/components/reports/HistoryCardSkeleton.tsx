import { Skeleton } from '@/components/ui/Skeleton'

export function HistoryCardSkeleton() {
  return (
    <div className="rounded-xl border border-white/5 bg-white/[0.03] p-5 space-y-3">
      {/* Title + badge row */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 space-y-2">
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-3 w-1/2" />
        </div>
        <Skeleton className="h-5 w-14 rounded-full shrink-0" />
      </div>
      {/* Score bar */}
      <Skeleton className="h-1.5 w-full rounded-full" />
      {/* Confidence line */}
      <Skeleton className="h-3 w-24" />
    </div>
  )
}

/** Grid of 6 skeleton cards to fill the History page on first load. */
export function HistoryGridSkeleton() {
  return (
    <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: 6 }).map((_, i) => (
        <HistoryCardSkeleton key={i} />
      ))}
    </div>
  )
}
