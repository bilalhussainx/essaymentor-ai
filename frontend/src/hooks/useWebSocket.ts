import { useEffect, useRef, useState, useCallback } from 'react'
import { useAuthStore } from '../store/authStore'

export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error'

export interface WebSocketMessage {
  type: string
  agent?: string
  content?: string
  message?: string
  progress?: number
  final_essay?: string
  critique?: string
  word_count?: number
  status?: string
}

interface UseWebSocketReturn {
  sendMessage: (message: Record<string, unknown>) => void
  lastMessage: WebSocketMessage | null
  connectionStatus: ConnectionStatus
  messages: WebSocketMessage[]
}

export function useWebSocket(generationId: string | null): UseWebSocketReturn {
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const [messages, setMessages] = useState<WebSocketMessage[]>([])
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('disconnected')

  const wsRef = useRef<WebSocket | null>(null)
  const { accessToken } = useAuthStore()

  useEffect(() => {
    if (!generationId || !accessToken) {
      return
    }

    // Build WebSocket URL
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsHost = import.meta.env.VITE_WS_URL || `${wsProtocol}//${window.location.host}`
    const wsUrl = `${wsHost}/ws/essays/${generationId}/?token=${accessToken}`

    setConnectionStatus('connecting')
    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      setConnectionStatus('connected')
      console.log('WebSocket connected')
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as WebSocketMessage
        setLastMessage(data)
        setMessages((prev) => [...prev, data])
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e)
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      setConnectionStatus('error')
    }

    ws.onclose = () => {
      setConnectionStatus('disconnected')
      console.log('WebSocket disconnected')
    }

    wsRef.current = ws

    return () => {
      ws.close()
    }
  }, [generationId, accessToken])

  const sendMessage = useCallback((message: Record<string, unknown>) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message))
    }
  }, [])

  return { sendMessage, lastMessage, connectionStatus, messages }
}
