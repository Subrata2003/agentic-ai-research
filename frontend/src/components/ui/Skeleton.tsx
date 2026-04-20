import { cn } from '@/lib/utils'

interface SkeletonProps {
  className?: string
}

/** Shimmer skeleton block — compose to build any loading shape. */
export function Skeleton({ className }: SkeletonProps) {
  return (
    <div
      className={cn(
        'relative overflow-hidden rounded-md bg-white/5',
        'before:absolute before:inset-0',
        'before:bg-gradient-to-r before:from-transparent before:via-white/8 before:to-transparent',
        'before:animate-[shimmer_1.5s_infinite]',
        className,
      )}
    />
  )
}
