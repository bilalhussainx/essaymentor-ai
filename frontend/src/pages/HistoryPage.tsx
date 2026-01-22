import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { essayApi } from '../services/api'
import clsx from 'clsx'

interface EssayItem {
  id: string
  prompt: string
  target_university_code: string
  target_university_name: string
  essay_type: string
  status: string
  progress_percent: number
  word_count_actual: number | null
  created_at: string
}

const STATUS_COLORS: Record<string, string> = {
  completed: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
  cancelled: 'bg-gray-100 text-gray-800',
  pending: 'bg-yellow-100 text-yellow-800',
  profile: 'bg-blue-100 text-blue-800',
  rag: 'bg-blue-100 text-blue-800',
  research: 'bg-blue-100 text-blue-800',
  brainstorm: 'bg-blue-100 text-blue-800',
  outline: 'bg-blue-100 text-blue-800',
  draft: 'bg-blue-100 text-blue-800',
  critique: 'bg-blue-100 text-blue-800',
}

export default function HistoryPage() {
  const [essays, setEssays] = useState<EssayItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadEssays()
  }, [])

  const loadEssays = async () => {
    try {
      const data = await essayApi.list()
      setEssays(data.results || data)
    } catch (error) {
      console.error('Failed to load essays:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this essay?')) return

    try {
      await essayApi.delete(id)
      setEssays((prev) => prev.filter((e) => e.id !== id))
    } catch (error) {
      console.error('Failed to delete essay:', error)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full" />
      </div>
    )
  }

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-4xl mx-auto p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold">Essay History</h2>
            <p className="text-gray-600">{essays.length} essays generated</p>
          </div>
          <Link
            to="/"
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            + New Essay
          </Link>
        </div>

        {essays.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg">
            <p className="text-gray-500 mb-4">No essays generated yet</p>
            <Link
              to="/"
              className="text-primary-600 hover:underline"
            >
              Generate your first essay
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {essays.map((essay) => (
              <div
                key={essay.id}
                className="bg-white rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="font-semibold text-primary-600">
                        {essay.target_university_code || essay.target_university_name}
                      </span>
                      <span
                        className={clsx(
                          'px-2 py-0.5 rounded-full text-xs font-medium',
                          STATUS_COLORS[essay.status] || 'bg-gray-100 text-gray-800'
                        )}
                      >
                        {essay.status}
                        {essay.status !== 'completed' && essay.status !== 'failed' && essay.status !== 'cancelled' && (
                          <span className="ml-1">({essay.progress_percent}%)</span>
                        )}
                      </span>
                      <span className="text-xs text-gray-400">
                        {essay.essay_type}
                      </span>
                    </div>

                    <p className="text-gray-700 text-sm line-clamp-2 mb-2">
                      {essay.prompt}
                    </p>

                    <div className="flex items-center gap-4 text-xs text-gray-500">
                      <span>{formatDate(essay.created_at)}</span>
                      {essay.word_count_actual && (
                        <span>{essay.word_count_actual} words</span>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-2 ml-4">
                    {essay.status === 'completed' && (
                      <Link
                        to={`/essay/${essay.id}`}
                        className="px-3 py-1.5 text-sm bg-gray-100 rounded-lg hover:bg-gray-200"
                      >
                        View
                      </Link>
                    )}
                    <button
                      onClick={() => handleDelete(essay.id)}
                      className="px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 rounded-lg"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
