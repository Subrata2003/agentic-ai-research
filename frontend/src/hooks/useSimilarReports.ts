import { useQuery } from '@tanstack/react-query'
import { api } from '@/services/api'

/**
 * Fetch semantically similar past reports for a given topic.
 * Used in the Research page sidebar to show related prior research.
 *
 * Only fires when `topic` has ≥ 3 characters to avoid spamming
 * the API on every keystroke.
 */
export function useSimilarReports(topic: string, n = 5) {
  return useQuery({
    queryKey: ['similar', topic, n],
    queryFn:  () => api.getSimilarReports(topic, n),
    enabled:  topic.trim().length >= 3,
    staleTime: 1000 * 60 * 5,
    placeholderData: [],
  })
}
