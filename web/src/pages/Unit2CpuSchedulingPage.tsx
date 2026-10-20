import React, { useState, useEffect, useRef } from 'react'
import {
  Layers,
  Play,
  Pause,
  RotateCcw,
  SkipForward,
  Plus,
  Trash2,
  Gauge,
  Clock,
  Cpu,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  BookOpen,
  ArrowRight,
  HelpCircle,
} from 'lucide-react'
import { ProcessScheduleInput, ScheduleResult, ScheduleEvent } from '../types'
import { api } from '../api'
import { UnitKnowledgeCheck } from '../components/UnitKnowledgeCheck'

export const Unit2CpuSchedulingPage: React.FC = () => {
  // Configurable processes list
  const [processes, setProcesses] = useState<ProcessScheduleInput[]>([
    { id: 'P1', arrival_time: 0, burst_time: 5, priority: 2 },
    { id: 'P2', arrival_time: 1, burst_time: 3, priority: 1 },
    { id: 'P3', arrival_time: 2, burst_time: 8, priority: 4 },
    { id: 'P4', arrival_time: 3, burst_time: 6, priority: 3 },
  ])

  const [algorithm, setAlgorithm] = useState<string>('SRTF')
  const [quantum, setQuantum] = useState<number>(2)

  // Simulation execution state
  const [result, setResult] = useState<ScheduleResult | null>(null)
  const [currentStepIdx, setCurrentStepIdx] = useState<number>(0)
  const [isPlaying, setIsPlaying] = useState<boolean>(false)
  const [speedMs, setSpeedMs] = useState<number>(1000)
  const [loading, setLoading] = useState<boolean>(false)
  const [selectedProcessId, setSelectedProcessId] = useState<string>('P1')
  const [showTheory, setShowTheory] = useState<boolean>(false)
  const [isCompleted, setIsCompleted] = useState<boolean>(false)

  useEffect(() => {
    try {
      if (localStorage.getItem('slarap_completed_unit2') === 'true') {
        setIsCompleted(true)
      }
    } catch {
      // ignore
    }
  }, [])

  const toggleCompleted = () => {
    const next = !isCompleted
    setIsCompleted(next)
    try {
      localStorage.setItem('slarap_completed_unit2', String(next))
    } catch {
      // ignore
    }
  }

  // Timer ref for automatic playback
  const playTimerRef = useRef<number | null>(null)

  // Run simulation calculation
  const runSimulation = async () => {
    setIsPlaying(false)
    setLoading(true)
    try {
      const data = await api.runCpuScheduling({
        algorithm,
        processes,
        time_quantum: quantum,
      })
      setResult(data)
      setCurrentStepIdx(0)
    } catch (err: any) {
      alert(`Simulation failed: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    runSimulation()
  }, [algorithm, quantum])

  // Playback timer
  useEffect(() => {
    if (isPlaying && result) {
      playTimerRef.current = setTimeout(() => {
        if (currentStepIdx < result.events.length - 1) {
          setCurrentStepIdx((prev) => prev + 1)
        } else {
          setIsPlaying(false)
        }
      }, speedMs)
    }
    return () => {
      if (playTimerRef.current) clearTimeout(playTimerRef.current)
    }
  }, [isPlaying, currentStepIdx, result, speedMs])

  const currentEvent: ScheduleEvent | null =
    result && result.events.length > 0 ? result.events[currentStepIdx] : null

  const handleAddProcess = () => {
    const nextId = `P${processes.length + 1}`
    setProcesses([
      ...processes,
      { id: nextId, arrival_time: processes.length, burst_time: 4, priority: 2 },
    ])
  }

  const handleRemoveProcess = (id: string) => {
    if (processes.length <= 1) return
    setProcesses(processes.filter((p) => p.id !== id))
  }

  const handleUpdateProcess = (id: string, field: keyof ProcessScheduleInput, val: number) => {
    setProcesses(
      processes.map((p) => (p.id === id ? { ...p, [field]: Math.max(0, val) } : p))
    )
  }

  const getStateColor = (state: string) => {
    switch (state) {
      case 'RUNNING':
        return 'bg-emerald-950 text-emerald-400 border-emerald-500 shadow-lg shadow-emerald-500/20'
      case 'READY':
        return 'bg-cyan-950 text-cyan-300 border-cyan-800'
      case 'WAITING':
        return 'bg-amber-950 text-amber-300 border-amber-800'
      case 'TERMINATED':
        return 'bg-slate-950 text-slate-500 border-slate-800'
      default:
        return 'bg-slate-900 text-slate-400 border-slate-800'
    }
  }

  const selectedPCB = currentEvent?.process_states[selectedProcessId]

  return (
    <div className="space-y-6">
      {/* Unit Header */}
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded bg-indigo-950 text-indigo-400 border border-indigo-800">
              Unit 2
            </span>
            <h2 className="text-lg font-bold text-white">Process Management & CPU Scheduling</h2>
          </div>
          <p className="text-xs text-slate-400">
            Step-by-step CPU scheduling engine with dynamic Gantt chart, PCB states, and preemption analysis.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Topic Completion Indicator */}
          <button
            onClick={toggleCompleted}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition ${
              isCompleted
                ? 'bg-emerald-950/70 text-emerald-400 border-emerald-800'
                : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-slate-200'
            }`}
          >
            <CheckCircle2 size={14} className={isCompleted ? 'text-emerald-400' : 'text-slate-500'} />
            <span>{isCompleted ? 'Topic Completed' : 'Mark Completed'}</span>
          </button>

          {/* Learn More Accordion Toggle */}
          <button
            onClick={() => setShowTheory((prev) => !prev)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 transition"
          >
            <BookOpen size={14} />
            <span>{showTheory ? 'Hide Theory' : 'Learn More'}</span>
            {showTheory ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
          </button>
        </div>
      </div>

      {/* Expandable Theory Section */}
      {showTheory && (
        <div className="p-5 rounded-xl bg-slate-950 border border-slate-800 space-y-4 text-xs text-slate-300">
          <h4 className="font-bold text-white text-sm">CPU Scheduling Concepts & Formulas</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
              <span className="font-semibold text-cyan-400 block">Scheduling Criteria</span>
              <p className="text-slate-400 leading-relaxed text-[11px]">
                <strong>Turnaround Time (TAT):</strong> Completion Time − Arrival Time.<br />
                <strong>Waiting Time (WT):</strong> TAT − Burst Time.<br />
                <strong>Response Time (RT):</strong> First CPU Start Time − Arrival Time.
              </p>
            </div>
            <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
              <span className="font-semibold text-indigo-400 block">Preemptive vs Non-Preemptive</span>
              <p className="text-slate-400 leading-relaxed text-[11px]">
                In non-preemptive (FCFS, SJF), once a process gets the CPU, it keeps it until termination or I/O. In preemptive (SRTF, Round Robin, Priority Preemptive), the OS can context-switch out a running process when higher priority tasks arrive or time slice expires.
              </p>
            </div>
            <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
              <span className="font-semibold text-emerald-400 block">Multi-Level Feedback Queue (MLFQ)</span>
              <p className="text-slate-400 leading-relaxed text-[11px]">
                Multiple priority queues with increasing time quantums. New processes enter top queue. I/O-bound tasks stay in high-priority queues; CPU-bound tasks age down to prevent starvation.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Lab Challenge Banner */}
      <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2.5">
          <span className="font-bold text-indigo-400 uppercase tracking-wider text-[10px]">
            Lab Challenge:
          </span>
          <span className="text-slate-300">
            Compare Round Robin with Quantum = 2 against SRTF to observe turnaround time differences and preemption!
          </span>
        </div>
      </div>

      {/* Algorithm & Workload Controls */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          {/* Algorithm Tabs */}
          <div className="flex flex-wrap gap-1.5">
            {[
              { id: 'FCFS', label: 'FCFS' },
              { id: 'SJF', label: 'SJF (Non-Preemptive)' },
              { id: 'SRTF', label: 'SRTF (Preemptive)' },
              { id: 'PRIORITY', label: 'Priority' },
              { id: 'PRIORITY_PREEMPTIVE', label: 'Priority (Preemptive)' },
              { id: 'ROUND_ROBIN', label: 'Round Robin' },
              { id: 'MLFQ', label: 'MLFQ (Multilevel)' },
            ].map((alg) => (
              <button
                key={alg.id}
                onClick={() => setAlgorithm(alg.id)}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition ${
                  algorithm === alg.id
                    ? 'bg-cyan-600 text-white shadow-md shadow-cyan-600/30'
                    : 'bg-slate-950 text-slate-400 hover:text-white border border-slate-800'
                }`}
              >
                {alg.label}
              </button>
            ))}
          </div>

          {/* Time Quantum for RR */}
          {algorithm === 'ROUND_ROBIN' && (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-xs">
              <span className="text-slate-400 font-semibold">Time Quantum:</span>
              <input
                type="number"
                min="1"
                max="10"
                value={quantum}
                onChange={(e) => setQuantum(Number(e.target.value))}
                className="w-14 px-2 py-0.5 bg-slate-900 border border-slate-700 rounded text-cyan-400 font-mono font-bold text-center"
              />
            </div>
          )}
        </div>

        {/* Process Inputs Table */}
        <div className="rounded-xl border border-slate-800 overflow-hidden bg-slate-950">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="bg-slate-900/90 text-slate-400 border-b border-slate-800">
                  <th className="py-2.5 px-3">PROCESS</th>
                  <th className="py-2.5 px-3">ARRIVAL TIME</th>
                  <th className="py-2.5 px-3">BURST TIME</th>
                  <th className="py-2.5 px-3">PRIORITY (0=HIGHEST)</th>
                  <th className="py-2.5 px-3 text-right">ACTION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {processes.map((p) => (
                  <tr key={p.id} className="hover:bg-slate-900/40">
                    <td className="py-2 px-3 text-cyan-400 font-bold">{p.id}</td>
                    <td className="py-2 px-3">
                      <input
                        type="number"
                        min="0"
                        value={p.arrival_time}
                        onChange={(e) =>
                          handleUpdateProcess(p.id, 'arrival_time', Number(e.target.value))
                        }
                        className="w-16 px-2 py-1 bg-slate-900 border border-slate-800 rounded text-slate-200"
                      />
                    </td>
                    <td className="py-2 px-3">
                      <input
                        type="number"
                        min="1"
                        value={p.burst_time}
                        onChange={(e) =>
                          handleUpdateProcess(p.id, 'burst_time', Number(e.target.value))
                        }
                        className="w-16 px-2 py-1 bg-slate-900 border border-slate-800 rounded text-slate-200"
                      />
                    </td>
                    <td className="py-2 px-3">
                      <input
                        type="number"
                        min="0"
                        value={p.priority ?? 0}
                        onChange={(e) =>
                          handleUpdateProcess(p.id, 'priority', Number(e.target.value))
                        }
                        className="w-16 px-2 py-1 bg-slate-900 border border-slate-800 rounded text-slate-200"
                      />
                    </td>
                    <td className="py-2 px-3 text-right">
                      <button
                        onClick={() => handleRemoveProcess(p.id)}
                        disabled={processes.length <= 1}
                        className="text-slate-500 hover:text-rose-400 disabled:opacity-30 p-1"
                      >
                        <Trash2 size={15} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="p-2.5 bg-slate-900/40 border-t border-slate-800 flex justify-between items-center">
            <button
              onClick={handleAddProcess}
              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-300 flex items-center gap-1.5 transition"
            >
              <Plus size={14} />
              <span>Add Process</span>
            </button>
            <button
              onClick={runSimulation}
              className="px-4 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-xs font-bold text-white transition"
            >
              Recalculate
            </button>
          </div>
        </div>
      </div>

      {/* Interactive Step-by-Step Execution Player */}
      {result && currentEvent && (
        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-6">
          {/* Player Controls Bar */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-xl bg-slate-950 border border-slate-800">
            <div className="flex items-center gap-3">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Simulation Time:
              </span>
              <span className="px-3 py-1 rounded-lg bg-cyan-950 text-cyan-400 border border-cyan-800 text-sm font-mono font-extrabold">
                t = {currentEvent.time}
              </span>
              <span className="text-xs text-slate-500">
                (Step {currentStepIdx + 1} of {result.events.length})
              </span>
            </div>

            {/* Play/Pause/Step Buttons */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => {
                  setCurrentStepIdx(0)
                  setIsPlaying(false)
                }}
                className="p-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 transition"
                title="Reset to beginning"
              >
                <RotateCcw size={16} />
              </button>

              <button
                onClick={() => setIsPlaying(!isPlaying)}
                className="px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs flex items-center gap-1.5 transition"
              >
                {isPlaying ? <Pause size={15} /> : <Play size={15} />}
                <span>{isPlaying ? 'Pause' : 'Play'}</span>
              </button>

              <button
                onClick={() => {
                  setIsPlaying(false)
                  if (currentStepIdx < result.events.length - 1) {
                    setCurrentStepIdx(currentStepIdx + 1)
                  }
                }}
                disabled={currentStepIdx >= result.events.length - 1}
                className="p-2 rounded-lg bg-slate-900 hover:bg-slate-800 disabled:opacity-40 text-slate-300 transition"
                title="Advance 1 step"
              >
                <SkipForward size={16} />
              </button>

              {/* Speed dropdown */}
              <select
                value={speedMs}
                onChange={(e) => setSpeedMs(Number(e.target.value))}
                className="ml-2 px-2.5 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-300"
              >
                <option value={2000}>0.5x (Slow)</option>
                <option value={1000}>1.0x (Normal)</option>
                <option value={500}>2.0x (Fast)</option>
              </select>
            </div>
          </div>

          {/* Dynamic Algorithmic Explanation Callout */}
          <div className="p-4 rounded-xl bg-cyan-950/30 border border-cyan-800/80 flex items-start gap-3">
            <HelpCircle size={18} className="text-cyan-400 mt-0.5 flex-shrink-0" />
            <div className="space-y-1">
              <div className="text-xs font-bold text-cyan-300 uppercase tracking-wider">
                Event: {currentEvent.event_type}
              </div>
              <p className="text-xs text-slate-200 leading-relaxed font-mono">
                {currentEvent.explanation}
              </p>
            </div>
          </div>

          {/* Queues & CPU State Visualization */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* CPU Status */}
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <Cpu size={14} className="text-cyan-400" />
                <span>Running on CPU</span>
              </span>
              <div className="h-16 flex items-center justify-center rounded-lg bg-slate-900 border border-slate-800">
                {currentEvent.running && currentEvent.running !== 'IDLE' ? (
                  <div className="flex items-center gap-3">
                    <span className="text-xl font-bold font-mono text-emerald-400">
                      {currentEvent.running}
                    </span>
                    <span className="text-xs font-mono text-slate-400">
                      Remaining Burst:{' '}
                      {currentEvent.process_states[currentEvent.running]?.remaining_burst}
                    </span>
                  </div>
                ) : (
                  <span className="text-xs text-slate-500 font-mono italic">
                    [CPU Idle • Waiting for processes]
                  </span>
                )}
              </div>
            </div>

            {/* Ready Queue */}
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                Ready Queue ({currentEvent.ready_queue.length})
              </span>
              <div className="h-16 flex items-center gap-2 px-3 overflow-x-auto rounded-lg bg-slate-900 border border-slate-800">
                {currentEvent.ready_queue.length === 0 ? (
                  <span className="text-xs text-slate-500 font-mono italic">Queue Empty</span>
                ) : (
                  currentEvent.ready_queue.map((pid) => (
                    <span
                      key={pid}
                      className="px-2.5 py-1 rounded bg-cyan-950 text-cyan-300 border border-cyan-800 font-mono font-bold text-xs"
                    >
                      {pid}
                    </span>
                  ))
                )}
              </div>
            </div>

            {/* Terminated Processes */}
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                Completed Processes
              </span>
              <div className="h-16 flex items-center gap-2 px-3 overflow-x-auto rounded-lg bg-slate-900 border border-slate-800">
                {Object.values(currentEvent.process_states)
                  .filter((p) => p.state === 'TERMINATED')
                  .map((p) => (
                    <span
                      key={p.id}
                      className="px-2 py-1 rounded bg-slate-900 text-slate-500 border border-slate-800 font-mono text-xs line-through"
                    >
                      {p.id} (t={p.completion_time})
                    </span>
                  ))}
              </div>
            </div>
          </div>

          {/* Growing Gantt Chart Progression */}
          <div className="space-y-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block">
              Gantt Chart Execution Timeline (t=0 to t={currentEvent.time})
            </span>
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 overflow-x-auto">
              <div className="flex items-center min-w-[500px] h-14 border border-slate-800 rounded-lg overflow-hidden">
                {currentEvent.gantt.map((slice, i) => {
                  const isIdle = slice.id === 'IDLE'
                  return (
                    <div
                      key={i}
                      style={{ flexGrow: slice.duration }}
                      className={`h-full border-r border-slate-900 flex flex-col items-center justify-center text-xs font-mono font-bold transition-all ${
                        isIdle
                          ? 'bg-slate-900/80 text-slate-600'
                          : 'bg-cyan-600/30 text-cyan-300 hover:bg-cyan-600/50'
                      }`}
                    >
                      <span>{slice.id}</span>
                      <span className="text-[10px] font-normal text-slate-400">
                        {slice.start}-{slice.end}
                      </span>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>

          {/* Process Control Block (PCB) Inspector */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Process Control Block (PCB) Inspector
              </span>
              <div className="flex gap-1.5">
                {processes.map((p) => (
                  <button
                    key={p.id}
                    onClick={() => setSelectedProcessId(p.id)}
                    className={`px-2.5 py-1 rounded text-xs font-mono font-bold transition ${
                      selectedProcessId === p.id
                        ? 'bg-cyan-600 text-white'
                        : 'bg-slate-950 text-slate-400 border border-slate-800'
                    }`}
                  >
                    {p.id}
                  </button>
                ))}
              </div>
            </div>

            {selectedPCB && (
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3 text-xs font-mono">
                <div>
                  <span className="text-slate-500 block text-[10px]">Process ID</span>
                  <span className="font-bold text-cyan-400">{selectedPCB.id}</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px]">Current State</span>
                  <span
                    className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold border ${getStateColor(
                      selectedPCB.state
                    )}`}
                  >
                    {selectedPCB.state}
                  </span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px]">Arrival Time</span>
                  <span className="text-slate-200">{selectedPCB.arrival_time}</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px]">Remaining Burst</span>
                  <span className="text-amber-400 font-bold">{selectedPCB.remaining_burst}</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px]">First Response (RT)</span>
                  <span className="text-slate-200">
                    {selectedPCB.start_time !== null
                      ? selectedPCB.start_time - selectedPCB.arrival_time
                      : '--'}
                  </span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px]">Completion (CT)</span>
                  <span className="text-slate-200">
                    {selectedPCB.completion_time ?? '--'}
                  </span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px]">Turnaround (TAT)</span>
                  <span className="text-emerald-400 font-bold">
                    {selectedPCB.completion_time
                      ? selectedPCB.completion_time - selectedPCB.arrival_time
                      : '--'}
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Calculated Scheduling Evaluation Metrics */}
      {result && (
        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
            <Gauge size={14} className="text-cyan-400" />
            <span>Algorithm Performance Metrics</span>
          </h3>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-[10px] text-slate-500 block">Average Waiting Time</span>
              <span className="text-2xl font-bold font-mono text-cyan-400">
                {result.metrics.avg_waiting_time}
              </span>
              <span className="text-[10px] text-slate-400 block mt-1">WT = TAT - Burst</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-[10px] text-slate-500 block">Average Turnaround Time</span>
              <span className="text-2xl font-bold font-mono text-indigo-400">
                {result.metrics.avg_turnaround_time}
              </span>
              <span className="text-[10px] text-slate-400 block mt-1">TAT = Comp - Arrival</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-[10px] text-slate-500 block">Average Response Time</span>
              <span className="text-2xl font-bold font-mono text-purple-400">
                {result.metrics.avg_response_time}
              </span>
              <span className="text-[10px] text-slate-400 block mt-1">RT = First Start - Arrival</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-[10px] text-slate-500 block">CPU Utilization</span>
              <span className="text-2xl font-bold font-mono text-emerald-400">
                {result.metrics.cpu_utilization}%
              </span>
              <span className="text-[10px] text-slate-400 block mt-1">Throughput: {result.metrics.throughput}</span>
            </div>
          </div>
        </div>
      )}

      {/* Embedded Unit Knowledge Check (Optional) */}
      <UnitKnowledgeCheck
        unitId="unit2"
        unitTitle="Unit 2: Process Management & CPU Scheduling"
        onComplete={() => setIsCompleted(true)}
      />
    </div>
  )
}
