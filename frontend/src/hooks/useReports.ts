import { useQuery, useInfiniteQuery } from '@tanstack/react-query'
import { api } from '@/services/api'

// ---------------------------------------------------------------------------
// Query key factory — keeps cache keys consistent across the app
// ---------------------------------------------------------------------------

export const reportKeys = {
  all:    ['reports'] as const,
  lists:  () => [...reportKeys.all, 'list'] as const,
  list:   (params: object) => [...reportKeys.lists(), params] as const,
  detail: (id: string) => [...reportKeys.all, 'detail', id] as const,
  analytics: ['analytics'] as const,
}

// ---------------------------------------------------------------------------
// Paginated report list (History page)
// ---------------------------------------------------------------------------

export function useReports(params?: {
  page?: number
  limit?: number
  search?: string
  sort?: 'newest' | 'oldest' | 'quality_desc' | 'quality_asc'
}) {
  return useQuery({
    queryKey: reportKeys.list(params ?? {}),
    queryFn:  () => api.getReports(params),
    placeholderData: (prev) => prev,  // keep previous data while fetching
  })
}

// ---------------------------------------------------------------------------
// Infinite scroll variant (also for History page grid)
// ---------------------------------------------------------------------------

export function useInfiniteReports(params?: {
  limit?: number
  search?: string
  sort?: 'newest' | 'oldest' | 'quality_desc' | 'quality_asc'
}) {
  return useInfiniteQuery({
    queryKey: reportKeys.list({ infinite: true, ...params }),
    queryFn: ({ pageParam }) =>
      api.getReports({ ...params, page: pageParam as number }),
    initialPageParam: 1,
    getNextPageParam: (lastPage) =>
      lastPage.page < lastPage.pages ? lastPage.page + 1 : undefined,
  })
}

// ---------------------------------------------------------------------------
// Single report detail (Report viewer page)
// ---------------------------------------------------------------------------

export function useReport(id: string | undefined) {
  return useQuery({
    queryKey: reportKeys.detail(id ?? ''),
    queryFn:  () => api.getReport(id!),
    enabled:  Boolean(id),
    staleTime: 1000 * 60 * 10,  // reports don't change — cache 10 min
  })
}

// ---------------------------------------------------------------------------
// Analytics dashboard data
// ---------------------------------------------------------------------------

export function useAnalytics() {
  return useQuery({
    queryKey: reportKeys.analytics,
    queryFn:  api.getAnalytics,
    staleTime: 1000 * 60 * 2,  // refresh every 2 min
  })
}
