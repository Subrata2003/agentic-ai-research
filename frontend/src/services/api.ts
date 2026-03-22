import { API_BASE_URL } from '@/lib/constants'
import type {
  StartResearchRequest,
  StartResearchResponse,
  PaginatedReports,
  ReportDetail,
  PdfExportResponse,
  SimilarReport,
  ApiStats,
} from '@/types/api'

// ---------------------------------------------------------------------------
// Error type
// ---------------------------------------------------------------------------

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

// ---------------------------------------------------------------------------
// Core fetch wrapper
// ---------------------------------------------------------------------------

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  })

  if (!res.ok) {
    const body = await res.text().catch(() => res.statusText)
    throw new ApiError(res.status, body)
  }

  // 204 No Content
  if (res.status === 204) return undefined as T

  return res.json() as Promise<T>
}

// ---------------------------------------------------------------------------
// API methods
// ---------------------------------------------------------------------------

export const api = {
  /** Start a new research job. Returns a job_id for WebSocket streaming. */
  startResearch(payload: StartResearchRequest): Promise<StartResearchResponse> {
    return request('/api/v1/research', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },

  /** Paginated list of past reports with optional search + sort. */
  getReports(params?: {
    page?: number
    limit?: number
    search?: string
    sort?: 'newest' | 'oldest' | 'quality_desc' | 'quality_asc'
  }): Promise<PaginatedReports> {
    const qs = params
      ? '?' + new URLSearchParams(
          Object.entries(params)
            .filter(([, v]) => v !== undefined && v !== '')
            .map(([k, v]) => [k, String(v)]),
        ).toString()
      : ''
    return request(`/api/v1/reports${qs}`)
  },

  /** Fetch a single report's full detail. */
  getReport(id: string): Promise<ReportDetail> {
    return request(`/api/v1/reports/${id}`)
  },

  /** Trigger PDF export for a report. Returns a status + eventual pdf_url. */
  exportPdf(id: string): Promise<PdfExportResponse> {
    return request(`/api/v1/reports/${id}/pdf`, { method: 'POST' })
  },

  /** Semantic similarity search over past reports. */
  getSimilarReports(topic: string): Promise<SimilarReport[]> {
    return request(`/api/v1/similar?topic=${encodeURIComponent(topic)}`)
  },

  /** Aggregate analytics stats. */
  getStats(): Promise<ApiStats> {
    return request('/api/v1/stats')
  },
}
