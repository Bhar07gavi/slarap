import React, { useState } from 'react'
import { X, Play, Loader2, CheckCircle, AlertCircle, Terminal } from 'lucide-react'
import { api } from '../api'

interface QuickCommandModalProps {
  isOpen: boolean
  onClose: () => void
}

export const QuickCommandModal: React.FC<QuickCommandModalProps> = ({ isOpen, onClose }) => {
  const [command, setCommand] = useState('uptime')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  if (!isOpen) return null

  const handleRun = async () => {
    if (!command.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await api.runCommand(command.trim())
      setResult(res)
    } catch (err: any) {
      setError(err.message || 'Failed to execute command')
    } finally {
      setLoading(false)
    }
  }

  const quickSamples = ['uptime', 'df -h', 'free -h', 'ps aux | head -8', 'uname -a']

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <div className="w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-[#0b0f19]">
          <div className="flex items-center gap-2 text-cyan-400 font-bold">
            <Terminal size={18} />
            <span>Linux Command Runner</span>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X size={18} />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-4">
          <div className="flex gap-2">
            <div className="relative flex-1">
              <span className="absolute left-3 top-2.5 text-slate-500 font-mono text-sm">$</span>
              <input
                type="text"
                value={command}
                onChange={(e) => setCommand(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleRun()}
                placeholder="Enter safe Linux command..."
                className="w-full pl-8 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 font-mono text-sm focus:outline-none focus:border-cyan-500 transition"
              />
            </div>
            <button
              onClick={handleRun}
              disabled={loading || !command.trim()}
              className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white rounded-xl font-semibold text-sm flex items-center gap-2 transition"
            >
              {loading ? <Loader2 size={16} className="animate-spin" /> : <Play size={16} />}
              <span>Execute</span>
            </button>
          </div>

          {/* Quick presets */}
          <div className="flex items-center gap-2 flex-wrap text-xs">
            <span className="text-slate-500">Quick presets:</span>
            {quickSamples.map((sample) => (
              <button
                key={sample}
                onClick={() => setCommand(sample)}
                className="px-2 py-1 rounded bg-slate-800/80 hover:bg-slate-700 text-slate-300 font-mono transition"
              >
                {sample}
              </button>
            ))}
          </div>

          {/* Output Display */}
          {error && (
            <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800 text-rose-300 text-xs flex items-center gap-2">
              <AlertCircle size={16} className="flex-shrink-0 text-rose-400" />
              <span>{error}</span>
            </div>
          )}

          {result && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs font-mono text-slate-400">
                <div className="flex items-center gap-2">
                  <span
                    className={`inline-flex items-center gap-1 font-bold ${
                      result.exit_code === 0 ? 'text-emerald-400' : 'text-rose-400'
                    }`}
                  >
                    {result.exit_code === 0 ? <CheckCircle size={14} /> : <AlertCircle size={14} />}
                    {result.status} (exit {result.exit_code})
                  </span>
                  <span>PID: {result.pid}</span>
                </div>
                <span>{result.duration}s</span>
              </div>
              <pre className="p-4 bg-black/60 border border-slate-800 rounded-xl text-slate-200 font-mono text-xs overflow-x-auto max-h-64 whitespace-pre-wrap">
                {result.output || '(No output returned)'}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
