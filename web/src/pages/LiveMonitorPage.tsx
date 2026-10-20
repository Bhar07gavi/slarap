import React, { useEffect, useState } from 'react'
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  LineChart,
  Line,
} from 'recharts'
import { Activity, Cpu, Layers, HardDrive } from 'lucide-react'
import { SystemSnapshotResponse } from '../types'
import { api } from '../api'

interface LiveMonitorPageProps {
  snapshot: SystemSnapshotResponse | null
}

export const LiveMonitorPage: React.FC<LiveMonitorPageProps> = ({ snapshot }) => {
  const [history, setHistory] = useState<any[]>([])

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const raw = await api.getHistory()
        if (raw.timestamp && raw.timestamp.length > 0) {
          const formatted = raw.timestamp.map((ts, idx) => ({
            time: new Date(ts * 1000).toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
              second: '2-digit',
            }),
            cpu: raw.cpu ? raw.cpu[idx] : 0,
            memory: raw.memory ? raw.memory[idx] : 0,
            swap: raw.swap ? raw.swap[idx] : 0,
            disk: raw.disk ? raw.disk[idx] : 0,
            upload: raw.network_upload ? raw.network_upload[idx] : 0,
            download: raw.network_download ? raw.network_download[idx] : 0,
          }))
          setHistory(formatted.slice(-40))
        }
      } catch (err) {
        console.error('Failed to load monitor history:', err)
      }
    }
    fetchHistory()
    const timer = setInterval(fetchHistory, 2000)
    return () => clearInterval(timer)
  }, [])

  const sample = snapshot?.sample

  return (
    <div className="space-y-6">
      {/* Header Info */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900 border border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Activity size={18} className="text-cyan-400" />
            <span>Continuous Linux Resource Telemetry</span>
          </h2>
          <p className="text-xs text-slate-400">
            Real-time sampled telemetry via Linux kernel `/proc/stat`, `/proc/meminfo`, and psutil.
          </p>
        </div>
        <div className="flex items-center gap-3 text-xs font-mono">
          <div className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-slate-300">
            Load Avg: {sample?.load.map((l) => l.toFixed(2)).join(', ') || '--'}
          </div>
          <div className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-slate-300">
            Tasks: {sample?.process_count || '--'}
          </div>
        </div>
      </div>

      {/* Per-Core CPU Bars */}
      {sample?.cpu_per_core && (
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-2">
            <Cpu size={14} className="text-cyan-400" />
            <span>Per-Core CPU Utilization ({sample.cpu_per_core.length} Cores)</span>
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
            {sample.cpu_per_core.map((usage, idx) => (
              <div key={idx} className="p-3 rounded-xl bg-slate-950 border border-slate-800/80">
                <div className="flex justify-between text-[11px] font-mono text-slate-400 mb-1">
                  <span>Core {idx}</span>
                  <span className="text-cyan-400 font-bold">{usage.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-300 ${
                      usage < 60 ? 'bg-emerald-400' : usage < 85 ? 'bg-amber-400' : 'bg-rose-400'
                    }`}
                    style={{ width: `${usage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Real-Time Area Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* CPU Chart */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2 text-sm font-bold text-white">
              <Cpu size={16} className="text-cyan-400" />
              <span>CPU Utilization History (%)</span>
            </div>
            <span className="text-xs font-mono font-bold text-cyan-400">
              {sample?.cpu.toFixed(1) || 0}%
            </span>
          </div>
          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={history}>
                <defs>
                  <linearGradient id="cpuGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#38bdf8" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="time" stroke="#475569" tick={{ fontSize: 10 }} />
                <YAxis domain={[0, 100]} stroke="#475569" tick={{ fontSize: 10 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '12px' }}
                />
                <Area type="monotone" dataKey="cpu" stroke="#38bdf8" strokeWidth={2} fill="url(#cpuGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Memory & Swap Chart */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2 text-sm font-bold text-white">
              <Layers size={16} className="text-indigo-400" />
              <span>RAM & Swap Utilization (%)</span>
            </div>
            <div className="flex items-center gap-3 text-xs font-mono">
              <span className="text-indigo-400 font-bold">RAM: {sample?.memory.toFixed(1) || 0}%</span>
              <span className="text-purple-400 font-bold">Swap: {sample?.swap.toFixed(1) || 0}%</span>
            </div>
          </div>
          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={history}>
                <defs>
                  <linearGradient id="memGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#818cf8" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#818cf8" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="time" stroke="#475569" tick={{ fontSize: 10 }} />
                <YAxis domain={[0, 100]} stroke="#475569" tick={{ fontSize: 10 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '12px' }}
                />
                <Area type="monotone" dataKey="memory" stroke="#818cf8" strokeWidth={2} fill="url(#memGrad)" />
                <Line type="monotone" dataKey="swap" stroke="#c084fc" strokeWidth={2} dot={false} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Network Throughput */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2 text-sm font-bold text-white">
              <Activity size={16} className="text-emerald-400" />
              <span>Network I/O Traffic (KB/s)</span>
            </div>
            <div className="flex items-center gap-3 text-xs font-mono">
              <span className="text-emerald-400">↓ {sample?.network_download_kbps.toFixed(1) || 0}</span>
              <span className="text-sky-400">↑ {sample?.network_upload_kbps.toFixed(1) || 0}</span>
            </div>
          </div>
          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={history}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="time" stroke="#475569" tick={{ fontSize: 10 }} />
                <YAxis stroke="#475569" tick={{ fontSize: 10 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '12px' }}
                />
                <Line type="monotone" dataKey="download" stroke="#34d399" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="upload" stroke="#38bdf8" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Disk Usage */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2 text-sm font-bold text-white">
              <HardDrive size={16} className="text-amber-400" />
              <span>Storage Partition Utilization (%)</span>
            </div>
            <span className="text-xs font-mono font-bold text-amber-400">
              {sample?.disk.toFixed(1) || 0}% used
            </span>
          </div>
          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={history}>
                <defs>
                  <linearGradient id="diskGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#fbbf24" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#fbbf24" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="time" stroke="#475569" tick={{ fontSize: 10 }} />
                <YAxis domain={[0, 100]} stroke="#475569" tick={{ fontSize: 10 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '12px' }}
                />
                <Area type="monotone" dataKey="disk" stroke="#fbbf24" strokeWidth={2} fill="url(#diskGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  )
}
