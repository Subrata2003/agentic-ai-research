/** Typed API request/response shapes — mirrors FastAPI schemas exactly. */

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
// Research job
// ---------------------------------------------------------------------------

export interface StartResearchResponse {
  job_id: string
  status: 'queued' | 'running' | 'complete' | 'error'
  topic: string
  depth?: ResearchDepth | null
}

// ---------------------------------------------------------------------------
// Report list (history page)
// ---------------------------------------------------------------------------

export interface ReportListItem {
  id: string
  topic: string
  depth: string
  num_sources: number
  overall_score: number | null       // 0–1 from EvaluationScore
  overall_confidence: number | null  // from SynthesizerOutput
  critic_quality: number | null
  created_at: string                 // ISO-8601
  report_path: string | null
}

export interface PaginatedReports {
  items: ReportListItem[]
  total: number
  page: number
  pages: number                      // total page count
}

// ---------------------------------------------------------------------------
// Quality score (EvaluationScore)
// ---------------------------------------------------------------------------

export interface QualityScore {
  overall: number
  source_coverage: number
  citation_accuracy: number
  synthesis_coherence: number
  factual_density: number
}

// ---------------------------------------------------------------------------
// Fact-check summary
// ---------------------------------------------------------------------------

export interface FactCheckSummary {
  supported: number
  unverifiable: number
  contradicted: number
  total: number
}

// ---------------------------------------------------------------------------
// Source quote
// ---------------------------------------------------------------------------

export interface SourceItem {
  source_index: number
  title: string
  url: string
  exact_quote: string
  relevance_score: number
}

// ---------------------------------------------------------------------------
// Full report detail (report viewer page)
// ---------------------------------------------------------------------------

export interface ReportDetail {
  id: string
  topic: string
  depth: string
  report_markdown: string
  num_sources: number
  overall_score: number | null
  overall_confidence: number | null
  critic_quality: number | null
  created_at: string
  report_path: string | null
  pdf_path: string | null
  quality_score: QualityScore | null
  fact_check_summary: FactCheckSummary | null
  sources: SourceItem[]
  plan_json: string | null
  synthesis_json: string | null
}

// ---------------------------------------------------------------------------
// PDF export
// ---------------------------------------------------------------------------

export interface PdfExportResponse {
  report_id: string
  pdf_path: string
  status: 'ok' | 'error'
}

// ---------------------------------------------------------------------------
// Semantic similar reports
// ---------------------------------------------------------------------------

export interface SimilarReport {
  report_id: string
  topic: string
  depth: string
  score: string
  distance: number
  summary: string
}

// ---------------------------------------------------------------------------
// Analytics dashboard
// ---------------------------------------------------------------------------

export interface AnalyticsStats {
  total_reports: number
  avg_quality: number | null
  avg_sources: number | null
  avg_confidence: number | null
  total_sources_analysed: number | null
  fact_check_distribution: Record<string, number>
  depth_distribution: Record<string, number>
  recent_reports: Array<{
    id: string
    topic: string
    overall_score: number | null
    created_at: string
  }>
}
