import { useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/services/api'
import { reportKeys } from './useReports'

/**
 * Mutation hook for exporting a report as PDF.
 *
 * Usage:
 *   const { mutate: exportPdf, isPending, data } = usePdfExport()
 *   exportPdf(reportId)
 *
 * On success the report detail cache is invalidated so the
 * Report page re-fetches and shows the new pdf_path.
 */
export function usePdfExport() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (reportId: string) => api.exportPdf(reportId),

    onSuccess: (_data, reportId) => {
      // Invalidate this report's detail so the download button
      // reflects the newly generated pdf_path immediately
      void queryClient.invalidateQueries({
        queryKey: reportKeys.detail(reportId),
      })
    },
  })
}
