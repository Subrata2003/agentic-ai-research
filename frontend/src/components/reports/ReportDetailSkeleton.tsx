import { Skeleton } from '@/components/ui/Skeleton'

export function ReportDetailSkeleton() {
  return (
    <div className="flex h-full overflow-hidden">
      {/* Main content */}
      <div className="flex-1 overflow-y-auto px-8 pt-8 pb-16 space-y-6">
        {/* Meta line */}
        <div className="flex items-center gap-3">
          <Skeleton className="h-3 w-16" />
          <Skeleton className="h-3 w-20" />
          <Skeleton className="h-3 w-28" />
          <Skeleton className="h-3 w-24" />
        </div>

        {/* Title */}
        <Skeleton className="h-8 w-2/3" />

        {/* Body paragraphs */}
        <div className="space-y-3 mt-6">
          {[100, 90, 95, 80, 85, 100, 70, 88].map((w, i) => (
            <Skeleton key={i} className={`h-3.5`} style={{ width: `${w}%` }} />
          ))}
        </div>

        {/* Section heading */}
        <Skeleton className="h-5 w-40 mt-6" />

        <div className="space-y-3">
          {[95, 88, 92, 75, 80].map((w, i) => (
            <Skeleton key={i} className="h-3.5" style={{ width: `${w}%` }} />
          ))}
        </div>

        <Skeleton className="h-5 w-52 mt-6" />

        <div className="space-y-3">
          {[90, 85, 100, 70].map((w, i) => (
            <Skeleton key={i} className="h-3.5" style={{ width: `${w}%` }} />
          ))}
        </div>
      </div>

      {/* Right sidebar */}
      <div className="w-80 shrink-0 border-l border-white/5 glass p-5 space-y-5">
        {/* ToC skeleton */}
        <div className="space-y-2 pb-5 border-b border-white/5">
          <Skeleton className="h-3 w-20 mb-3" />
          {[60, 80, 70, 65, 75].map((w, i) => (
            <Skeleton key={i} className="h-3" style={{ width: `${w}%` }} />
          ))}
        </div>

        {/* Score breakdown skeleton */}
        <div className="space-y-3 pb-5 border-b border-white/5">
          <Skeleton className="h-3 w-24 mb-3" />
          {[85, 90, 75, 80].map((w, i) => (
            <div key={i} className="space-y-1.5">
              <div className="flex justify-between">
                <Skeleton className="h-2.5 w-28" />
                <Skeleton className="h-2.5 w-8" />
              </div>
              <Skeleton className="h-1.5 rounded-full" style={{ width: `${w}%` }} />
            </div>
          ))}
        </div>

        {/* Source cards skeleton */}
        <div className="space-y-3">
          <Skeleton className="h-3 w-20 mb-3" />
          {[1, 2, 3].map((i) => (
            <div key={i} className="rounded-xl border border-white/5 p-3 space-y-2">
              <div className="flex gap-2">
                <Skeleton className="h-5 w-5 rounded-full shrink-0" />
                <div className="flex-1 space-y-1.5">
                  <Skeleton className="h-3 w-full" />
                  <Skeleton className="h-2.5 w-24" />
                </div>
              </div>
              <Skeleton className="h-2.5 w-full" />
              <Skeleton className="h-2.5 w-3/4" />
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
