import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'
import type { AgentMessage, JobStatus } from '@/types/research'

interface ResearchState {
  jobId: string | null
  status: JobStatus
  stage: string
  progress: number
  messages: AgentMessage[]
  completedReportId: string | null

  // Actions
  startJob: (jobId: string) => void
  setStatus: (status: JobStatus) => void
  setStage: (stage: string) => void
  setProgress: (progress: number) => void
  appendMessage: (msg: AgentMessage) => void
  setCompleted: (reportId: string) => void
  reset: () => void
}

const initialState = {
  jobId: null,
  status: 'idle' as JobStatus,
  stage: '',
  progress: 0,
  messages: [],
  completedReportId: null,
}

export const useResearchStore = create<ResearchState>()(
  immer((set) => ({
    ...initialState,

    startJob: (jobId) =>
      set((s) => {
        s.jobId = jobId
        s.status = 'queued'
        s.stage = 'planning'
        s.progress = 0
        s.messages = []
        s.completedReportId = null
      }),

    setStatus: (status) =>
      set((s) => { s.status = status }),

    setStage: (stage) =>
      set((s) => { s.stage = stage }),

    setProgress: (progress) =>
      set((s) => { s.progress = progress }),

    appendMessage: (msg) =>
      set((s) => { s.messages.push(msg) }),

    setCompleted: (reportId) =>
      set((s) => {
        s.completedReportId = reportId
        s.status = 'complete'
        s.progress = 1
      }),

    reset: () => set(() => ({ ...initialState })),
  })),
)
