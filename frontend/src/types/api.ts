/** Typed API request/response shapes that mirror the FastAPI schemas. */

export type ResearchDepth = 'shallow' | 'medium' | 'deep'

// ---------------------------------------------------------------------------
// Requests
// ---------------------------------------------------------------------------

export interface StartResearchRequest {
  topic: string
  depth?: ResearchDepth
  save_report?: boolean
}

// ---------------------------------------------------------------------------
// Responses
// ---------------------------------------------------------------------------

export interface StartResearchResponse {
  job_id: string
  status: 'queued' | 'running' | 'complete' | 'error'
}

export interface ReportListItem {
  id: string
  topic: string
  depth: ResearchDepth
  created_at: string
  num_sources: number
  quality_score: number
  report_path: string | null
  pdf_path: string | null
}

export interface PaginatedReports {
  items: ReportListItem[]
  total: number
  page: number
  limit: number
  has_next: boolean
}

export interface QualityScore {
  source_coverage:    number
  citation_accuracy:  number
  synthesis_coherence: number
  factual_density:    number
  overall:            number
}

export interface SourceItem {
  source_index: number
  url: string
  title: string
  exact_quote: string
  relevance_score: number
}

export interface FactCheck {
  claim: string
  verdict: 'SUPPORTED' | 'CONTRADICTED' | 'UNVERIFIABLE'
  confidence: number
  evidence: string | null
}

export interface ReportDetail {
  id: string
  topic: string
  depth: ResearchDepth
  created_at: string
  num_sources: number
  report_markdown: string
  quality_score: QualityScore | null
  sources: SourceItem[]
  fact_checks: FactCheck[]
}

export interface PdfExportResponse {
  job_id: string
  pdf_url: string | null
  status: 'processing' | 'ready' | 'error'
}

export interface SimilarReport {
  id: string
  topic: string
  created_at: string
  quality_score: number
  distance: number
}

export interface ApiStats {
  total_reports: number
  avg_quality_score: number
  avg_sources: number
  fact_check_support_rate: number
  reports_this_week: number
}
