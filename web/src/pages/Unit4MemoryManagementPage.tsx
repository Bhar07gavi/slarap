import React, { useState, useEffect } from 'react'
import {
  HardDrive,
  Layers,
  Play,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Database,
  BookOpen,
  ChevronDown,
  ChevronUp,
} from 'lucide-react'
import { api } from '../api'
import { UnitKnowledgeCheck } from '../components/UnitKnowledgeCheck'

export const Unit4MemoryManagementPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'allocation' | 'paging' | 'replacement' | 'buddy'>('allocation')
  const [showTheory, setShowTheory] = useState<boolean>(false)
  const [isCompleted, setIsCompleted] = useState<boolean>(false)

  useEffect(() => {
    try {
      if (localStorage.getItem('slarap_completed_unit4') === 'true') {
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
      localStorage.setItem('slarap_completed_unit4', String(next))
    } catch {
      // ignore
    }
  }

  // --- 1. Memory Allocation State ---
  const [allocAlgorithm, setAllocAlgorithm] = useState<'FIRST_FIT' | 'BEST_FIT' | 'WORST_FIT'>('FIRST_FIT')
  const [blocks, setBlocks] = useState<number[]>([100, 500, 200, 300, 600])
  const [processes, setProcesses] = useState<Array<{ id: string; size: number }>>([
    { id: 'P1', size: 212 },
    { id: 'P2', size: 417 },
    { id: 'P3', size: 112 },
    { id: 'P4', size: 426 },
  ])
  const [allocResult, setAllocResult] = useState<any>(null)

  // --- 2. Paging & Segmentation State ---
  const [logicalAddr, setLogicalAddr] = useState<number>(2500)
  const [pageSize, setPageSize] = useState<number>(1024)
  const [pagingResult, setPagingResult] = useState<any>(null)

  const [segNum, setSegNum] = useState<number>(2)
  const [segOffset, setSegOffset] = useState<number>(150)
  const [segResult, setSegResult] = useState<any>(null)

  // --- 3. Page Replacement State ---
  const [replaceAlg, setReplaceAlg] = useState<'FIFO' | 'LRU' | 'OPTIMAL'>('LRU')
  const [refString, setRefString] = useState<string>('7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1')
  const [frameCount, setFrameCount] = useState<number>(3)
  const [replaceResult, setReplaceResult] = useState<any>(null)

  // --- 4. Buddy Allocation State ---
  const [buddyResult, setBuddyResult] = useState<any>(null)

  const runAllocation = async () => {
    try {
      const res = await api.runMemoryAllocation({
        algorithm: allocAlgorithm,
        blocks,
        processes,
      })
      setAllocResult(res)
    } catch (err: any) {
      alert(err.message)
    }
  }

  const runPaging = async () => {
    try {
      const res = await api.runPagingTranslation(logicalAddr, pageSize)
      setPagingResult(res)
    } catch (err: any) {
      alert(err.message)
    }
  }

  const runSeg = async () => {
    try {
      const res = await api.runSegmentationTranslation(segNum, segOffset)
      setSegResult(res)
    } catch (err: any) {
      alert(err.message)
    }
  }

  const runReplacement = async () => {
    try {
      const refs = refString
        .split(',')
        .map((s) => Number(s.trim()))
        .filter((n) => !isNaN(n))
      const res = await api.runPageReplacement({
        algorithm: replaceAlg,
        reference_string: refs,
        frame_count: frameCount,
      })
      setReplaceResult(res)
    } catch (err: any) {
      alert(err.message)
    }
  }

  const runBuddy = async () => {
    try {
      const res = await api.runBuddyAllocation(1024)
      setBuddyResult(res)
    } catch (err: any) {
      alert(err.message)
    }
  }

  useEffect(() => {
    runAllocation()
    runPaging()
    runSeg()
    runReplacement()
  }, [])

  return (
    <div className="space-y-6">
      {/* Unit Header */}
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded bg-indigo-950 text-indigo-400 border border-indigo-800">
              Unit 4
            </span>
            <h2 className="text-lg font-bold text-white">Memory Management & Paging</h2>
          </div>
          <p className="text-xs text-slate-400">
            Contiguous partition fits, fragmentation analysis, MMU address translation, and page replacement.
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
          <h4 className="font-bold text-white text-sm">Memory Management & Virtual Memory Concepts</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
              <span className="font-semibold text-cyan-400 block">Contiguous Allocation Fits</span>
              <p className="text-slate-400 leading-relaxed text-[11px]">
                <strong>First Fit:</strong> Allocates first hole that is big enough.<br />
                <strong>Best Fit:</strong> Allocates smallest hole that is big enough (leaves tiny leftover holes).<br />
                <strong>Worst Fit:</strong> Allocates largest hole (leaves largest leftover hole).
              </p>
            </div>
            <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
              <span className="font-semibold text-indigo-400 block">Paging vs Segmentation</span>
              <p className="text-slate-400 leading-relaxed text-[11px]">
                <strong>Paging:</strong> Physical memory divided into fixed-size frames; logical memory divided into same-sized pages. Eliminates external fragmentation.<br />
                <strong>Segmentation:</strong> Memory divided into variable-sized logical segments (code, stack, heap).
              </p>
            </div>
            <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
              <span className="font-semibold text-emerald-400 block">Page Replacement & Belady's Anomaly</span>
              <p className="text-slate-400 leading-relaxed text-[11px]">
                When RAM is full, the OS selects a victim page. FIFO replaces oldest (can suffer from Belady's Anomaly where more frames = more page faults). LRU replaces least recently used (stack algorithm, immune to Belady's).
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
            Compare First Fit against Best Fit to observe leftover internal/external fragmentation, then run LRU on reference string [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]!
          </span>
        </div>
      </div>

      {/* Main Tabs */}
      <div className="flex p-1.5 rounded-2xl bg-slate-900 border border-slate-800 max-w-2xl overflow-x-auto">
        {[
          { id: 'allocation', label: 'Contiguous Allocation' },
          { id: 'paging', label: 'Paging & Segmentation' },
          { id: 'replacement', label: 'Virtual Memory (Page Replacement)' },
          { id: 'buddy', label: 'Buddy Allocation' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => {
              setActiveTab(tab.id as any)
              if (tab.id === 'buddy') runBuddy()
            }}
            className={`flex-1 px-3 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition ${
              activeTab === tab.id
                ? 'bg-emerald-600 text-white shadow'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* ======================================================== */}
      {/* TAB 1: CONTIGUOUS ALLOCATION */}
      {/* ======================================================== */}
      {activeTab === 'allocation' && (
        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Layers size={16} className="text-emerald-400" />
                <span>Dynamic Partition Allocation Lab</span>
              </h3>
              <p className="text-xs text-slate-400">
                Compare First Fit, Best Fit, and Worst Fit algorithms and observe internal/external fragmentation.
              </p>
            </div>

            <div className="flex items-center gap-2">
              <select
                value={allocAlgorithm}
                onChange={(e) => {
                  setAllocAlgorithm(e.target.value as any)
                  setTimeout(runAllocation, 50)
                }}
                className="px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs font-semibold text-emerald-400"
              >
                <option value="FIRST_FIT">First Fit</option>
                <option value="BEST_FIT">Best Fit</option>
                <option value="WORST_FIT">Worst Fit</option>
              </select>
              <button
                onClick={runAllocation}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition flex items-center gap-1.5"
              >
                <Play size={14} />
                <span>Simulate</span>
              </button>
            </div>
          </div>

          {/* Allocation Decisions Progression */}
          {allocResult && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Visual Memory Blocks */}
                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    Physical Memory Partition Blocks
                  </span>
                  <div className="space-y-2">
                    {allocResult.final_blocks.map((b: any) => {
                      const allocatedSize = b.total_size - b.remaining_size
                      const usedPct = Math.round((allocatedSize / b.total_size) * 100)
                      return (
                        <div key={b.block_id} className="p-3 rounded-lg bg-slate-900 border border-slate-800 font-mono text-xs space-y-1">
                          <div className="flex justify-between text-slate-300">
                            <span className="font-bold text-cyan-400">Block {b.block_id} ({b.total_size} KB)</span>
                            <span className="text-slate-400">Free: {b.remaining_size} KB ({100 - usedPct}%)</span>
                          </div>
                          <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden">
                            <div className="bg-emerald-500 h-full rounded-full transition-all" style={{ width: `${usedPct}%` }} />
                          </div>
                          <div className="text-[11px] text-slate-500">
                            Allocated to:{' '}
                            {b.allocated_processes.length > 0
                              ? b.allocated_processes.map((p: any) => `${p.id} (${p.size} KB)`).join(', ')
                              : 'None (Free Hole)'}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>

                {/* Step Decisions */}
                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    Step-by-Step Allocation Logic
                  </span>
                  <div className="space-y-2 max-h-80 overflow-y-auto">
                    {allocResult.steps.map((st: any, i: number) => (
                      <div
                        key={i}
                        className={`p-3 rounded-lg border text-xs font-mono space-y-1 ${
                          st.allocated
                            ? 'bg-slate-900 border-slate-800 text-slate-300'
                            : 'bg-rose-950/30 border-rose-800 text-rose-300'
                        }`}
                      >
                        <div className="flex justify-between font-bold">
                          <span>{st.process_id} ({st.process_size} KB)</span>
                          <span>{st.allocated ? `Assigned Block ${st.block_assigned}` : 'FAILED'}</span>
                        </div>
                        <p className="text-[11px] opacity-80">{st.explanation}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Fragmentation Analysis */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between text-xs font-mono">
                <div>
                  <span className="text-slate-500 block">Total Free Memory:</span>
                  <span className="text-base font-bold text-white">{allocResult.total_free_memory} KB</span>
                </div>
                <div>
                  <span className="text-slate-500 block">External Fragmentation:</span>
                  <span
                    className={`text-base font-bold ${
                      allocResult.external_fragmentation_present ? 'text-amber-400' : 'text-emerald-400'
                    }`}
                  >
                    {allocResult.external_fragmentation_present ? 'DETECTED' : 'NONE'}
                  </span>
                </div>
                <div>
                  <span className="text-slate-500 block">Failed Processes:</span>
                  <span className="text-base font-bold text-rose-400">
                    {allocResult.unallocated_processes.length}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ======================================================== */}
      {/* TAB 2: PAGING & SEGMENTATION */}
      {/* ======================================================== */}
      {activeTab === 'paging' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Paging Translation */}
          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Database size={16} className="text-cyan-400" />
              <span>Paging Address Translation Calculator</span>
            </h3>
            <p className="text-xs text-slate-400">
              Logical Address = (Page p * Page Size) + Offset d. Page table maps Page p to Frame f.
            </p>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Logical Address</label>
                <input
                  type="number"
                  value={logicalAddr}
                  onChange={(e) => setLogicalAddr(Number(e.target.value))}
                  className="w-full px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-xl text-xs font-mono text-cyan-400"
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Page Size (Bytes)</label>
                <input
                  type="number"
                  value={pageSize}
                  onChange={(e) => setPageSize(Number(e.target.value))}
                  className="w-full px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-xl text-xs font-mono text-white"
                />
              </div>
            </div>

            <button
              onClick={runPaging}
              className="w-full py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl text-xs font-bold transition"
            >
              Compute Physical Address
            </button>

            {pagingResult && (
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 font-mono text-xs space-y-2">
                <div className="text-emerald-400 font-bold">Translation Result:</div>
                <div>Page Number (p) = {pagingResult.page_number}</div>
                <div>Offset (d) = {pagingResult.offset}</div>
                <div>Frame Number (f) = {pagingResult.frame_number ?? 'INVALID / PAGE FAULT'}</div>
                <div className="text-cyan-300 font-bold">Physical Address = {pagingResult.physical_address ?? 'NONE'}</div>
                <p className="text-[11px] text-slate-400 pt-1 font-sans">{pagingResult.explanation}</p>
              </div>
            )}
          </div>

          {/* Segmentation Translation */}
          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Layers size={16} className="text-purple-400" />
              <span>Segmentation Address Translation</span>
            </h3>
            <p className="text-xs text-slate-400">
              Logical Address = (Segment s, Offset d). Traps on limit violation (d &ge; Limit).
            </p>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Segment Number (0-4)</label>
                <input
                  type="number"
                  min="0"
                  max="4"
                  value={segNum}
                  onChange={(e) => setSegNum(Number(e.target.value))}
                  className="w-full px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-xl text-xs font-mono text-purple-400"
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Offset (Bytes)</label>
                <input
                  type="number"
                  value={segOffset}
                  onChange={(e) => setSegOffset(Number(e.target.value))}
                  className="w-full px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-xl text-xs font-mono text-white"
                />
              </div>
            </div>

            <button
              onClick={runSeg}
              className="w-full py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-xl text-xs font-bold transition"
            >
              Translate Segment
            </button>

            {segResult && (
              <div
                className={`p-4 rounded-xl border font-mono text-xs space-y-2 ${
                  segResult.trap
                    ? 'bg-rose-950/40 border-rose-800 text-rose-300'
                    : 'bg-slate-950 border-slate-800 text-slate-200'
                }`}
              >
                <div className="font-bold flex items-center gap-2">
                  {segResult.trap ? <AlertTriangle size={15} /> : <CheckCircle2 size={15} />}
                  <span>{segResult.trap ? 'TRAP: SEGMENTATION FAULT' : 'VALID ADDRESS'}</span>
                </div>
                <div>Base: {segResult.base} | Limit: {segResult.limit}</div>
                <div>Physical Address: {segResult.physical_address ?? 'NONE (TRAPPED)'}</div>
                <p className="text-[11px] font-sans opacity-90">{segResult.explanation}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* TAB 3: PAGE REPLACEMENT LAB */}
      {/* ======================================================== */}
      {activeTab === 'replacement' && (
        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Database size={16} className="text-cyan-400" />
                <span>Demand Paging Page Replacement Lab</span>
              </h3>
              <p className="text-xs text-slate-400">
                Compare FIFO, LRU, and Belady's Optimal algorithms on configurable page reference strings.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <select
                value={replaceAlg}
                onChange={(e) => {
                  setReplaceAlg(e.target.value as any)
                  setTimeout(runReplacement, 50)
                }}
                className="px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-xl text-xs font-semibold text-cyan-400"
              >
                <option value="FIFO">FIFO (First-In, First-Out)</option>
                <option value="LRU">LRU (Least Recently Used)</option>
                <option value="OPTIMAL">Optimal (Belady's MIN)</option>
              </select>

              <div className="flex items-center gap-1.5 text-xs text-slate-300">
                <span>Frames:</span>
                <input
                  type="number"
                  min="2"
                  max="6"
                  value={frameCount}
                  onChange={(e) => setFrameCount(Number(e.target.value))}
                  className="w-12 px-2 py-1 bg-slate-950 border border-slate-800 rounded text-center font-mono font-bold"
                />
              </div>

              <button
                onClick={runReplacement}
                className="px-4 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl text-xs font-bold transition flex items-center gap-1.5"
              >
                <Play size={14} />
                <span>Simulate</span>
              </button>
            </div>
          </div>

          <div>
            <label className="text-xs text-slate-400 block mb-1">Page Reference String (Comma-separated)</label>
            <input
              type="text"
              value={refString}
              onChange={(e) => setRefString(e.target.value)}
              className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl font-mono text-xs text-cyan-300"
            />
          </div>

          {replaceResult && (
            <div className="space-y-4">
              {/* Metrics Summary */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono text-xs">
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                  <span className="text-slate-500 block text-[10px]">Total Page Faults</span>
                  <span className="text-xl font-bold text-rose-400">{replaceResult.total_faults}</span>
                </div>
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                  <span className="text-slate-500 block text-[10px]">Total Hits</span>
                  <span className="text-xl font-bold text-emerald-400">{replaceResult.total_hits}</span>
                </div>
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                  <span className="text-slate-500 block text-[10px]">Fault Rate</span>
                  <span className="text-xl font-bold text-amber-400">{replaceResult.fault_rate_percent}%</span>
                </div>
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                  <span className="text-slate-500 block text-[10px]">Hit Ratio</span>
                  <span className="text-xl font-bold text-cyan-400">{replaceResult.hit_rate_percent}%</span>
                </div>
              </div>

              {/* Step Grid Trace */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 overflow-x-auto space-y-2">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">
                  Step-by-Step Frame Trace
                </span>
                <div className="space-y-1.5 font-mono text-xs min-w-[600px]">
                  {replaceResult.steps.map((st: any) => (
                    <div
                      key={st.step}
                      className={`p-2.5 rounded-lg border flex items-center justify-between ${
                        st.is_hit
                          ? 'bg-emerald-950/20 border-emerald-900/60 text-emerald-200'
                          : 'bg-slate-900 border-slate-800 text-slate-300'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-cyan-400 font-bold">Step {st.step} (Ref: {st.page})</span>
                        <span>{st.explanation}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-slate-500 text-[10px]">Frames:</span>
                        <div className="flex gap-1">
                          {st.frames.map((f: any, i: number) => (
                            <span
                              key={i}
                              className={`px-2 py-0.5 rounded font-bold ${
                                f === st.page
                                  ? 'bg-cyan-600 text-white'
                                  : 'bg-slate-950 border border-slate-800 text-slate-400'
                              }`}
                            >
                              {f !== null ? f : '-'}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ======================================================== */}
      {/* TAB 4: BUDDY ALLOCATION */}
      {/* ======================================================== */}
      {activeTab === 'buddy' && buddyResult && (
        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Layers size={16} className="text-cyan-400" />
              <span>Buddy System Allocation & Coalescing</span>
            </h3>
            <p className="text-xs text-slate-400">
              Allocates memory in power-of-two blocks. When adjacent buddy blocks are freed, they recursively coalesce into larger blocks.
            </p>
          </div>

          <div className="space-y-2 font-mono text-xs">
            {buddyResult.steps.map((st: any, i: number) => (
              <div key={i} className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
                <div className="flex justify-between items-center text-cyan-400 font-bold">
                  <span>Action: {st.action} Process {st.process_id}</span>
                  <span className="text-slate-400">{st.explanation}</span>
                </div>
                <div className="flex gap-1.5 flex-wrap pt-1">
                  {st.blocks.map((b: any, bIdx: number) => (
                    <div
                      key={bIdx}
                      className={`px-2.5 py-1 rounded text-center border text-[11px] ${
                        b.allocated_to
                          ? 'bg-cyan-950 text-cyan-300 border-cyan-800'
                          : 'bg-slate-900 text-slate-500 border-slate-800'
                      }`}
                    >
                      {b.size} KB {b.allocated_to ? `[${b.allocated_to}]` : '(Free)'}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Embedded Unit Knowledge Check (Optional) */}
      <UnitKnowledgeCheck
        unitId="unit4"
        unitTitle="Unit 4: Memory Management"
        onComplete={() => setIsCompleted(true)}
      />
    </div>
  )
}
