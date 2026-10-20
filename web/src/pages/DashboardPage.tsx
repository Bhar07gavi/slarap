import React, { useEffect, useState } from 'react'
import {
  Cpu,
  Layers,
  HardDrive,
  Activity,
  ShieldCheck,
  AlertTriangle,
  ArrowRight,
  Terminal,
} from 'lucide-react'
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts'
import { SystemSnapshotResponse, ProcessInfo, AlertItem } from '../types'
import { api } from '../api'

interface DashboardPageProps {
  snapshot: SystemSnapshotResponse | null
  onNavigate: (route: string) => void
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ snapshot, onNavigate }) => {
  const [topProcs, setTopProcs] = useState<ProcessInfo[]>([])
  const [alerts, setAlerts] = useState<AlertItem[]>([])
  const [history, setHistory] = useState<any[]>([])

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [procs, alertData, rawHist] = await Promise.all([
          api.getTopProcesses(5, 'cpu'),
          api.getAlerts(),
          api.getHistory(),
        ])
        setTopProcs(procs)
        setAlerts(alertData.recent_in_memory.slice(0, 3))

        if (rawHist.timestamp && rawHist.timestamp.length > 0) {
          const formatted = rawHist.timestamp.map((ts: number, idx: number) => ({
            time: new Date(ts * 1000).toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
              second: '2-digit',
            }),
            cpu: rawHist.cpu ? rawHist.cpu[idx] : 0,
            memory: rawHist.memory ? rawHist.memory[idx] : 0,
          }))
          setHistory(formatted.slice(-25))
        }
      } catch (err) {
        console.error('Dashboard data fetch error:', err)
      }
    }

    fetchDashboardData()
    const timer = setInterval(fetchDashboardData, 3000)
    return () => clearInterval(timer)
  }, [])

  const sample = snapshot?.sample

  const getBarColor = (val: number) => {
    if (val < 60) return 'bg-emerald-500'
    if (val < 85) return 'bg-amber-500'
    return 'bg-rose-500'
  }

  return (
    <div className="space-y-8">
      {/* 4 Core Summary Cards Only */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* 1. CPU Utilization */}
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 shadow-sm">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span className="font-semibold uppercase tracking-wider">CPU Utilization</span>
            <Cpu size={16} className="text-cyan-400" />
          </div>
          <div className="text-3xl font-extrabold text-white mb-2">
            {sample?.cpu ? `${sample.cpu.toFixed(1)}%` : '--'}
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mb-2">
            <div
              className={`h-full rounded-full transition-all duration-300 ${getBarColor(
                sample?.cpu || 0
              )}`}
              style={{ width: `${sample?.cpu || 0}%` }}
            />
          </div>
          <div className="text-xs text-slate-400">
            {sample?.cpu_count || 1} Cores Active • Load: {sample?.load ? sample.load[0].toFixed(2) : '--'}
          </div>
        </div>

        {/* 2. Memory Utilization */}
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 shadow-sm">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span className="font-semibold uppercase tracking-wider">Memory Utilization</span>
            <Layers size={16} className="text-indigo-400" />
          </div>
          <div className="text-3xl font-extrabold text-white mb-2">
            {sample?.memory ? `${sample.memory.toFixed(1)}%` : '--'}
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mb-2">
            <div
              className={`h-full rounded-full transition-all duration-300 ${getBarColor(
                sample?.memory || 0
              )}`}
              style={{ width: `${sample?.memory || 0}%` }}
            />
          </div>
          <div className="text-xs text-slate-400">
            {sample ? `${sample.memory_used_gb} GB used of ${sample.memory_total_gb} GB` : '--'}
          </div>
        </div>

        {/* 3. Disk Usage */}
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 shadow-sm">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span className="font-semibold uppercase tracking-wider">Disk Usage</span>
            <HardDrive size={16} className="text-emerald-400" />
          </div>
          <div className="text-3xl font-extrabold text-white mb-2">
            {sample?.disk ? `${sample.disk.toFixed(1)}%` : '--'}
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mb-2">
            <div
              className={`h-full rounded-full transition-all duration-300 ${getBarColor(
                sample?.disk || 0
              )}`}
              style={{ width: `${sample?.disk || 0}%` }}
            />
          </div>
          <div className="text-xs text-slate-400">
            {sample ? `${sample.disk_free_gb} GB free of ${sample.disk_total_gb} GB` : '--'}
          </div>
        </div>

        {/* 4. Active Process Count */}
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 shadow-sm">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span className="font-semibold uppercase tracking-wider">Active Processes</span>
            <Terminal size={16} className="text-amber-400" />
          </div>
          <div className="text-3xl font-extrabold text-white mb-2">
            {sample?.process_count || '--'}
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mb-2">
            <div className="h-full bg-amber-500 rounded-full" style={{ width: '100%' }} />
          </div>
          <div className="text-xs text-slate-400">
            System Uptime: {snapshot?.human_uptime || '--'}
          </div>
        </div>
      </div>

      {/* Live Resource Timeline Chart */}
      <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Activity size={16} className="text-cyan-400" />
              <span>Real-Time Resource Telemetry</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Live CPU and RAM utilization streamed from Linux kernel
            </p>
          </div>
          <div className="flex items-center gap-4 text-xs font-medium">
            <span className="flex items-center gap-1.5 text-cyan-400">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-400" /> CPU (%)
            </span>
            <span className="flex items-center gap-1.5 text-indigo-400">
              <span className="w-2.5 h-2.5 rounded-full bg-indigo-400" /> RAM (%)
            </span>
          </div>
        </div>

        <div className="h-64 w-full">
          {history.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={history} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="dashCpuGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="dashMemGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="time" stroke="#64748b" tick={{ fontSize: 10 }} />
                <YAxis domain={[0, 100]} stroke="#64748b" tick={{ fontSize: 10 }} unit="%" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    borderColor: '#334155',
                    borderRadius: '8px',
                    fontSize: '11px',
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="cpu"
                  name="CPU"
                  stroke="#06b6d4"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#dashCpuGrad)"
                  isAnimationActive={false}
                />
                <Area
                  type="monotone"
                  dataKey="memory"
                  name="Memory"
                  stroke="#6366f1"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#dashMemGrad)"
                  isAnimationActive={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-full text-xs text-slate-500">
              Sampling telemetry data...
            </div>
          )}
        </div>
      </div>

      {/* Bottom Grid: Recent Activity & Important Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Concise Top Processes */}
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Cpu size={16} className="text-cyan-400" />
                <span>Active Processes</span>
              </h3>
              <button
                onClick={() => onNavigate('processes')}
                className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1 font-semibold transition"
              >
                <span>Process Manager</span>
                <ArrowRight size={13} />
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 font-semibold">
                    <th className="pb-2">PID</th>
                    <th className="pb-2">PROCESS</th>
                    <th className="pb-2 text-right">CPU</th>
                    <th className="pb-2 text-right">MEM</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono">
                  {topProcs.slice(0, 5).map((p) => (
                    <tr key={p.pid} className="hover:bg-slate-800/30 transition">
                      <td className="py-2.5 text-cyan-400 font-semibold">{p.pid}</td>
                      <td className="py-2.5 text-slate-200 truncate max-w-[160px]">{p.name}</td>
                      <td className="py-2.5 text-right text-emerald-400">
                        {p.cpu_percent ? `${p.cpu_percent.toFixed(1)}%` : '0.0%'}
                      </td>
                      <td className="py-2.5 text-right text-indigo-400">
                        {p.memory_percent ? `${p.memory_percent.toFixed(1)}%` : '0.0%'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Right: Important Alerts */}
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <ShieldCheck size={16} className="text-emerald-400" />
                <span>System Health & Alerts</span>
              </h3>
              <button
                onClick={() => onNavigate('analytics')}
                className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1 font-semibold transition"
              >
                <span>Alerts & Analytics</span>
                <ArrowRight size={13} />
              </button>
            </div>

            {alerts.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-8 text-center text-slate-400 text-xs">
                <ShieldCheck size={28} className="text-emerald-500 mb-2" />
                <span className="font-medium text-slate-300">All thresholds normal</span>
                <span className="text-[11px] text-slate-500 mt-0.5">
                  CPU, Memory, and Disk operate within configured safe bounds.
                </span>
              </div>
            ) : (
              <div className="space-y-2.5">
                {alerts.map((alert, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-lg bg-slate-950 border border-slate-800 flex items-start gap-3"
                  >
                    <AlertTriangle
                      size={15}
                      className={`flex-shrink-0 mt-0.5 ${
                        alert.level === 'CRITICAL' ? 'text-rose-400' : 'text-amber-400'
                      }`}
                    />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between text-[11px] text-slate-400 mb-0.5">
                        <span className="font-bold text-slate-300">
                          {alert.category.toUpperCase()}
                        </span>
                        <span>{alert.time || alert.date_time}</span>
                      </div>
                      <p className="text-xs text-slate-200 truncate">{alert.message}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
