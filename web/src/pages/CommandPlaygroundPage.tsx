import React, { useState, useEffect } from 'react'
import {
  Terminal,
  Play,
  Share2,
  Clock,
  CheckCircle,
  AlertCircle,
  Loader2,
  RefreshCw,
  Layers,
} from 'lucide-react'
import { api } from '../api'

export const CommandPlaygroundPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'single' | 'pipe' | 'background'>('single')

  // Single Command state
  const [singleCmd, setSingleCmd] = useState('ps -eo pid,user,%cpu,%mem,comm --sort=-%cpu | head -10')
  const [singleLoading, setSingleLoading] = useState(false)
  const [singleResult, setSingleResult] = useState<any>(null)
  const [singleError, setSingleError] = useState<string | null>(null)

  // Pipe IPC state
  const [pipeCmd1, setPipeCmd1] = useState('ls -la /var/log')
  const [pipeCmd2, setPipeCmd2] = useState('grep -i error')
  const [pipeLoading, setPipeLoading] = useState(false)
  const [pipeResult, setPipeResult] = useState<any>(null)

  // Background jobs state
  const [bgJobs, setBgJobs] = useState<Record<string, any>>({})
  const [bgCmd, setBgCmd] = useState('sleep 10')
  const [bgLoading, setBgLoading] = useState(false)

  const fetchBgJobs = async () => {
    try {
      const jobs = await api.getBackgroundJobs()
      setBgJobs(jobs)
    } catch (err) {
      console.error('Failed to fetch background jobs:', err)
    }
  }

  useEffect(() => {
    if (activeTab === 'background') {
      fetchBgJobs()
      const t = setInterval(fetchBgJobs, 3000)
      return () => clearInterval(t)
    }
  }, [activeTab])

  const handleRunSingle = async () => {
    if (!singleCmd.trim()) return
    setSingleLoading(true)
    setSingleError(null)
    setSingleResult(null)
    try {
      const res = await api.runCommand(singleCmd.trim())
      setSingleResult(res)
    } catch (err: any) {
      setSingleError(err.message || 'Execution failed')
    } finally {
      setSingleLoading(false)
    }
  }

  const handleRunPipe = async () => {
    if (!pipeCmd1.trim() || !pipeCmd2.trim()) return
    setPipeLoading(true)
    setPipeResult(null)
    try {
      const res = await api.runPipeline(pipeCmd1.trim(), pipeCmd2.trim())
      setPipeResult(res)
    } catch (err: any) {
      setPipeResult({ exit_code: -1, output: err.message, duration: 0 })
    } finally {
      setPipeLoading(false)
    }
  }

  const handleStartBackground = async () => {
    if (!bgCmd.trim()) return
    setBgLoading(true)
    try {
      await api.startBackgroundJob(bgCmd.trim())
      await fetchBgJobs()
      setBgCmd('')
    } catch (err: any) {
      alert(err.message || 'Failed to start background job')
    } finally {
      setBgLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header & Mode Switcher */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Terminal size={18} className="text-cyan-400" />
            <span>Linux Command & IPC Playground</span>
          </h2>
          <p className="text-xs text-slate-400">
            Executes real commands inside the WSL2 Linux environment using `fork()`, `execvp()`, `waitpid()`, and pipes.
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex p-1 rounded-xl bg-slate-950 border border-slate-800">
          <button
            onClick={() => setActiveTab('single')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === 'single' ? 'bg-cyan-600/30 text-cyan-400' : 'text-slate-400 hover:text-white'
            }`}
          >
            Command Execution
          </button>
          <button
            onClick={() => setActiveTab('pipe')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === 'pipe' ? 'bg-cyan-600/30 text-cyan-400' : 'text-slate-400 hover:text-white'
            }`}
          >
            Pipe IPC (cmd1 | cmd2)
          </button>
          <button
            onClick={() => setActiveTab('background')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === 'background' ? 'bg-cyan-600/30 text-cyan-400' : 'text-slate-400 hover:text-white'
            }`}
          >
            Background Jobs
          </button>
        </div>
      </div>

      {/* Tab 1: Single Command Runner */}
      {activeTab === 'single' && (
        <div className="space-y-4">
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
            <div className="flex gap-2">
              <div className="relative flex-1">
                <span className="absolute left-3 top-2.5 text-slate-500 font-mono text-sm">$</span>
                <input
                  type="text"
                  value={singleCmd}
                  onChange={(e) => setSingleCmd(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleRunSingle()}
                  placeholder="Enter Linux command..."
                  className="w-full pl-8 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 font-mono text-xs focus:outline-none focus:border-cyan-500 transition"
                />
              </div>
              <button
                onClick={handleRunSingle}
                disabled={singleLoading || !singleCmd.trim()}
                className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white rounded-xl font-semibold text-xs flex items-center gap-2 transition"
              >
                {singleLoading ? <Loader2 size={15} className="animate-spin" /> : <Play size={15} />}
                <span>Execute</span>
              </button>
            </div>

            {/* Presets */}
            <div className="flex items-center gap-2 flex-wrap text-xs">
              <span className="text-slate-500">Suggested:</span>
              {[
                'uptime',
                'free -h',
                'df -h',
                'cat /proc/cpuinfo | grep "model name" | head -2',
                'uname -a',
                'ls -lh',
              ].map((c) => (
                <button
                  key={c}
                  onClick={() => setSingleCmd(c)}
                  className="px-2 py-0.5 rounded bg-slate-800/80 hover:bg-slate-700 text-slate-300 font-mono text-[11px] transition"
                >
                  {c}
                </button>
              ))}
            </div>
          </div>

          {singleError && (
            <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800 text-rose-300 text-xs flex items-center gap-2">
              <AlertCircle size={16} className="text-rose-400 flex-shrink-0" />
              <span>{singleError}</span>
            </div>
          )}

          {singleResult && (
            <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
              <div className="flex items-center justify-between text-xs font-mono">
                <div className="flex items-center gap-3">
                  <span
                    className={`inline-flex items-center gap-1 font-bold ${
                      singleResult.exit_code === 0 ? 'text-emerald-400' : 'text-rose-400'
                    }`}
                  >
                    {singleResult.exit_code === 0 ? <CheckCircle size={14} /> : <AlertCircle size={14} />}
                    {singleResult.status} (exit {singleResult.exit_code})
                  </span>
                  <span className="text-slate-400">PID: {singleResult.pid}</span>
                </div>
                <span className="text-slate-400">{singleResult.duration}s</span>
              </div>
              <pre className="p-4 rounded-xl bg-black/70 border border-slate-800/80 text-slate-200 font-mono text-xs overflow-x-auto whitespace-pre-wrap max-h-96">
                {singleResult.output || '(No output returned)'}
              </pre>
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Pipe IPC Demo */}
      {activeTab === 'pipe' && (
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800/80 text-xs text-slate-300 leading-relaxed">
            <span className="font-bold text-cyan-400">Operating System Concept:</span> Pipes (`os.pipe()`) create an anonymous simplex data channel between processes. Process A writes to the write-end file descriptor, and Process B reads from the read-end file descriptor.
          </div>

          <div className="flex flex-col sm:flex-row items-center gap-3">
            <div className="w-full sm:flex-1">
              <label className="text-[11px] text-slate-400 block mb-1">Process A (Writer)</label>
              <input
                type="text"
                value={pipeCmd1}
                onChange={(e) => setPipeCmd1(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl font-mono text-xs text-slate-200"
              />
            </div>
            <div className="text-slate-500 font-mono text-xl pt-5">|</div>
            <div className="w-full sm:flex-1">
              <label className="text-[11px] text-slate-400 block mb-1">Process B (Reader)</label>
              <input
                type="text"
                value={pipeCmd2}
                onChange={(e) => setPipeCmd2(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl font-mono text-xs text-slate-200"
              />
            </div>
            <div className="pt-5 w-full sm:w-auto">
              <button
                onClick={handleRunPipe}
                disabled={pipeLoading}
                className="w-full px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-semibold text-xs flex items-center justify-center gap-2 transition"
              >
                {pipeLoading ? <Loader2 size={15} className="animate-spin" /> : <Share2 size={15} />}
                <span>Run Pipe</span>
              </button>
            </div>
          </div>

          {pipeResult && (
            <div className="pt-3 space-y-2">
              <div className="flex items-center justify-between text-xs font-mono text-slate-400">
                <span>$ {pipeResult.command}</span>
                <span>{pipeResult.duration}s</span>
              </div>
              <pre className="p-4 rounded-xl bg-black/70 border border-slate-800 text-slate-200 font-mono text-xs overflow-x-auto whitespace-pre-wrap max-h-80">
                {pipeResult.output || '(No pipe output)'}
              </pre>
            </div>
          )}
        </div>
      )}

      {/* Tab 3: Background Jobs */}
      {activeTab === 'background' && (
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={bgCmd}
              onChange={(e) => setBgCmd(e.target.value)}
              placeholder="Command to fork in background (e.g. sleep 30)..."
              className="flex-1 px-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 font-mono text-xs"
            />
            <button
              onClick={handleStartBackground}
              disabled={bgLoading || !bgCmd.trim()}
              className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl text-xs font-semibold flex items-center gap-2 transition"
            >
              {bgLoading && <Loader2 size={14} className="animate-spin" />}
              <span>Launch Background Job</span>
            </button>
          </div>

          <div className="rounded-xl border border-slate-800 overflow-hidden">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="bg-slate-950 text-slate-400 border-b border-slate-800">
                  <th className="py-2.5 px-4">PID</th>
                  <th className="py-2.5 px-4">COMMAND</th>
                  <th className="py-2.5 px-4 text-right">ELAPSED</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {Object.keys(bgJobs).length === 0 ? (
                  <tr>
                    <td colSpan={3} className="text-center py-8 text-slate-500">
                      No background jobs currently running.
                    </td>
                  </tr>
                ) : (
                  Object.entries(bgJobs).map(([pid, info]: [string, any]) => (
                    <tr key={pid} className="hover:bg-slate-800/40">
                      <td className="py-2.5 px-4 text-cyan-400 font-bold">{pid}</td>
                      <td className="py-2.5 px-4 text-slate-200">{info.command}</td>
                      <td className="py-2.5 px-4 text-right text-slate-400">{info.elapsed}s</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
