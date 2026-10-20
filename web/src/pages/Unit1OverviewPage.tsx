import React, { useState, useEffect } from 'react'
import {
  BookOpen,
  Layers,
  Terminal,
  ShieldCheck,
  Play,
  Loader2,
  ChevronDown,
  ChevronUp,
  CheckCircle2,
} from 'lucide-react'
import { api } from '../api'
import { UnitKnowledgeCheck } from '../components/UnitKnowledgeCheck'

export const Unit1OverviewPage: React.FC = () => {
  const [selectedArch, setSelectedArch] = useState<'monolithic' | 'microkernel' | 'hybrid' | 'modular'>('monolithic')
  const [shellCmd, setShellCmd] = useState('uname -a')
  const [shellOutput, setShellOutput] = useState<string | null>(null)
  const [shellLoading, setShellLoading] = useState(false)
  const [showTheory, setShowTheory] = useState(false)
  const [isCompleted, setIsCompleted] = useState(false)

  useEffect(() => {
    try {
      if (localStorage.getItem('slarap_completed_unit1') === 'true') {
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
      localStorage.setItem('slarap_completed_unit1', String(next))
    } catch {
      // ignore
    }
  }

  const handleRunShell = async () => {
    if (!shellCmd.trim()) return
    setShellLoading(true)
    try {
      const res = await api.runCommand(shellCmd.trim())
      setShellOutput(res.output || '(No output returned)')
    } catch (err: any) {
      setShellOutput(`Error: ${err.message}`)
    } finally {
      setShellLoading(false)
    }
  }

  const architectures = {
    monolithic: {
      name: 'Monolithic Kernel',
      example: 'Linux, Traditional UNIX',
      summary: 'All OS services (VFS, IPC, drivers, scheduler) execute in privileged Ring 0 address space. Fastest execution, but single driver crash can panic kernel.',
      structure: [
        { name: 'User Applications (Ring 3)', type: 'user' },
        { name: 'System Call Interface (SCI)', type: 'boundary' },
        { name: 'VFS, Scheduler, IPC, Network, Drivers (Ring 0)', type: 'kernel' },
        { name: 'Hardware (CPU, Memory, Disks, Network)', type: 'hardware' },
      ],
    },
    microkernel: {
      name: 'Microkernel',
      example: 'Mach, QNX, L4, MINIX',
      summary: 'Only bare essentials stay in Ring 0 (IPC, low-level memory, basic scheduling). File systems and device drivers run in user space as server daemons.',
      structure: [
        { name: 'User Applications & Shell (Ring 3)', type: 'user' },
        { name: 'FS Server, Net Server, Device Drivers (Ring 3)', type: 'user_server' },
        { name: 'Microkernel IPC Boundary', type: 'boundary' },
        { name: 'Minimal Microkernel Core (Ring 0)', type: 'kernel' },
        { name: 'Hardware', type: 'hardware' },
      ],
    },
    hybrid: {
      name: 'Hybrid Kernel',
      example: 'Windows NT (10/11), macOS XNU',
      summary: 'Combines microkernel modularity with monolithic speed by running select performance-critical services (graphics/GUI) directly in kernel space.',
      structure: [
        { name: 'User Applications & Subsystem DLLs (Ring 3)', type: 'user' },
        { name: 'Executive Services & Graphics Subsystem (Ring 0)', type: 'kernel' },
        { name: 'Microkernel Core & HAL (Ring 0)', type: 'kernel' },
        { name: 'Hardware', type: 'hardware' },
      ],
    },
    modular: {
      name: 'Modular Monolithic Kernel',
      example: 'Modern Linux with LKMs (.ko)',
      summary: 'Retains a monolithic core but dynamically loads and unloads kernel modules (.ko) at runtime via insmod/rmmod without system recompilation.',
      structure: [
        { name: 'User Space Applications & Glibc (Ring 3)', type: 'user' },
        { name: 'System Call Layer (syscall)', type: 'boundary' },
        { name: 'Core Kernel + Dynamic Modules (Ring 0)', type: 'kernel' },
        { name: 'Hardware Devices', type: 'hardware' },
      ],
    },
  }

  const currentArch = architectures[selectedArch]

  return (
    <div className="space-y-6">
      {/* Unit Header */}
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded bg-indigo-950 text-indigo-400 border border-indigo-800">
              Unit 1
            </span>
            <h2 className="text-lg font-bold text-white">OS Overview & Kernel Architectures</h2>
          </div>
          <p className="text-xs text-slate-400">
            Hardware abstraction, dual-mode protection (Ring 3 vs Ring 0), and kernel design paradigms.
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
          <h4 className="font-bold text-white text-sm">Key Operating Systems Syllabus Concepts</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
              <span className="font-semibold text-cyan-400 block">Dual-Mode Operation</span>
              <p className="text-slate-400 leading-relaxed text-[11px]">
                CPUs provide hardware privilege rings. Ring 3 (User Mode) runs untrusted applications; Ring 0 (Supervisor/Kernel Mode) executes privileged instructions and direct hardware access.
              </p>
            </div>
            <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
              <span className="font-semibold text-indigo-400 block">System Call Interface (SCI)</span>
              <p className="text-slate-400 leading-relaxed text-[11px]">
                The programmatic boundary through which user programs request kernel services. Handled via software interrupts (`int 0x80` or `syscall` instruction).
              </p>
            </div>
            <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
              <span className="font-semibold text-emerald-400 block">Kernel Responsibilities</span>
              <p className="text-slate-400 leading-relaxed text-[11px]">
                Process scheduling, virtual memory management, filesystem access (VFS), network protocols, inter-process communication (IPC), and hardware device drivers.
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
            Compare kernel layer transitions between Monolithic and Microkernel models, then query Linux kernel release info.
          </span>
        </div>
      </div>

      {/* Visual Architectural Comparison */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Architecture Selector & Details */}
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Layers size={16} className="text-indigo-400" />
              <span>Kernel Architecture Comparison</span>
            </h3>
          </div>

          <div className="grid grid-cols-2 gap-2">
            {(Object.keys(architectures) as Array<keyof typeof architectures>).map((archKey) => (
              <button
                key={archKey}
                onClick={() => setSelectedArch(archKey)}
                className={`p-3 rounded-lg border text-left transition ${
                  selectedArch === archKey
                    ? 'bg-indigo-950/70 border-indigo-500 text-indigo-200'
                    : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="text-xs font-bold">{architectures[archKey].name}</div>
                <div className="text-[10px] text-slate-500 truncate mt-0.5">
                  {architectures[archKey].example}
                </div>
              </button>
            ))}
          </div>

          <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-300 space-y-2">
            <div className="font-bold text-white">{currentArch.name} ({currentArch.example})</div>
            <p className="text-slate-400 text-[11px] leading-relaxed">{currentArch.summary}</p>
          </div>
        </div>

        {/* Structural Layer Diagram */}
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-white mb-3">Address Space & Layer Diagram</h3>
            <div className="space-y-2">
              {currentArch.structure.map((layer, idx) => {
                let badge = 'bg-slate-800 text-slate-300'
                if (layer.type === 'user') badge = 'bg-sky-950/80 text-sky-400 border border-sky-800'
                if (layer.type === 'boundary') badge = 'bg-amber-950/80 text-amber-400 border border-amber-800'
                if (layer.type === 'kernel') badge = 'bg-indigo-950/80 text-indigo-300 border border-indigo-800'
                if (layer.type === 'hardware') badge = 'bg-emerald-950/80 text-emerald-400 border border-emerald-800'

                return (
                  <div
                    key={idx}
                    className={`p-3 rounded-lg text-xs font-semibold flex items-center justify-between ${badge}`}
                  >
                    <span>{layer.name}</span>
                    <span className="text-[10px] uppercase font-mono tracking-wider opacity-80">
                      Layer {idx + 1}
                    </span>
                  </div>
                )
              })}
            </div>
          </div>
          <div className="text-[11px] text-slate-500 font-mono mt-4 pt-3 border-t border-slate-800">
            Protected ring switch occurred via software interrupt trap.
          </div>
        </div>
      </div>

      {/* Practical Linux Inspection Shell */}
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Terminal size={16} className="text-cyan-400" />
            <span>Interactive Kernel Shell Lab</span>
          </h3>
          <div className="flex items-center gap-2">
            {['uname -a', 'cat /proc/version', 'cat /proc/sys/kernel/osrelease'].map((preset) => (
              <button
                key={preset}
                onClick={() => setShellCmd(preset)}
                className="px-2.5 py-1 rounded bg-slate-950 hover:bg-slate-800 border border-slate-800 text-[11px] font-mono text-slate-400 transition"
              >
                {preset}
              </button>
            ))}
          </div>
        </div>

        <div className="flex gap-2">
          <div className="relative flex-1 font-mono text-xs">
            <span className="absolute left-3 top-2.5 text-slate-500">$</span>
            <input
              type="text"
              value={shellCmd}
              onChange={(e) => setShellCmd(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleRunShell()}
              className="w-full pl-7 pr-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-cyan-500"
              placeholder="Enter safe Linux command..."
            />
          </div>
          <button
            onClick={handleRunShell}
            disabled={shellLoading || !shellCmd.trim()}
            className="flex items-center gap-1.5 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white rounded-lg text-xs font-semibold transition"
          >
            {shellLoading ? <Loader2 size={14} className="animate-spin" /> : <Play size={14} />}
            <span>Execute</span>
          </button>
        </div>

        {shellOutput && (
          <pre className="p-3.5 rounded-lg bg-black/60 border border-slate-800 font-mono text-xs text-slate-200 overflow-x-auto whitespace-pre-wrap">
            {shellOutput}
          </pre>
        )}
      </div>

      {/* Embedded Unit Knowledge Check (Optional) */}
      <UnitKnowledgeCheck
        unitId="unit1"
        unitTitle="Unit 1: OS Overview"
        onComplete={() => setIsCompleted(true)}
      />
    </div>
  )
}
