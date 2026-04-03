import { useEffect, useRef, useCallback } from 'react'
import { useResearchStore } from '@/store/researchStore'
import { WS_BASE_URL } from '@/lib/constants'
import type { StreamEvent } from '@/types/research'

const MAX_RECONNECT_ATTEMPTS = 5
const RECONNECT_BASE_DELAY_MS = 1000

/**
 * WebSocket hook that streams live research progress into the Zustand store.
 *
 * Connects to:  ws://localhost:8000/api/v1/research/{jobId}/stream
 *
 * Handles:
 *   agent_message → appendMessage (feeds the terminal feed)
 *   progress      → setProgress + setStage
 *   complete      → setCompleted (triggers auto-navigate in ResearchPage)
 *   error         → setStatus('error')
 *   ping          → ignored (server keepalive)
 *
 * Reconnects with exponential backoff on unexpected close (max 5 attempts).
 * Cleans up properly on unmount — no reconnect after component is gone.
 */
export function useResearchStream(jobId: string | null) {
  const wsRef               = useRef<WebSocket | null>(null)
  const reconnectAttempts   = useRef(0)
  const reconnectTimerRef   = useRef<ReturnType<typeof setTimeout> | null>(null)
  const isMountedRef        = useRef(true)

  const appendMessage = useResearchStore((s) => s.appendMessage)
  const setProgress   = useResearchStore((s) => s.setProgress)
  const setStage      = useResearchStore((s) => s.setStage)
  const setStatus     = useResearchStore((s) => s.setStatus)
  const setCompleted  = useResearchStore((s) => s.setCompleted)

  const connect = useCallback(() => {
    if (!jobId || !isMountedRef.current) return
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    const url = `${WS_BASE_URL}/api/v1/research/${jobId}/stream`
    const ws  = new WebSocket(url)
    wsRef.current = ws

    ws.onopen = () => {
      reconnectAttempts.current = 0
      setStatus('streaming')
    }

    ws.onmessage = (event: MessageEvent<string>) => {
      try {
        const data = JSON.parse(event.data) as StreamEvent | { type: 'ping' }

        if (data.type === 'ping') return

        switch (data.type) {
          case 'agent_message':
            appendMessage({
              id:        data.id ?? crypto.randomUUID(),
              agent:     data.agent,
              message:   data.message,
              timestamp: data.timestamp,
            })
            break

          case 'progress':
            setProgress(data.progress)
            setStage(data.stage)
            break

          case 'complete':
            setCompleted(data.report_id)
            ws.close(1000, 'Research complete')
            break

          case 'error':
            setStatus('error')
            appendMessage({
              id:        crypto.randomUUID(),
              agent:     'system',
              message:   `Error: ${data.message}`,
              timestamp: new Date().toISOString(),
            })
            ws.close(1011, 'Server error')
            break
        }
      } catch {
        // Malformed JSON — ignore silently
      }
    }

    ws.onerror = () => {
      setStatus('error')
    }

    ws.onclose = (event: CloseEvent) => {
      wsRef.current = null

      // Normal close codes — don't reconnect
      if (event.code === 1000 || event.code === 1001 || !isMountedRef.current) return

      if (reconnectAttempts.current < MAX_RECONNECT_ATTEMPTS) {
        const delay = RECONNECT_BASE_DELAY_MS * Math.pow(2, reconnectAttempts.current)
        reconnectAttempts.current += 1
        setStatus('reconnecting')
        reconnectTimerRef.current = setTimeout(connect, delay)
      } else {
        setStatus('failed')
      }
    }
  }, [jobId, appendMessage, setProgress, setStage, setStatus, setCompleted])

  useEffect(() => {
    isMountedRef.current = true
    if (jobId) connect()

    return () => {
      isMountedRef.current = false
      if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current)
      if (wsRef.current) {
        wsRef.current.onclose = null   // prevent reconnect on intentional unmount
        wsRef.current.close(1000, 'Component unmounted')
      }
    }
  }, [jobId, connect])

  const disconnect = useCallback(() => {
    if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current)
    wsRef.current?.close(1000, 'Manual disconnect')
  }, [])

  return { disconnect }
}
