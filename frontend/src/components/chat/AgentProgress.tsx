import clsx from 'clsx'

interface AgentProgressProps {
  currentAgent: string | null
  progress: number
  onCancel: () => void
}

const AGENTS = [
  { key: 'profile', name: 'Profile', icon: '👤', description: 'Analyzing student profile' },
  { key: 'rag', name: 'RAG', icon: '🔍', description: 'Retrieving similar essays' },
  { key: 'research', name: 'Research', icon: '📚', description: 'Researching prompt' },
  { key: 'brainstorm', name: 'Brainstorm', icon: '💡', description: 'Generating ideas' },
  { key: 'outline', name: 'Outline', icon: '📝', description: 'Creating structure' },
  { key: 'draft', name: 'Draft', icon: '✍️', description: 'Writing essay' },
  { key: 'critique', name: 'Critique', icon: '🎯', description: 'Reviewing essay' },
]

export default function AgentProgress({ currentAgent, progress, onCancel }: AgentProgressProps) {
  const currentIndex = AGENTS.findIndex((a) => a.key === currentAgent)
  const currentAgentInfo = AGENTS.find((a) => a.key === currentAgent)

  return (
    <div className="bg-white border-b px-6 py-4">
      {/* Progress bar */}
      <div className="h-2 bg-gray-200 rounded-full mb-4 overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-primary-500 to-primary-600 transition-all duration-500 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Current agent info */}
      {currentAgentInfo && (
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <span className="text-2xl">{currentAgentInfo.icon}</span>
            <div>
              <p className="font-medium">{currentAgentInfo.name} Agent</p>
              <p className="text-sm text-gray-500">{currentAgentInfo.description}</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-500">{progress}%</span>
            <button
              onClick={onCancel}
              className="px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Agent pipeline */}
      <div className="flex items-center justify-between">
        {AGENTS.map((agent, index) => {
          const isComplete = index < currentIndex
          const isCurrent = agent.key === currentAgent
          const isPending = index > currentIndex

          return (
            <div key={agent.key} className="flex items-center">
              {/* Agent badge */}
              <div
                className={clsx(
                  'flex items-center gap-2 px-3 py-1.5 rounded-full text-sm transition-all',
                  isCurrent && 'bg-primary-100 text-primary-800 animate-pulse',
                  isComplete && 'bg-green-100 text-green-800',
                  isPending && 'bg-gray-100 text-gray-400'
                )}
              >
                <span>{agent.icon}</span>
                <span className="hidden md:inline font-medium">{agent.name}</span>
                {isComplete && <span>✓</span>}
              </div>

              {/* Connector line */}
              {index < AGENTS.length - 1 && (
                <div
                  className={clsx(
                    'w-4 md:w-8 h-0.5 mx-1',
                    index < currentIndex ? 'bg-green-300' : 'bg-gray-200'
                  )}
                />
              )}
            </div>
          )
        })}
      </div>

      {/* Typing indicator */}
      {currentAgent && (
        <div className="flex items-center gap-2 mt-4 text-gray-500">
          <span className="text-sm">Processing</span>
          <span className="flex gap-1">
            <span className="w-1.5 h-1.5 bg-gray-400 rounded-full typing-dot" />
            <span className="w-1.5 h-1.5 bg-gray-400 rounded-full typing-dot" />
            <span className="w-1.5 h-1.5 bg-gray-400 rounded-full typing-dot" />
          </span>
        </div>
      )}
    </div>
  )
}
