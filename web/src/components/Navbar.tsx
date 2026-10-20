import React from 'react'
import {
  Clock,
  RefreshCw,
  Terminal,
} from 'lucide-react'
import { SystemSnapshotResponse } from '../types'

interface NavbarProps {
  currentRoute: string
  snapshot: SystemSnapshotResponse | null
  loading: boolean
  onRefresh: () => void
  onOpenQuickCommand: () => void
}

export const Navbar: React.FC<NavbarProps> = ({
  currentRoute,
  snapshot,
  loading,
  onRefresh,
  onOpenQuickCommand,
}) => {
  const getRouteTitle = (route: string) => {
    const titles: Record<string, { title: string; category: string }> = {
      dashboard: { title: 'Dashboard', category: 'SYSTEM' },
      monitor: { title: 'Live Monitoring', category: 'SYSTEM' },
      processes: { title: 'Process Manager', category: 'SYSTEM' },
      automation: { title: 'Automation & Workflows', category: 'SYSTEM' },
      analytics: { title: 'Alerts & Analytics', category: 'SYSTEM' },
      unit1: { title: 'Unit 1: OS Overview', category: 'OS LABS' },
      unit2: { title: 'Unit 2: Process & CPU Scheduling', category: 'OS LABS' },
      unit3: { title: 'Unit 3: Synchronization & Deadlocks', category: 'OS LABS' },
      unit4: { title: 'Unit 4: Memory Management', category: 'OS LABS' },
      unit5: { title: 'Unit 5: File & I/O Management', category: 'OS LABS' },
      unit6: { title: 'Unit 6: Linux Kernel & Android OS', category: 'OS LABS' },
    }
    return titles[route] || { title: 'SLARAP Platform', category: 'SYSTEM' }
  }

  const { title, category } = getRouteTitle(currentRoute)

  const getHealthBadgeColor = (label: string) => {
    switch (label?.toUpperCase()) {
      case 'EXCELLENT':
        return 'bg-emerald-950/70 text-emerald-400 border-emerald-800'
      case 'GOOD':
        return 'bg-cyan-950/70 text-cyan-400 border-cyan-800'
      case 'FAIR':
        return 'bg-amber-950/70 text-amber-400 border-amber-800'
      default:
        return 'bg-rose-950/70 text-rose-400 border-rose-800'
    }
  }

  return (
    <header className="h-16 px-6 bg-[#0b0f19]/90 backdrop-blur-md border-b border-slate-800 flex items-center justify-between z-20 select-none">
      {/* Title & Category */}
      <div className="flex flex-col">
        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
          {category}
        </span>
        <h1 className="text-sm font-bold text-white tracking-wide">{title}</h1>
      </div>

      {/* Right Action Widgets */}
      <div className="flex items-center gap-3">
        {/* Health Score Pill */}
        {snapshot && (
          <div
            className={`hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-semibold ${getHealthBadgeColor(
              snapshot.health_label
            )}`}
          >
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span>Health: {snapshot.health_score}/100</span>
          </div>
        )}

        {/* Uptime Indicator */}
        {snapshot && (
          <div className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300 font-mono">
            <Clock size={13} className="text-slate-400" />
            <span>Up {snapshot.human_uptime}</span>
          </div>
        )}

        {/* Quick Command Button */}
        <button
          onClick={onOpenQuickCommand}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-xs font-semibold text-slate-300 transition"
          title="Terminal (Ctrl+K)"
        >
          <Terminal size={14} className="text-cyan-400" />
          <span className="hidden sm:inline">Terminal</span>
          <span className="hidden md:inline text-[10px] text-slate-500 font-mono ml-1">^K</span>
        </button>

        {/* Refresh button */}
        <button
          onClick={onRefresh}
          disabled={loading}
          className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white hover:bg-slate-800 transition"
          title="Refresh Data"
        >
          <RefreshCw size={15} className={loading ? 'animate-spin text-cyan-400' : ''} />
        </button>
      </div>
    </header>
  )
}
