import React, { useEffect, useState } from 'react'
import {
  Workflow as WorkflowIcon,
  Play,
  Plus,
  Trash2,
  ToggleLeft,
  ToggleRight,
  Clock,
  History,
  CheckCircle,
  AlertCircle,
  Loader2,
  RefreshCw,
  Terminal,
} from 'lucide-react'
import { TaskRun, ScheduledJob, WorkflowSummary } from '../types'
import { api } from '../api'
import { CommandPlaygroundPage } from './CommandPlaygroundPage'

export const AutomationPage: React.FC = () => {
  const [automationTab, setAutomationTab] = useState<'workflows' | 'playground'>('workflows')
  const [workflows, setWorkflows] = useState<WorkflowSummary[]>([])
  const [scheduledJobs, setScheduledJobs] = useState<ScheduledJob[]>([])
  const [taskRuns, setTaskRuns] = useState<TaskRun[]>([])
  const [loading, setLoading] = useState(false)

  // Running workflow state
  const [runningWf, setRunningWf] = useState<string | null>(null)
  const [wfResults, setWfResults] = useState<any[] | null>(null)

  // Add Job Form State
  const [showAddJob, setShowAddJob] = useState(false)
  const [newJobName, setNewJobName] = useState('')
  const [newJobCmd, setNewJobCmd] = useState('')
  const [newJobInterval, setNewJobInterval] = useState(60)

  const loadData = async () => {
    setLoading(true)
    try {
      const [wfList, jobs, runs] = await Promise.all([
        api.getWorkflows(),
        api.getScheduledJobs(),
        api.getTaskRuns(30),
      ])
      setWorkflows(wfList)
      setScheduledJobs(jobs)
      setTaskRuns(runs)
    } catch (err) {
      console.error('Failed to load automation data:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleRunWorkflow = async (name: string) => {
    setRunningWf(name)
    setWfResults(null)
    try {
      const res = await api.runWorkflow({ workflow_name: name })
      setWfResults(res.results)
      await loadData()
    } catch (err: any) {
      alert(`Workflow execution failed: ${err.message}`)
    } finally {
      setRunningWf(null)
    }
  }

  const handleAddJob = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newJobName || !newJobCmd) return
    try {
      await api.addScheduledJob({
        name: newJobName,
        command: newJobCmd,
        interval_seconds: Number(newJobInterval),
      })
      setShowAddJob(false)
      setNewJobName('')
      setNewJobCmd('')
      await loadData()
    } catch (err: any) {
      alert(err.message)
    }
  }

  const handleToggleJob = async (id: string) => {
    try {
      await api.toggleScheduledJob(id)
      await loadData()
    } catch (err: any) {
      alert(err.message)
    }
  }

  const handleDeleteJob = async (id: string) => {
    try {
      await api.removeScheduledJob(id)
      await loadData()
    } catch (err: any) {
      alert(err.message)
    }
  }

  return (
    <div className="space-y-6">
      {/* Sub-tab navigation */}
      <div className="flex items-center gap-2 p-1.5 bg-slate-900 border border-slate-800 rounded-xl">
        <button
          onClick={() => setAutomationTab('workflows')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition ${
            automationTab === 'workflows'
              ? 'bg-cyan-600 text-white shadow-sm'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          }`}
        >
          <WorkflowIcon size={15} />
          <span>Workflows & Scheduler</span>
        </button>

        <button
          onClick={() => setAutomationTab('playground')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition ${
            automationTab === 'playground'
              ? 'bg-cyan-600 text-white shadow-sm'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          }`}
        >
          <Terminal size={15} />
          <span>Linux Command Playground</span>
        </button>
      </div>

      {automationTab === 'playground' ? (
        <CommandPlaygroundPage />
      ) : (
        <>
          {/* Header */}
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <WorkflowIcon size={18} className="text-cyan-400" />
                <span>Automation & Scheduled Job Orchestrator</span>
              </h2>
              <p className="text-xs text-slate-400">
                Multi-threaded task execution engine with ThreadPoolExecutor, retries, and SQLite job logging.
              </p>
            </div>
            <button
              onClick={loadData}
              className="p-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-400 hover:text-white transition"
            >
              <RefreshCw size={15} className={loading ? 'animate-spin text-cyan-400' : ''} />
            </button>
          </div>

          {/* Available JSON Workflows */}
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
          Workflows Catalog (workflows/*.json)
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {workflows.map((wf) => (
            <div
              key={wf.file_name}
              className="p-4 rounded-xl bg-slate-950 border border-slate-800 hover:border-slate-700 transition flex flex-col justify-between gap-3"
            >
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="font-bold text-sm text-white">{wf.name}</span>
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800">
                    {wf.mode.toUpperCase()}
                  </span>
                </div>
                <p className="text-xs text-slate-400 mb-2">{wf.tasks.length} Parallel Tasks configured</p>
                <div className="space-y-1">
                  {wf.tasks.map((t, i) => (
                    <div key={i} className="text-[11px] font-mono text-slate-400 truncate">
                      • {t.name}: <span className="text-slate-500">{t.command}</span>
                    </div>
                  ))}
                </div>
              </div>

              <button
                onClick={() => handleRunWorkflow(wf.file_name)}
                disabled={runningWf === wf.file_name}
                className="w-full py-2 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white rounded-lg text-xs font-semibold flex items-center justify-center gap-2 transition"
              >
                {runningWf === wf.file_name ? (
                  <Loader2 size={14} className="animate-spin" />
                ) : (
                  <Play size={14} />
                )}
                <span>Execute Workflow</span>
              </button>
            </div>
          ))}
        </div>

        {/* Live Execution Results */}
        {wfResults && (
          <div className="p-4 rounded-xl bg-black/60 border border-slate-800 space-y-2">
            <h4 className="text-xs font-bold text-cyan-400">Execution Progression Summary</h4>
            <div className="space-y-1.5 font-mono text-xs">
              {wfResults.map((r, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between p-2 rounded bg-slate-900 border border-slate-800/80"
                >
                  <span className="text-slate-200">{r.task_name}</span>
                  <div className="flex items-center gap-3">
                    <span className="text-slate-400">{r.duration}s</span>
                    <span
                      className={`font-bold ${
                        r.status === 'SUCCESS' ? 'text-emerald-400' : 'text-rose-400'
                      }`}
                    >
                      {r.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Scheduled Jobs Section */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
            <Clock size={14} className="text-cyan-400" />
            <span>Scheduled Periodic Jobs</span>
          </h3>
          <button
            onClick={() => setShowAddJob(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-600/20 text-cyan-400 border border-cyan-500/30 hover:bg-cyan-600/30 text-xs font-semibold transition"
          >
            <Plus size={14} />
            <span>Schedule Job</span>
          </button>
        </div>

        <div className="rounded-xl border border-slate-800 overflow-hidden">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="bg-slate-950 text-slate-400 border-b border-slate-800">
                <th className="py-2.5 px-4">NAME</th>
                <th className="py-2.5 px-4">COMMAND</th>
                <th className="py-2.5 px-4">INTERVAL</th>
                <th className="py-2.5 px-4">RUNS</th>
                <th className="py-2.5 px-4">STATUS</th>
                <th className="py-2.5 px-4 text-right">ACTION</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {scheduledJobs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center py-6 text-slate-500">
                    No scheduled jobs configured.
                  </td>
                </tr>
              ) : (
                scheduledJobs.map((j) => (
                  <tr key={j.id} className="hover:bg-slate-800/40">
                    <td className="py-2.5 px-4 text-white font-bold">{j.name}</td>
                    <td className="py-2.5 px-4 text-slate-300">{j.command}</td>
                    <td className="py-2.5 px-4 text-slate-400">{j.interval}s</td>
                    <td className="py-2.5 px-4 text-cyan-400">{j.runs}</td>
                    <td className="py-2.5 px-4">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          j.enabled
                            ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                            : 'bg-slate-800 text-slate-400'
                        }`}
                      >
                        {j.enabled ? 'ACTIVE' : 'PAUSED'}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 text-right space-x-2">
                      <button
                        onClick={() => handleToggleJob(j.id)}
                        className="p-1 hover:text-cyan-400 transition"
                        title={j.enabled ? 'Pause Job' : 'Enable Job'}
                      >
                        {j.enabled ? <ToggleRight size={18} className="text-emerald-400" /> : <ToggleLeft size={18} className="text-slate-500" />}
                      </button>
                      <button
                        onClick={() => handleDeleteJob(j.id)}
                        className="p-1 hover:text-rose-400 transition text-slate-500"
                        title="Delete Job"
                      >
                        <Trash2 size={16} />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Task Execution History */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
          <History size={14} className="text-cyan-400" />
          <span>Recent Execution Audit Trail</span>
        </h3>
        <div className="rounded-xl border border-slate-800 overflow-hidden">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="bg-slate-950 text-slate-400 border-b border-slate-800">
                <th className="py-2.5 px-4">TIME</th>
                <th className="py-2.5 px-4">TASK</th>
                <th className="py-2.5 px-4">STATUS</th>
                <th className="py-2.5 px-4">EXIT</th>
                <th className="py-2.5 px-4 text-right">DURATION</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {taskRuns.slice(0, 8).map((run, i) => (
                <tr key={i} className="hover:bg-slate-800/40">
                  <td className="py-2.5 px-4 text-slate-500">{run.date_time}</td>
                  <td className="py-2.5 px-4 text-slate-200">{run.task_name}</td>
                  <td className="py-2.5 px-4">
                    <span
                      className={`font-bold ${
                        run.status === 'SUCCESS' ? 'text-emerald-400' : 'text-rose-400'
                      }`}
                    >
                      {run.status}
                    </span>
                  </td>
                  <td className="py-2.5 px-4 text-slate-400">{run.exit_code}</td>
                  <td className="py-2.5 px-4 text-right text-slate-400">{run.duration}s</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Job Modal */}
      {showAddJob && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <form
            onSubmit={handleAddJob}
            className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-4"
          >
            <h4 className="text-sm font-bold text-white">Create Scheduled Automation Job</h4>
            <div>
              <label className="text-xs text-slate-400 block mb-1">Job Name</label>
              <input
                type="text"
                value={newJobName}
                onChange={(e) => setNewJobName(e.target.value)}
                placeholder="disk_health_check"
                required
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200"
              />
            </div>
            <div>
              <label className="text-xs text-slate-400 block mb-1">Command</label>
              <input
                type="text"
                value={newJobCmd}
                onChange={(e) => setNewJobCmd(e.target.value)}
                placeholder="df -h"
                required
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs font-mono text-slate-200"
              />
            </div>
            <div>
              <label className="text-xs text-slate-400 block mb-1">Interval (seconds)</label>
              <input
                type="number"
                min="5"
                value={newJobInterval}
                onChange={(e) => setNewJobInterval(Number(e.target.value))}
                required
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200"
              />
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setShowAddJob(false)}
                className="px-4 py-2 bg-slate-800 text-slate-300 rounded-xl text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl text-xs font-bold"
              >
                Save Job
              </button>
            </div>
          </form>
        </div>
      )}
        </>
      )}
    </div>
  )
}
