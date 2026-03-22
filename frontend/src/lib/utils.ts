import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

/** Merge Tailwind classes without conflicts. */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/** Format an ISO timestamp to a human-readable string. */
export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/** Return a short relative time string ("2 hours ago"). */
export function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  const minutes = Math.floor(diff / 60_000)
  if (minutes < 1)  return 'just now'
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24)   return `${hours}h ago`
  return `${Math.floor(hours / 24)}d ago`
}

/** Map a quality score (0–1) to a Tailwind colour class. */
export function scoreColor(score: number): string {
  if (score >= 0.8) return 'text-emerald-400'
  if (score >= 0.6) return 'text-amber-400'
  return 'text-red-400'
}

/** Map a quality score to a badge variant string for styling. */
export function scoreBadgeClass(score: number): string {
  if (score >= 0.8)
    return 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
  if (score >= 0.6)
    return 'bg-amber-500/15 text-amber-400 border-amber-500/30'
  return 'bg-red-500/15 text-red-400 border-red-500/30'
}

/** Truncate a string to `maxLen` characters with an ellipsis. */
export function truncate(str: string, maxLen = 80): string {
  return str.length <= maxLen ? str : str.slice(0, maxLen - 1) + '…'
}

/** Extract the domain from a URL for display. */
export function extractDomain(url: string): string {
  try {
    return new URL(url).hostname.replace('www.', '')
  } catch {
    return url
  }
}

/** Format a float (0–1) as a percentage string. */
export function pct(value: number, decimals = 0): string {
  return `${(value * 100).toFixed(decimals)}%`
}
