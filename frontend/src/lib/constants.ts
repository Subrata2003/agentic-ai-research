export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export const WS_BASE_URL =
  import.meta.env.VITE_WS_BASE_URL ?? 'ws://localhost:8000'

export const DEPTH_OPTIONS = [
  {
    value: 'shallow',
    label: 'Shallow',
    description: '5 sources · ~30 sec',
    hint: 'Good for quick overviews',
  },
  {
    value: 'medium',
    label: 'Medium',
    description: '10 sources · ~60 sec',
    hint: 'Balanced depth and speed',
  },
  {
    value: 'deep',
    label: 'Deep',
    description: '20 sources · ~2 min',
    hint: 'Comprehensive multi-angle analysis',
  },
] as const

export const EXAMPLE_TOPICS = [
  'Impact of AI on healthcare',
  'Climate change solutions 2024',
  'Quantum computing breakthroughs',
  'Future of remote work',
  'Gene editing ethics',
  'Central bank digital currencies',
]

export const AGENT_STAGES = [
  { key: 'planning',    label: 'Planning',     pct: 0.05 },
  { key: 'researching', label: 'Researching',  pct: 0.15 },
  { key: 'synthesizing',label: 'Synthesizing', pct: 0.55 },
  { key: 'fact_checking',label: 'Fact Checking',pct: 0.70 },
  { key: 'critiquing',  label: 'Critiquing',   pct: 0.80 },
  { key: 'scoring',     label: 'Scoring',      pct: 0.88 },
  { key: 'generating',  label: 'Generating',   pct: 0.92 },
  { key: 'persisting',  label: 'Saving',       pct: 0.96 },
  { key: 'done',        label: 'Done',         pct: 1.00 },
] as const
