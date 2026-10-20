import React, { useEffect, useState } from 'react'
import {
  TrendingUp,
  TrendingDown,
  Minus,
  AlertTriangle,
  HardDrive,
  Cpu,
  Layers,
  RefreshCw,
} from 'lucide-react'
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts'
import { PredictionMetric } from '../types'
import { api } from '../api'

export const PredictiveAnalyticsPage: React.FC = () => {
  const [predictions, setPredictions] = useState<Record<string, PredictionMetric> | null>(null)
  const [loading, setLoading] = useState(false)

  const loadPredictions = async () => {
    setLoading(true)
    try {
      const data = await api.getPredictions(24)
      setPredictions(data)
    } catch (err) {
      console.error('Failed to load predictions:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadPredictions()
  }, [])

  const getTrendIcon = (trend: string) => {
    if (trend === 'RISING') return <TrendingUp size={16} className="text-rose-400" />
    if (trend === 'FALLING') return <TrendingDown size={16} className="text-emerald-400" />
    return <Minus size={16} className="text-slate-400" />
  }

  const formatChartData = (metric?: PredictionMetric) => {
    if (!metric) return []
    return metric.forecast.map((val, idx) => ({
      step: `+${idx + 1}`,
      predicted: val,
    }))
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <TrendingUp size={18} className="text-cyan-400" />
            <span>Lightweight Predictive Analytics & Forecasting</span>
          </h2>
          <p className="text-xs text-slate-400">
            Real-time moving average, Exponentially Weighted Moving Average (EWMA), and Ordinary Least Squares linear regression forecasting.
          </p>
        </div>
        <button
          onClick={loadPredictions}
          className="p-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-400 hover:text-white transition"
        >
          <RefreshCw size={15} className={loading ? 'animate-spin text-cyan-400' : ''} />
        </button>
      </div>

      {/* Disk Capacity & Exhaustion Projection Card */}
      {predictions?.disk && (
        <div className="p-5 rounded-2xl bg-gradient-to-r from-slate-900 to-amber-950/20 border border-amber-900/40 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-amber-500/20 text-amber-400 border border-amber-500/30 flex items-center justify-center flex-shrink-0">
              <HardDrive size={20} />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">Storage Exhaustion Horizon</h3>
              <p className="text-xs text-slate-400">
                Calculated from historical slope over the last 24 hours of disk usage samples.
              </p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold font-mono text-amber-400">
              {predictions.disk.days_until_full
                ? `~${predictions.disk.days_until_full} Days`
                : 'Indefinite (Stable)'}
            </div>
            <div className="text-[11px] text-slate-400">
              Growth: {predictions.disk.growth_per_day?.toFixed(3) || '0.000'}%/day
            </div>
          </div>
        </div>
      )}

      {/* Prediction Cards Grid for CPU, RAM, Disk */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {(['cpu', 'memory', 'disk'] as const).map((resource) => {
          const data = predictions?.[resource]
          const title = resource === 'cpu' ? 'CPU' : resource === 'memory' ? 'Memory (RAM)' : 'Disk'
          const Icon = resource === 'cpu' ? Cpu : resource === 'memory' ? Layers : HardDrive
          const strokeColor =
            resource === 'cpu' ? '#38bdf8' : resource === 'memory' ? '#818cf8' : '#fbbf24'

          return (
            <div
              key={resource}
              className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2 text-sm font-bold text-white">
                    <Icon size={16} className="text-slate-400" />
                    <span>{title}</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-xs font-semibold px-2 py-0.5 rounded bg-slate-950 border border-slate-800">
                    {getTrendIcon(data?.trend || '')}
                    <span className="text-slate-200">{data?.trend || 'STABLE'}</span>
                  </div>
                </div>

                {/* Metrics Table */}
                <div className="grid grid-cols-2 gap-2 text-xs font-mono my-3">
                  <div className="p-2 rounded-lg bg-slate-950 border border-slate-800">
                    <span className="text-[10px] text-slate-500 block">Current</span>
                    <span className="text-sm font-bold text-white">{data?.current.toFixed(1) || 0}%</span>
                  </div>
                  <div className="p-2 rounded-lg bg-slate-950 border border-slate-800">
                    <span className="text-[10px] text-slate-500 block">MA (10-sample)</span>
                    <span className="text-sm font-bold text-slate-200">{data?.moving_avg.toFixed(1) || 0}%</span>
                  </div>
                  <div className="p-2 rounded-lg bg-slate-950 border border-slate-800">
                    <span className="text-[10px] text-slate-500 block">EWMA (α=0.3)</span>
                    <span className="text-sm font-bold text-slate-200">{data?.ewma.toFixed(1) || 0}%</span>
                  </div>
                  <div className="p-2 rounded-lg bg-slate-950 border border-slate-800">
                    <span className="text-[10px] text-slate-500 block">Horizon (+10 steps)</span>
                    <span className="text-sm font-bold text-cyan-400">{data?.horizon.toFixed(1) || 0}%</span>
                  </div>
                </div>
              </div>

              {/* Forecast Curve Chart */}
              <div className="h-40 w-full pt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={formatChartData(data)}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="step" stroke="#475569" tick={{ fontSize: 10 }} />
                    <YAxis domain={[0, 100]} stroke="#475569" tick={{ fontSize: 10 }} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '12px' }}
                    />
                    <Line
                      type="monotone"
                      dataKey="predicted"
                      stroke={strokeColor}
                      strokeWidth={2}
                      dot={{ r: 3 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
