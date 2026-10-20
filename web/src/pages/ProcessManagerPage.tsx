import React, { useEffect, useState } from 'react'
import {
  Cpu,
  Search,
  RefreshCw,
  AlertOctagon,
  FolderTree,
  List,
  AlertCircle,
  CheckCircle,
  Loader2,
  X,
} from 'lucide-react'
import { ProcessInfo } from '../types'
import { api } from '../api'

export const ProcessManagerPage: React.FC = () => {
  const [processes, setProcesses] = useState<ProcessInfo[]>([])
  const [search, setSearch] = useState('')
  const [sortBy, setSortBy] = useState('cpu')
  const [loading, setLoading] = useState(false)
  const [viewMode, setViewMode] = useState<'table' | 'tree'>('table')
  const [processTree, setProcessTree] = useState<string[]>([])

  // Kill modal state
  const [selectedProcess, setSelectedProcess] = useState<ProcessInfo | null>(null)
  const [forceKill, setForceKill] = useState(false)
  const [killLoading, setKillLoading] = useState(false)
  const [killMsg, setKillMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  const fetchProcesses = async () => {
    setLoading(true)
    try {
      const data = await api.getProcesses(search, sortBy, 100)
      setProcesses(data)
    } catch (err) {
      console.error('Failed to fetch processes:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchTree = async () => {
    setLoading(true)
    try {
      const tree = await api.getProcessTree()
      setProcessTree(tree)
    } catch (err) {
      console.error('Failed to load process tree:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (viewMode === 'table') {
      fetchProcesses()
    } else {
      fetchTree()
    }
  }, [search, sortBy, viewMode])

  const handleKill = async () => {
    if (!selectedProcess) return
    setKillLoading(true)
    setKillMsg(null)
    try {
      const res = await api.killProcess(selectedProcess.pid, forceKill)
      setKillMsg({ type: 'success', text: res.message })
      setTimeout(() => {
        setSelectedProcess(null)
        setKillMsg(null)
        fetchProcesses()
      }, 1200)
    } catch (err: any) {
      setKillMsg({ type: 'error', text: err.message || 'Termination failed' })
    } finally {
      setKillLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Top Controls Bar */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center gap-3 w-full md:w-auto">
          {/* Search */}
          <div className="relative flex-1 md:w-64">
            <Search size={16} className="absolute left-3 top-2.5 text-slate-500" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by name, PID, user..."
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-cyan-500 transition"
            />
          </div>

          {/* Sort selector */}
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-cyan-500 transition"
          >
            <option value="cpu">Sort: CPU %</option>
            <option value="mem">Sort: Memory %</option>
          </select>
        </div>

        <div className="flex items-center gap-2 w-full md:w-auto justify-end">
          {/* View Mode Toggle */}
          <div className="flex rounded-xl bg-slate-950 border border-slate-800 p-1">
            <button
              onClick={() => setViewMode('table')}
              className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold transition ${
                viewMode === 'table' ? 'bg-cyan-600/30 text-cyan-400' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <List size={14} />
              <span>Table</span>
            </button>
            <button
              onClick={() => setViewMode('tree')}
              className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold transition ${
                viewMode === 'tree' ? 'bg-cyan-600/30 text-cyan-400' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <FolderTree size={14} />
              <span>Tree</span>
            </button>
          </div>

          <button
            onClick={() => (viewMode === 'table' ? fetchProcesses() : fetchTree())}
            className="p-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <RefreshCw size={15} className={loading ? 'animate-spin text-cyan-400' : ''} />
          </button>
        </div>
      </div>

      {/* Process Table or Tree */}
      {viewMode === 'table' ? (
        <div className="rounded-2xl bg-slate-900 border border-slate-800 overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 bg-[#0b0f19] text-slate-400 uppercase tracking-wider font-semibold">
                  <th className="py-3 px-4">PID</th>
                  <th className="py-3 px-4">NAME</th>
                  <th className="py-3 px-4">USER</th>
                  <th className="py-3 px-4 text-right">CPU%</th>
                  <th className="py-3 px-4 text-right">MEM%</th>
                  <th className="py-3 px-4 text-center">STATUS</th>
                  <th className="py-3 px-4 text-right">ACTION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {processes.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="text-center py-10 text-slate-500">
                      No matching processes found.
                    </td>
                  </tr>
                ) : (
                  processes.map((proc) => (
                    <tr key={proc.pid} className="hover:bg-slate-800/40 transition">
                      <td className="py-3 px-4 text-cyan-400 font-bold">{proc.pid}</td>
                      <td className="py-3 px-4 font-semibold text-slate-200 truncate max-w-xs">
                        {proc.name}
                      </td>
                      <td className="py-3 px-4 text-slate-400">{proc.username || 'root'}</td>
                      <td className="py-3 px-4 text-right text-emerald-400 font-bold">
                        {proc.cpu_percent ? `${proc.cpu_percent.toFixed(1)}%` : '0.0%'}
                      </td>
                      <td className="py-3 px-4 text-right text-indigo-400">
                        {proc.memory_percent ? `${proc.memory_percent.toFixed(1)}%` : '0.0%'}
                      </td>
                      <td className="py-3 px-4 text-center">
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-800 text-slate-300">
                          {proc.status || 'running'}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={() => {
                            setSelectedProcess(proc)
                            setKillMsg(null)
                          }}
                          className="px-2.5 py-1 rounded-lg bg-rose-950/40 border border-rose-800/60 text-rose-300 hover:bg-rose-900/60 transition text-[11px] font-semibold"
                        >
                          Terminate
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 font-mono text-xs text-slate-300 overflow-x-auto space-y-1">
          {processTree.map((line, idx) => (
            <div key={idx} className="hover:bg-slate-800/50 px-2 py-0.5 rounded">
              {line}
            </div>
          ))}
        </div>
      )}

      {/* Confirmation Modal */}
      {selectedProcess && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between text-rose-400 font-bold">
              <div className="flex items-center gap-2">
                <AlertOctagon size={20} />
                <span>Confirm Process Termination</span>
              </div>
              <button
                onClick={() => setSelectedProcess(null)}
                className="text-slate-400 hover:text-white"
              >
                <X size={18} />
              </button>
            </div>

            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs space-y-2 font-mono">
              <div>
                <span className="text-slate-500">PID:</span>{' '}
                <span className="text-cyan-400 font-bold">{selectedProcess.pid}</span>
              </div>
              <div>
                <span className="text-slate-500">Name:</span>{' '}
                <span className="text-white font-semibold">{selectedProcess.name}</span>
              </div>
              <div>
                <span className="text-slate-500">User:</span>{' '}
                <span className="text-slate-300">{selectedProcess.username || 'root'}</span>
              </div>
            </div>

            <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
              <input
                type="checkbox"
                checked={forceKill}
                onChange={(e) => setForceKill(e.target.checked)}
                className="rounded border-slate-700 bg-slate-800 text-rose-600 focus:ring-0"
              />
              <span>Send SIGKILL (kill -9) instead of graceful SIGTERM</span>
            </label>

            {killMsg && (
              <div
                className={`p-3 rounded-xl text-xs flex items-center gap-2 ${
                  killMsg.type === 'success'
                    ? 'bg-emerald-950/50 border border-emerald-800 text-emerald-300'
                    : 'bg-rose-950/50 border border-rose-800 text-rose-300'
                }`}
              >
                {killMsg.type === 'success' ? <CheckCircle size={15} /> : <AlertCircle size={15} />}
                <span>{killMsg.text}</span>
              </div>
            )}

            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                onClick={() => setSelectedProcess(null)}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 font-semibold transition"
              >
                Cancel
              </button>
              <button
                onClick={handleKill}
                disabled={killLoading}
                className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-xs text-white font-bold transition flex items-center gap-2"
              >
                {killLoading && <Loader2 size={14} className="animate-spin" />}
                <span>Confirm Kill</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
