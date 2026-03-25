/** Types for live research jobs and WebSocket streaming. */

export type AgentType = 'planner' | 'researcher' | 'synthesizer' | 'reporter' | 'system'

export type JobStatus =
  | 'idle'
  | 'queued'
  | 'streaming'
  | 'reconnecting'
  | 'complete'
  | 'error'
  | 'failed'

export interface AgentMessage {
  id: string
  agent: AgentType
  message: string
  timestamp: string
}

// WebSocket event discriminated union
export type StreamEvent =
  | { type: 'agent_message'; id: string; agent: AgentType; message: string; timestamp: string }
  | { type: 'progress';      stage: string; progress: number }
  | { type: 'complete';      progress: 1;   report_id: string }
  | { type: 'error';         message: string }
