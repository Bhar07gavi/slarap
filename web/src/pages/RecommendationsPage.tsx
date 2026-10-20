import React, { useEffect, useState } from 'react'
import { Lightbulb, AlertTriangle, CheckCircle, Info, RefreshCw, ArrowRight } from 'lucide-react'
import { RecommendationItem } from '../types'
import { api } from '../api'

export const RecommendationsPage: React.FC = () => {
  const [recommendations, setRecommendations] = useState<RecommendationItem[]>([])
  const [loading, setLoading] = useState(false)

  const loadRecommendations = async () => {
    setLoading(true)
    try {
      const data = await api.getRecommendations()
      setRecommendations(data)
    } catch (err) {
      console.error('Failed to load recommendations:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadRecommendations()
  }, [])

  const getPriorityBadge = (priority: string) => {
    switch (priority.toUpperCase()) {
      case 'HIGH':
        return 'bg-rose-950/80 text-rose-300 border-rose-800'
      case 'MEDIUM':
        return 'bg-amber-950/80 text-amber-300 border-amber-800'
      case 'LOW':
        return 'bg-blue-950/80 text-blue-300 border-blue-800'
      default:
        return 'bg-emerald-950/80 text-emerald-300 border-emerald-800'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Lightbulb size={18} className="text-amber-400" />
            <span>Intelligent System Recommendations</span>
          </h2>
          <p className="text-xs text-slate-400">
            Rule-based expert advisor analyzing process resource hogs, zombie tasks, memory pressure, and storage trends.
          </p>
        </div>
        <button
          onClick={loadRecommendations}
          className="p-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-400 hover:text-white transition"
        >
          <RefreshCw size={15} className={loading ? 'animate-spin text-amber-400' : ''} />
        </button>
      </div>

      {/* Recommendations Feed */}
      <div className="space-y-3">
        {recommendations.length === 0 ? (
          <div className="p-12 text-center rounded-2xl bg-slate-900 border border-slate-800 text-slate-500 text-xs flex flex-col items-center">
            <CheckCircle size={32} className="text-emerald-500 mb-2" />
            <span>No critical optimization recommendations right now. System is performing optimally.</span>
          </div>
        ) : (
          recommendations.map((rec, i) => (
            <div
              key={i}
              className="p-5 rounded-2xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition space-y-2"
            >
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <span className="text-amber-400">•</span>
                  <span>{rec.title}</span>
                </h3>
                <span
                  className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase tracking-wider ${getPriorityBadge(
                    rec.priority
                  )}`}
                >
                  {rec.priority} Priority
                </span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed font-mono bg-slate-950 p-3 rounded-xl border border-slate-800/80">
                {rec.detail}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
