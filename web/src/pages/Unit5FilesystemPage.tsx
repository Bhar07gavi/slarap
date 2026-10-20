import React, { useState, useEffect } from 'react'
import {
  FolderTree,
  Disc,
  Play,
  CheckCircle2,
  Database,
  ArrowUp,
  ArrowDown,
  Layers,
  BookOpen,
  ChevronDown,
  ChevronUp,
} from 'lucide-react'
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts'
import { api } from '../api'
import { UnitKnowledgeCheck } from '../components/UnitKnowledgeCheck'

export const Unit5FilesystemPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'disk' | 'allocation' | 'freespace' | 'buffering'>('disk')
  const [showTheory, setShowTheory] = useState<boolean>(false)
  const [isCompleted, setIsCompleted] = useState<boolean>(false)

  useEffect(() => {
    try {
      if (localStorage.getItem('slarap_completed_unit5') === 'true') {
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
      localStorage.setItem('slarap_completed_unit5', String(next))
    } catch {
      // ignore
    }
  }

  // --- Disk Scheduling State ---
  const [diskAlg, setDiskAlg] = useState('SCAN')
  const [initialHead, setInitialHead] = useState(53)
  const [direction, setDirection] = useState<'UP' | 'DOWN'>('UP')
  const diskSize = 200
  const [requestStr, setRequestStr] = useState('98, 183, 37, 122, 14, 124, 65, 67')
  const [diskResult, setDiskResult] = useState<any>(null)
  const [comparisonResults, setComparisonResults] = useState<any[] | null>(null)

  // --- File Allocation State ---
  const [allocMethod, setAllocMethod] = useState<'CONTIGUOUS' | 'LINKED' | 'INDEXED'>('CONTIGUOUS')
  const [fileAllocResult, setFileAllocResult] = useState<any>(null)

  // --- Free Space & Buffering State ---
  const [freespaceResult, setFreespaceResult] = useState<any>(null)
  const [bufferModel, setBufferModel] = useState<'SINGLE' | 'DOUBLE' | 'CIRCULAR'>('DOUBLE')
  const [bufferResult, setBufferResult] = useState<any>(null)

  const parseRequests = () => {
    return requestStr
      .split(',')
      .map((s) => Number(s.trim()))
      .filter((n) => !isNaN(n) && n >= 0 && n < diskSize)
  }

  const runDiskSchedule = async () => {
    try {
      const requests = parseRequests()
      const res = await api.runDiskSchedule({
        algorithm: diskAlg,
        requests,
        initial_head: initialHead,
        disk_size: diskSize,
        direction,
      })
      setDiskResult(res)
    } catch (err: any) {
      alert(err.message)
    }
  }

  const compareDiskAll = async () => {
    try {
      const requests = parseRequests()
      const res = await api.compareDiskAlgorithms({
        algorithm: 'COMPARE',
        requests,
        initial_head: initialHead,
        disk_size: diskSize,
        direction,
      })
      setComparisonResults(res)
    } catch (err: any) {
      alert(err.message)
    }
  }

  const runFileAlloc = async () => {
    try {
      const res = await api.runFileAllocation(allocMethod, 32)
      setFileAllocResult(res)
    } catch (err: any) {
      alert(err.message)
    }
  }

  const runFreespace = async () => {
    try {
      const res = await api.getFreeSpaceMap(16)
      setFreespaceResult(res)
    } catch (err: any) {
      alert(err.message)
    }
  }

  const runBuffering = async () => {
    try {
      const res = await api.getIoBuffering(bufferModel)
      setBufferResult(res)
    } catch (err: any) {
      alert(err.message)
    }
  }

  useEffect(() => {
    runDiskSchedule()
    runFileAlloc()
    runFreespace()
    runBuffering()
  }, [])

  const diskChartData = diskResult?.seek_sequence.map((cyl: number, step: number) => ({
    step: `S${step}`,
    cylinder: cyl,
  }))

  return (
    <div className="space-y-6">
      {/* Unit Header */}
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded bg-indigo-950 text-indigo-400 border border-indigo-800">
              Unit 5
            </span>
            <h2 className="text-lg font-bold text-white">File & I/O Management</h2>
          </div>
          <p className="text-xs text-slate-400">
            Disk arm seek scheduling, file allocation methods (Contiguous, Linked, Indexed), and I/O buffering.
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
          <h4 className="font-bold text-white text-sm">Storage & File System Theory</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
              <span className="font-semibold text-cyan-400 block">Disk Scheduling Metrics</span>
              <p className="text-slate-400 leading-relaxed text-[11px]">
                Disk access time = Seek Time (head movement) + Rotational Latency (platter spin) + Transfer Time. Algorithms (SSTF, SCAN, LOOK, C-LOOK) minimize total cylinder seek distance.
              </p>
            </div>
            <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
              <span className="font-semibold text-indigo-400 block">File Allocation Strategies</span>
              <p className="text-slate-400 leading-relaxed text-[11px]">
                <strong>Contiguous:</strong> Fast sequential access, suffer external fragmentation.<br />
                <strong>Linked:</strong> No external fragmentation, slow random access.<br />
                <strong>Indexed (Inodes):</strong> Index block stores pointers; supports fast direct and sequential access.
              </p>
            </div>
            <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
              <span className="font-semibold text-emerald-400 block">I/O Buffering Models</span>
              <p className="text-slate-400 leading-relaxed text-[11px]">
                Hardware transfers blocks to OS buffer while CPU processes previous block in user memory. Double buffering overlaps I/O input time (T) with computation time (C).
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
            Compare SCAN vs C-LOOK on requests [98, 183, 37, 122, 14, 124, 65, 67] starting at cylinder 53 to observe total head movement!
          </span>
        </div>
      </div>

      {/* Main Tabs */}
      <div className="flex p-1.5 rounded-2xl bg-slate-900 border border-slate-800 max-w-2xl overflow-x-auto">
        {[
          { id: 'disk', label: 'Disk Scheduling Lab' },
          { id: 'allocation', label: 'File Allocation Methods' },
          { id: 'freespace', label: 'Free Space Management' },
          { id: 'buffering', label: 'I/O Buffering Models' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex-1 px-3 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition ${
              activeTab === tab.id
                ? 'bg-sky-600 text-white shadow'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* ======================================================== */}
      {/* TAB 1: DISK SCHEDULING LAB */}
      {/* ======================================================== */}
      {activeTab === 'disk' && (
        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Disc size={16} className="text-sky-400" />
                <span>Disk Arm Traversal Simulation</span>
              </h3>
              <p className="text-xs text-slate-400">
                Simulate disk head seek motion across cylinders (0 to 199).
              </p>
            </div>

            {/* Algorithm selector & direction */}
            <div className="flex items-center gap-2 flex-wrap">
              <select
                value={diskAlg}
                onChange={(e) => {
                  setDiskAlg(e.target.value)
                  setTimeout(runDiskSchedule, 50)
                }}
                className="px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-xl text-xs font-semibold text-sky-400"
              >
                <option value="FCFS">FCFS</option>
                <option value="SSTF">SSTF</option>
                <option value="SCAN">SCAN (Elevator)</option>
                <option value="C_SCAN">C-SCAN</option>
                <option value="LOOK">LOOK</option>
                <option value="C_LOOK">C-LOOK</option>
              </select>

              <button
                onClick={() => setDirection(direction === 'UP' ? 'DOWN' : 'UP')}
                className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-slate-300 hover:text-white transition"
                title="Toggle Scan Direction"
              >
                {direction === 'UP' ? <ArrowUp size={13} className="text-emerald-400" /> : <ArrowDown size={13} className="text-rose-400" />}
                <span>{direction}</span>
              </button>

              <button
                onClick={runDiskSchedule}
                className="px-4 py-1.5 bg-sky-600 hover:bg-sky-500 text-white rounded-xl text-xs font-bold transition flex items-center gap-1.5"
              >
                <Play size={13} />
                <span>Run</span>
              </button>

              <button
                onClick={compareDiskAll}
                className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-bold transition"
              >
                Compare All
              </button>
            </div>
          </div>

          {/* Config Controls */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="sm:col-span-2">
              <label className="text-[11px] text-slate-400 block mb-1">
                Pending Request Queue (Cylinders 0 to 199)
              </label>
              <input
                type="text"
                value={requestStr}
                onChange={(e) => setRequestStr(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl font-mono text-xs text-sky-300"
              />
            </div>
            <div>
              <label className="text-[11px] text-slate-400 block mb-1">Initial Head Position</label>
              <input
                type="number"
                min="0"
                max={diskSize - 1}
                value={initialHead}
                onChange={(e) => setInitialHead(Number(e.target.value))}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl font-mono text-xs text-white"
              />
            </div>
          </div>

          {/* Disk Scheduling Results */}
          {diskResult && (
            <div className="space-y-4">
              {/* Stats */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono text-xs">
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                  <span className="text-slate-500 block text-[10px]">Total Head Movement</span>
                  <span className="text-2xl font-bold text-sky-400">
                    {diskResult.total_head_movement}
                  </span>
                  <span className="text-[10px] text-slate-400 block">Cylinders traveled</span>
                </div>
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                  <span className="text-slate-500 block text-[10px]">Average Seek Length</span>
                  <span className="text-2xl font-bold text-indigo-400">
                    {diskResult.average_seek_length}
                  </span>
                  <span className="text-[10px] text-slate-400 block">Cylinders / seek</span>
                </div>
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                  <span className="text-slate-500 block text-[10px]">Initial Position</span>
                  <span className="text-2xl font-bold text-white">{diskResult.initial_head}</span>
                  <span className="text-[10px] text-slate-400 block">Direction: {direction}</span>
                </div>
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                  <span className="text-slate-500 block text-[10px]">Total Requests</span>
                  <span className="text-2xl font-bold text-emerald-400">
                    {diskResult.seek_sequence.length - 1}
                  </span>
                  <span className="text-[10px] text-slate-400 block">Serviced</span>
                </div>
              </div>

              {/* Head Traversal Line Chart */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">
                  Head Seek Trajectory Curve (Cylinder Position vs Service Step)
                </span>
                <div className="h-56 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={diskChartData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                      <XAxis dataKey="step" stroke="#475569" tick={{ fontSize: 10 }} />
                      <YAxis domain={[0, diskSize]} stroke="#475569" tick={{ fontSize: 10 }} />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '12px' }}
                      />
                      <Line
                        type="monotone"
                        dataKey="cylinder"
                        stroke="#38bdf8"
                        strokeWidth={2}
                        dot={{ r: 4, fill: '#38bdf8' }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Step Sequence Breakdown */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">
                  Step-by-Step Movement Rationale
                </span>
                <div className="space-y-1.5 font-mono text-xs max-h-60 overflow-y-auto">
                  {diskResult.steps.map((st: any) => (
                    <div
                      key={st.step}
                      className="p-2.5 rounded-lg bg-slate-900 border border-slate-800/80 flex items-center justify-between"
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-sky-400 font-bold">Step {st.step}</span>
                        <span className="text-slate-200">{st.explanation}</span>
                      </div>
                      <span className="text-slate-400">
                        Dist: {st.distance} | Cum: {st.cumulative_movement}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Comparative Ranking Table */}
              {comparisonResults && (
                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
                  <h4 className="text-xs font-bold text-white uppercase tracking-wider">
                    Comparative Algorithm Benchmark (Ranked by Total Arm Movement)
                  </h4>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left font-mono text-xs">
                      <thead>
                        <tr className="border-b border-slate-800 text-slate-400">
                          <th className="pb-2">RANK</th>
                          <th className="pb-2">ALGORITHM</th>
                          <th className="pb-2">TOTAL MOVEMENT</th>
                          <th className="pb-2">AVG SEEK</th>
                          <th className="pb-2">SEEK SEQUENCE</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60">
                        {comparisonResults.map((c, i) => (
                          <tr key={c.algorithm} className={i === 0 ? 'bg-emerald-950/20' : ''}>
                            <td className="py-2 text-slate-500">#{i + 1}</td>
                            <td className="py-2 font-bold text-white">{c.algorithm}</td>
                            <td className="py-2 text-sky-400 font-bold">{c.total_head_movement}</td>
                            <td className="py-2 text-slate-300">{c.average_seek_length}</td>
                            <td className="py-2 text-slate-400 truncate max-w-xs">{c.seek_sequence.join(' -> ')}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* ======================================================== */}
      {/* TAB 2: FILE ALLOCATION METHODS */}
      {/* ======================================================== */}
      {activeTab === 'allocation' && (
        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <FolderTree size={16} className="text-sky-400" />
                <span>File Allocation Strategies on Disk (32 Blocks)</span>
              </h3>
              <p className="text-xs text-slate-400">
                Compare Contiguous (sequential), Linked (pointer chain), and Indexed (index block) disk allocation.
              </p>
            </div>

            <div className="flex items-center gap-2">
              <select
                value={allocMethod}
                onChange={(e) => {
                  setAllocMethod(e.target.value as any)
                  setTimeout(runFileAlloc, 50)
                }}
                className="px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-xl text-xs font-semibold text-sky-400"
              >
                <option value="CONTIGUOUS">Contiguous Allocation</option>
                <option value="LINKED">Linked Allocation</option>
                <option value="INDEXED">Indexed Allocation</option>
              </select>
              <button
                onClick={runFileAlloc}
                className="px-4 py-1.5 bg-sky-600 hover:bg-sky-500 text-white rounded-xl text-xs font-bold transition flex items-center gap-1.5"
              >
                <Play size={13} />
                <span>Simulate</span>
              </button>
            </div>
          </div>

          {fileAllocResult && (
            <div className="space-y-4">
              {/* Visual Disk Block Matrix */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block">
                  Disk Blocks Allocation Map (Blocks 0 to 31)
                </span>
                <div className="grid grid-cols-4 sm:grid-cols-8 gap-2 font-mono text-[11px]">
                  {fileAllocResult.final_disk_map.map((file: string | null, idx: number) => (
                    <div
                      key={idx}
                      className={`p-2 rounded-lg border text-center truncate ${
                        file
                          ? file.includes('[IDX]')
                            ? 'bg-purple-950/80 border-purple-700 text-purple-300 font-bold'
                            : 'bg-sky-950/60 border-sky-800 text-sky-300 font-semibold'
                          : 'bg-slate-900 border-slate-800 text-slate-600'
                      }`}
                    >
                      <span className="block text-[9px] text-slate-500">#{idx}</span>
                      <span>{file || 'Free'}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Directory Structure */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block">
                  File System Directory Table
                </span>
                <div className="space-y-1.5 font-mono text-xs">
                  {fileAllocResult.directory.map((f: any) => (
                    <div
                      key={f.name}
                      className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-between"
                    >
                      <span className="font-bold text-white">{f.name}</span>
                      <span className="text-slate-400">Length: {f.length} blocks</span>
                      <span className="text-sky-400">
                        {f.start_block !== undefined
                          ? `Start: ${f.start_block} ${f.end_block !== undefined ? `-> End: ${f.end_block}` : ''}`
                          : `Index Block: ${f.index_block}`}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ======================================================== */}
      {/* TAB 3: FREE SPACE MANAGEMENT */}
      {/* ======================================================== */}
      {activeTab === 'freespace' && freespaceResult && (
        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4 font-mono text-xs">
          <div>
            <h3 className="text-sm font-bold text-white font-sans flex items-center gap-2">
              <Database size={16} className="text-sky-400" />
              <span>Free Space Management (Bit Vector & Linked List)</span>
            </h3>
            <p className="text-xs text-slate-400 font-sans mt-0.5">
              Bit Vector (Bitmap) represents disk blocks where bit 0 = Free and bit 1 = Allocated.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
            <div>
              <span className="text-slate-500 block mb-1">Bit Vector String:</span>
              <span className="text-xl font-bold tracking-widest text-sky-400">
                {freespaceResult.bitmap_string}
              </span>
            </div>
            <div>
              <span className="text-slate-500 block mb-1">Free Blocks:</span>
              <span className="text-emerald-400 font-bold">
                {freespaceResult.free_blocks.join(', ')}
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-sans pt-1">
              {freespaceResult.explanation}
            </p>
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* TAB 4: I/O BUFFERING */}
      {/* ======================================================== */}
      {activeTab === 'buffering' && (
        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Layers size={16} className="text-sky-400" />
                <span>Operating System I/O Buffering Models</span>
              </h3>
              <p className="text-xs text-slate-400">
                Smooths out execution speed mismatches between mechanical devices and CPU.
              </p>
            </div>

            <div className="flex gap-2">
              {(['SINGLE', 'DOUBLE', 'CIRCULAR'] as const).map((m) => (
                <button
                  key={m}
                  onClick={() => {
                    setBufferModel(m)
                    setTimeout(runBuffering, 50)
                  }}
                  className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition ${
                    bufferModel === m
                      ? 'bg-sky-600 text-white'
                      : 'bg-slate-950 text-slate-400 border border-slate-800'
                  }`}
                >
                  {m} Buffer
                </button>
              ))}
            </div>
          </div>

          {bufferResult && (
            <div className="p-5 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono text-xs">
                <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                  <span className="text-slate-500 block text-[10px]">Device I/O Time (T)</span>
                  <span className="text-base font-bold text-white">
                    {bufferResult.device_transfer_time_T_ms} ms
                  </span>
                </div>
                <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                  <span className="text-slate-500 block text-[10px]">Buffer Copy Time (C)</span>
                  <span className="text-base font-bold text-white">
                    {bufferResult.system_to_user_copy_C_ms} ms
                  </span>
                </div>
                <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                  <span className="text-slate-500 block text-[10px]">CPU Compute (M)</span>
                  <span className="text-base font-bold text-white">
                    {bufferResult.cpu_computation_time_M_ms} ms
                  </span>
                </div>
                <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                  <span className="text-slate-500 block text-[10px]">Total Time per Block</span>
                  <span className="text-xl font-bold text-sky-400">
                    {bufferResult.time_per_block_ms} ms
                  </span>
                </div>
              </div>
              <p className="text-xs text-slate-300 font-mono bg-slate-900 p-3 rounded-lg">
                {bufferResult.explanation}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Embedded Unit Knowledge Check (Optional) */}
      <UnitKnowledgeCheck
        unitId="unit5"
        unitTitle="Unit 5: File & I/O Management"
        onComplete={() => setIsCompleted(true)}
      />
    </div>
  )
}
