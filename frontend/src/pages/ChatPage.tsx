import { useState, useEffect, useRef } from 'react'
import { useParams } from 'react-router-dom'
import { useWebSocket, WebSocketMessage } from '../hooks/useWebSocket'
import { essayApi, universityApi } from '../services/api'
import toast from 'react-hot-toast'
import clsx from 'clsx'
import AgentProgress from '../components/chat/AgentProgress'

interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  agent?: string
  timestamp: Date
}

interface University {
  code: string
  name: string
}

const PROMPTS = [
  { id: 'growth', text: 'Discuss an accomplishment that sparked personal growth' },
  { id: 'challenge', text: 'Recount a time when you faced a challenge or setback' },
  { id: 'belief', text: 'Reflect on a time you questioned a belief or idea' },
  { id: 'passion', text: 'Describe a topic that makes you lose track of time' },
]

export default function ChatPage() {
  const { id: existingId } = useParams()
  const [generationId, setGenerationId] = useState<string | null>(existingId || null)
  const [messages, setMessages] = useState<Message[]>([])
  const [isGenerating, setIsGenerating] = useState(false)
  const [currentAgent, setCurrentAgent] = useState<string | null>(null)
  const [progress, setProgress] = useState(0)
  const [finalEssay, setFinalEssay] = useState<string | null>(null)
  const [critique, setCritique] = useState<string | null>(null)

  // Form state
  const [prompt, setPrompt] = useState('')
  const [university, setUniversity] = useState('MIT')
  const [universities, setUniversities] = useState<University[]>([])

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { lastMessage, sendMessage, connectionStatus } = useWebSocket(generationId)

  // Load universities on mount
  useEffect(() => {
    universityApi.list().then((data) => {
      setUniversities(data.results || data)
    }).catch(() => {
      // Fallback universities
      setUniversities([
        { code: 'MIT', name: 'MIT' },
        { code: 'Harvard', name: 'Harvard' },
        { code: 'Stanford', name: 'Stanford' },
        { code: 'Yale', name: 'Yale' },
        { code: 'Princeton', name: 'Princeton' },
      ])
    })
  }, [])

  // Handle WebSocket messages
  useEffect(() => {
    if (!lastMessage) return

    const data = lastMessage as WebSocketMessage

    switch (data.type) {
      case 'connected':
        if (data.status && data.status !== 'pending' && data.status !== 'completed') {
          setIsGenerating(true)
          setCurrentAgent(data.status)
          setProgress(data.progress || 0)
        }
        break

      case 'agent_start':
        setCurrentAgent(data.agent || null)
        setProgress(data.progress || 0)
        setIsGenerating(true)
        addMessage({
          role: 'system',
          content: data.message || `${data.agent} agent started...`,
          agent: data.agent,
        })
        break

      case 'agent_progress':
        setProgress(data.progress || 0)
        // For streaming, append to last message if same agent
        if (data.content) {
          setMessages((prev) => {
            const last = prev[prev.length - 1]
            if (last?.agent === data.agent && last?.role === 'assistant') {
              return [
                ...prev.slice(0, -1),
                { ...last, content: last.content + data.content },
              ]
            }
            return prev
          })
        }
        break

      case 'agent_complete':
        setProgress(data.progress || 0)
        if (data.content && data.agent === 'draft') {
          addMessage({
            role: 'assistant',
            content: data.content,
            agent: data.agent,
          })
        }
        break

      case 'generation_complete':
        setIsGenerating(false)
        setCurrentAgent(null)
        setProgress(100)
        setFinalEssay(data.final_essay || null)
        setCritique(data.critique || null)
        addMessage({
          role: 'system',
          content: `Essay complete! ${data.word_count} words.`,
        })
        break

      case 'error':
        setIsGenerating(false)
        toast.error(data.message || 'Generation failed')
        addMessage({
          role: 'system',
          content: `Error: ${data.message}`,
        })
        break

      case 'cancelled':
        setIsGenerating(false)
        addMessage({
          role: 'system',
          content: 'Generation cancelled.',
        })
        break
    }
  }, [lastMessage])

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const addMessage = (msg: Omit<Message, 'id' | 'timestamp'>) => {
    setMessages((prev) => [
      ...prev,
      {
        ...msg,
        id: Date.now().toString(),
        timestamp: new Date(),
      },
    ])
  }

  const handleStartGeneration = async () => {
    if (!prompt.trim()) {
      toast.error('Please enter an essay prompt')
      return
    }

    try {
      // Add user message
      addMessage({
        role: 'user',
        content: `Generate an essay for ${university}:\n\n"${prompt}"`,
      })

      // Start generation
      const response = await essayApi.create({
        prompt: prompt.trim(),
        target_university_code: university,
        essay_type: 'common_app',
        word_count_target: 650,
      })

      setGenerationId(response.id)
      setIsGenerating(true)
      setPrompt('')
    } catch (error) {
      toast.error('Failed to start essay generation')
      console.error(error)
    }
  }

  const handleCancel = () => {
    if (generationId) {
      sendMessage({ type: 'cancel' })
      essayApi.cancel(generationId).catch(console.error)
    }
  }

  const handleNewEssay = () => {
    setGenerationId(null)
    setMessages([])
    setFinalEssay(null)
    setCritique(null)
    setProgress(0)
    setCurrentAgent(null)
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <header className="bg-white border-b px-6 py-4 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">
            {generationId ? 'Essay Generation' : 'New Essay'}
          </h2>
          <p className="text-sm text-gray-500">
            {connectionStatus === 'connected' ? '🟢 Connected' :
             connectionStatus === 'connecting' ? '🟡 Connecting...' :
             connectionStatus === 'error' ? '🔴 Error' : '⚪ Ready'}
          </p>
        </div>
        {generationId && (
          <button
            onClick={handleNewEssay}
            className="px-4 py-2 text-sm bg-gray-100 rounded-lg hover:bg-gray-200"
          >
            + New Essay
          </button>
        )}
      </header>

      {/* Agent Progress */}
      {isGenerating && (
        <AgentProgress
          currentAgent={currentAgent}
          progress={progress}
          onCancel={handleCancel}
        />
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 && !generationId && (
          <div className="text-center py-12">
            <h3 className="text-2xl font-bold text-gray-900 mb-2">
              Welcome to EssayMentor AI
            </h3>
            <p className="text-gray-600 mb-8">
              Generate college essays using our 7-agent RAG system
            </p>

            {/* Quick prompts */}
            <div className="grid grid-cols-2 gap-4 max-w-2xl mx-auto">
              {PROMPTS.map((p) => (
                <button
                  key={p.id}
                  onClick={() => setPrompt(p.text)}
                  className="p-4 text-left bg-white border rounded-lg hover:border-primary-500 hover:shadow transition-all"
                >
                  <p className="text-sm text-gray-700">{p.text}</p>
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={clsx(
              'message-bubble',
              msg.role === 'user' && 'message-user',
              msg.role === 'assistant' && 'message-assistant',
              msg.role === 'system' && 'message-system'
            )}
          >
            {msg.agent && (
              <span className="text-xs font-medium text-gray-500 mb-1 block">
                {msg.agent.charAt(0).toUpperCase() + msg.agent.slice(1)} Agent
              </span>
            )}
            <p className="whitespace-pre-wrap">{msg.content}</p>
          </div>
        ))}

        {/* Final Essay Display */}
        {finalEssay && (
          <div className="bg-white border rounded-lg p-6 mt-4">
            <h3 className="font-semibold text-lg mb-4">Final Essay</h3>
            <div className="prose max-w-none">
              <p className="whitespace-pre-wrap">{finalEssay}</p>
            </div>
            <div className="mt-4 flex gap-2">
              <button
                onClick={() => navigator.clipboard.writeText(finalEssay)}
                className="px-4 py-2 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700"
              >
                Copy to Clipboard
              </button>
            </div>
          </div>
        )}

        {/* Critique Display */}
        {critique && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mt-4">
            <h3 className="font-semibold text-lg mb-4">Critique</h3>
            <p className="whitespace-pre-wrap text-sm">{critique}</p>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      {!isGenerating && !finalEssay && (
        <div className="bg-white border-t p-4">
          <div className="max-w-4xl mx-auto space-y-4">
            {/* University selector */}
            <div className="flex gap-4">
              <select
                value={university}
                onChange={(e) => setUniversity(e.target.value)}
                className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
              >
                {universities.map((u) => (
                  <option key={u.code} value={u.code}>
                    {u.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Prompt input */}
            <div className="flex gap-4">
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Enter your essay prompt or question..."
                rows={3}
                className="flex-1 px-4 py-3 border rounded-lg resize-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && e.metaKey) {
                    handleStartGeneration()
                  }
                }}
              />
              <button
                onClick={handleStartGeneration}
                disabled={!prompt.trim()}
                className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed self-end"
              >
                Generate
              </button>
            </div>
            <p className="text-xs text-gray-500">
              Press ⌘+Enter to generate
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
