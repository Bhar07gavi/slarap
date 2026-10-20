import React, { useEffect, useState } from 'react'
import { Bell, AlertTriangle, ShieldAlert, CheckCircle, Sliders, RefreshCw } from 'lucide-react'
import { AlertItem } from '../types'
import { api } from '../api'

export const AlertsPage: React.FC = () => {
  const [alerts, setAlerts] = useState<AlertItem[]>([])
  const [thresholds, setThresholds] = useState<Record<string, number>>({})
  const [filter, setFilter] = useState('ALL')
  const [loading, setLoading] = useState(false)

  const loadAlerts = async () => {
    setLoading(true)
    try {
      const [alertData, thresh] = await Promise.all([
        api.getAlerts(),
        api.getThresholds(),
      ])
      // Merge in-memory and database history
      setAlerts(alertData.history)
      setThresholds(thresh)
    } catch (err) {
      console.error('Failed to load alerts:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadAlerts()
  }, [])

  const filteredAlerts =
    filter === 'ALL'
      ? alerts
      : alerts.filter((a) => a.category.toUpperCase() === filter.toUpperCase())

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Bell size={18} className="text-amber-400" />
            <span>Alert Engine & Incident Log</span>
          </h2>
          <p className="text-xs text-slate-400">
            Automated monitoring daemon with 60-second cooldown deduplication to prevent notification storms.
          </p>
        </div>
        <button
          onClick={loadAlerts}
          className="p-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-400 hover:text-white transition"
        >
          <RefreshCw size={15} className={loading ? 'animate-spin text-amber-400' : ''} />
        </button>
      </div>

      {/* Thresholds Cards Grid */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
          <Sliders size={14} className="text-cyan-400" />
          <span>Configured Detection Thresholds</span>
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
          {Object.entries(thresholds).map(([key, val]) => (
            <div key={key} className="p-3 rounded-xl bg-slate-950 border border-slate-800/80">
              <span className="text-[10px] text-slate-500 uppercase font-semibold block truncate">
                {key.replace('_', ' ')}
              </span>
              <span className="text-base font-bold text-cyan-400 font-mono">
                {val}
                {key.includes('load') || key.includes('count') || key.includes('runtime') ? '' : '%'}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Alerts Log & Filters */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
            Triggered Incidents ({filteredAlerts.length})
          </h3>
          <div className="flex items-center gap-1.5 flex-wrap">
            {['ALL', 'CPU', 'MEMORY', 'DISK', 'SECURITY', 'AUTOMATION'].map((cat) => (
              <button
                key={cat}
                onClick={() => setFilter(cat)}
                className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition ${
                  filter === cat
                    ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
                    : 'text-slate-400 hover:text-slate-200 bg-slate-950'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {filteredAlerts.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-slate-500 text-xs">
            <CheckCircle size={32} className="text-emerald-500 mb-2" />
            <span>No alerts recorded for this category. All thresholds satisfied.</span>
          </div>
        ) : (
          <div className="space-y-2">
            {filteredAlerts.map((a, i) => (
              <div
                key={i}
                className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 flex items-start justify-between gap-4"
              >
                <div className="flex items-start gap-3">
                  <AlertTriangle
                    size={16}
                    className={`flex-shrink-0 mt-0.5 ${
                      a.level === 'CRITICAL' ? 'text-rose-400' : 'text-amber-400'
                    }`}
                  />
                  <div>
                    <div className="flex items-center gap-2 mb-0.5">
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                          a.level === 'CRITICAL'
                            ? 'bg-rose-950 text-rose-300 border border-rose-800'
                            : 'bg-amber-950 text-amber-300 border border-amber-800'
                        }`}
                      >
                        {a.level}
                      </span>
                      <span className="text-xs font-bold text-slate-300 uppercase">
                        {a.category}
                      </span>
                    </div>
                    <p className="text-xs text-slate-200">{a.message}</p>
                  </div>
                </div>
                <div className="text-[11px] font-mono text-slate-500 flex-shrink-0">
                  {a.date_time || a.time}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
