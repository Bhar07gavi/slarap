import React, { useState, useEffect } from 'react'
import {
  ShieldCheck,
  Lock,
  Unlock,
  AlertTriangle,
  Play,
  RotateCcw,
  CheckCircle2,
  KeyRound,
  Layers,
  ArrowRight,
  BookOpen,
  ChevronDown,
  ChevronUp,
} from 'lucide-react'
import { api } from '../api'
import { UnitKnowledgeCheck } from '../components/UnitKnowledgeCheck'

export const Unit3SyncDeadlocksPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'sync' | 'deadlock'>('sync')
  const [showTheory, setShowTheory] = useState<boolean>(false)
  const [isCompleted, setIsCompleted] = useState<boolean>(false)

  useEffect(() => {
    try {
      if (localStorage.getItem('slarap_completed_unit3') === 'true') {
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
      localStorage.setItem('slarap_completed_unit3', String(next))
    } catch {
      // ignore
    }
  }

  // --- Synchronization Lab State ---
  const [syncSubTab, setSyncSubTab] = useState<'race' | 'peterson' | 'producer_consumer' | 'dining'>('race')
  const [raceUseMutex, setRaceUseMutex] = useState(false)
  const [raceResult, setRaceResult] = useState<any>(null)
  const [petersonResult, setPetersonResult] = useState<any>(null)
  const [prodConsResult, setProdConsResult] = useState<any>(null)
  const [diningResult, setDiningResult] = useState<any>(null)
  const [diningStrategy, setDiningStrategy] = useState<'asymmetric' | 'naive_deadlock'>('asymmetric')

  // --- Deadlock Lab State ---
  // Banker's Algorithm default textbook configuration (5 processes, 3 resources)
  const [available, setAvailable] = useState<number[]>([3, 3, 2])
  const [allocation, setAllocation] = useState<number[][]>([
    [0, 1, 0],
    [2, 0, 0],
    [3, 0, 2],
    [2, 1, 1],
    [0, 0, 2],
  ])
  const [maxMatrix, setMaxMatrix] = useState<number[][]>([
    [7, 5, 3],
    [3, 2, 2],
    [9, 0, 2],
    [2, 2, 2],
    [4, 3, 3],
  ])
  const [bankerResult, setBankerResult] = useState<any>(null)

  // Request state
  const [reqProcessIdx, setReqProcessIdx] = useState(1)
  const [reqVector, setReqVector] = useState<number[]>([1, 0, 2])
  const [reqResult, setReqResult] = useState<any>(null)

  // Coffman conditions state
  const [coffmanMutual, setCoffmanMutual] = useState(true)
  const [coffmanHoldWait, setCoffmanHoldWait] = useState(true)
  const [coffmanNoPreempt, setCoffmanNoPreempt] = useState(true)
  const [coffmanCircularWait, setCoffmanCircularWait] = useState(true)
  const [coffmanResult, setCoffmanResult] = useState<any>(null)

  // Execute race condition
  const runRace = async () => {
    try {
      const res = await api.runRaceCondition({ iterations: 5, threads_count: 2, use_mutex: raceUseMutex })
      setRaceResult(res)
    } catch (err: any) {
      alert(err.message)
    }
  }

  // Execute Peterson's algorithm
  const runPeterson = async () => {
    try {
      const res = await api.runPeterson()
      setPetersonResult(res)
    } catch (err: any) {
      alert(err.message)
    }
  }

  // Execute Producer-Consumer
  const runProdCons = async () => {
    try {
      const res = await api.runProducerConsumer(5, 12)
      setProdConsResult(res)
    } catch (err: any) {
      alert(err.message)
    }
  }

  // Execute Dining Philosophers
  const runDining = async () => {
    try {
      const res = await api.runDiningPhilosophers(diningStrategy)
      setDiningResult(res)
    } catch (err: any) {
      alert(err.message)
    }
  }

  // Execute Banker's Algorithm
  const runBankers = async () => {
    try {
      const res = await api.runBankersSafety({
        available,
        allocation,
        max_matrix: maxMatrix,
      })
      setBankerResult(res)
    } catch (err: any) {
      alert(err.message)
    }
  }

  // Execute Resource Request
  const handleTestRequest = async () => {
    try {
      const res = await api.runBankersRequest({
        available,
        allocation,
        max_matrix: maxMatrix,
        process_index: reqProcessIdx,
        request: reqVector,
      })
      setReqResult(res)
    } catch (err: any) {
      alert(err.message)
    }
  }

  // Execute Coffman
  const checkCoffman = async () => {
    try {
      const res = await api.runCoffmanCheck({
        mutual_exclusion: coffmanMutual,
        hold_and_wait: coffmanHoldWait,
        no_preemption: coffmanNoPreempt,
        circular_wait: coffmanCircularWait,
      })
      setCoffmanResult(res)
    } catch (err: any) {
      alert(err.message)
    }
  }

  useEffect(() => {
    runRace()
    runBankers()
    checkCoffman()
  }, [])

  return (
    <div className="space-y-6">
      {/* Unit Header */}
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded bg-indigo-950 text-indigo-400 border border-indigo-800">
              Unit 3
            </span>
            <h2 className="text-lg font-bold text-white">Synchronization & Deadlocks</h2>
          </div>
          <p className="text-xs text-slate-400">
            Critical sections, atomic mutexes, Peterson's algorithm, and Dijkstra's Banker's safety evaluation.
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
          <h4 className="font-bold text-white text-sm">Concurrency & Deadlock Prevention Theory</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
              <span className="font-semibold text-cyan-400 block">Critical Section 3 Requirements</span>
              <p className="text-slate-400 leading-relaxed text-[11px]">
                <strong>1. Mutual Exclusion:</strong> Only one thread in CS.<br />
                <strong>2. Progress:</strong> Selection cannot be postponed indefinitely.<br />
                <strong>3. Bounded Waiting:</strong> Bound on turns before entry.
              </p>
            </div>
            <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
              <span className="font-semibold text-purple-400 block">Coffman's 4 Conditions</span>
              <p className="text-slate-400 leading-relaxed text-[11px]">
                Mutual exclusion, hold and wait, no preemption, circular wait. All 4 must hold simultaneously for a deadlock to occur. Breaking any single condition prevents deadlocks.
              </p>
            </div>
            <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
              <span className="font-semibold text-emerald-400 block">Banker's Algorithm</span>
              <p className="text-slate-400 leading-relaxed text-[11px]">
                A resource allocation and deadlock avoidance algorithm that tests for safety by simulating the allocation for predetermined maximum possible amounts of all resources before approving requests.
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
            Run the Race Condition demo without Mutex to see counter corruption, then evaluate Banker's algorithm with request [1, 0, 2] for Process 1.
          </span>
        </div>
      </div>

      {/* Main Switcher: Synchronization vs Deadlocks */}
      <div className="flex p-1.5 rounded-2xl bg-slate-900 border border-slate-800 max-w-md">
        <button
          onClick={() => setActiveTab('sync')}
          className={`flex-1 py-2 rounded-xl text-xs font-bold transition ${
            activeTab === 'sync' ? 'bg-cyan-600 text-white shadow' : 'text-slate-400 hover:text-white'
          }`}
        >
          Synchronization Lab
        </button>
        <button
          onClick={() => setActiveTab('deadlock')}
          className={`flex-1 py-2 rounded-xl text-xs font-bold transition ${
            activeTab === 'deadlock' ? 'bg-purple-600 text-white shadow' : 'text-slate-400 hover:text-white'
          }`}
        >
          Deadlock & Banker's Lab
        </button>
      </div>

      {/* ======================================================== */}
      {/* TAB 1: SYNCHRONIZATION LAB */}
      {/* ======================================================== */}
      {activeTab === 'sync' && (
        <div className="space-y-6">
          {/* Sub-tabs */}
          <div className="flex gap-2 border-b border-slate-800 pb-2">
            {[
              { id: 'race', label: 'Race Condition vs Mutex' },
              { id: 'peterson', label: "Peterson's Algorithm" },
              { id: 'producer_consumer', label: 'Producer-Consumer (Semaphores)' },
              { id: 'dining', label: 'Dining Philosophers' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => {
                  setSyncSubTab(tab.id as any)
                  if (tab.id === 'peterson') runPeterson()
                  if (tab.id === 'producer_consumer') runProdCons()
                  if (tab.id === 'dining') runDining()
                }}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition ${
                  syncSubTab === tab.id
                    ? 'bg-slate-800 text-cyan-400 border border-slate-700'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Sub-tab 1: Race Condition */}
          {syncSubTab === 'race' && (
            <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div>
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    {raceUseMutex ? (
                      <Lock size={16} className="text-emerald-400" />
                    ) : (
                      <Unlock size={16} className="text-rose-400" />
                    )}
                    <span>Shared Variable Race Condition</span>
                  </h3>
                  <p className="text-xs text-slate-400">
                    Observe how unsynchronized non-atomic Read-Modify-Write instructions cause lost updates.
                  </p>
                </div>

                <div className="flex items-center gap-3">
                  <label className="flex items-center gap-2 text-xs text-slate-300 font-semibold cursor-pointer">
                    <input
                      type="checkbox"
                      checked={raceUseMutex}
                      onChange={(e) => setRaceUseMutex(e.target.checked)}
                      className="rounded border-slate-700 bg-slate-800 text-cyan-600 focus:ring-0"
                    />
                    <span>Enable Mutex Lock Protection</span>
                  </label>
                  <button
                    onClick={runRace}
                    className="px-4 py-1.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-xs font-bold text-white transition flex items-center gap-1.5"
                  >
                    <Play size={13} />
                    <span>Run Simulation</span>
                  </button>
                </div>
              </div>

              {raceResult && (
                <div className="space-y-4">
                  {/* Summary Bar */}
                  <div className="grid grid-cols-3 gap-3 text-xs font-mono">
                    <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                      <span className="text-slate-500 block text-[10px]">Expected Final Value</span>
                      <span className="text-base font-bold text-white">{raceResult.expected_value}</span>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                      <span className="text-slate-500 block text-[10px]">Actual Shared Counter</span>
                      <span
                        className={`text-base font-bold ${
                          raceResult.lost_updates === 0 ? 'text-emerald-400' : 'text-rose-400'
                        }`}
                      >
                        {raceResult.actual_value}
                      </span>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                      <span className="text-slate-500 block text-[10px]">Lost Updates</span>
                      <span
                        className={`text-base font-bold ${
                          raceResult.lost_updates === 0 ? 'text-emerald-400' : 'text-rose-400'
                        }`}
                      >
                        {raceResult.lost_updates}
                      </span>
                    </div>
                  </div>

                  {/* Interleaved execution timeline */}
                  <div className="rounded-xl border border-slate-800 overflow-hidden bg-slate-950 font-mono text-xs">
                    <div className="p-3 border-b border-slate-800 text-slate-400 font-bold uppercase tracking-wider text-[11px]">
                      Interleaved Instruction Trace
                    </div>
                    <div className="divide-y divide-slate-800/60 max-h-80 overflow-y-auto">
                      {raceResult.steps.map((s: any) => (
                        <div key={s.step} className="p-2.5 px-4 flex items-center justify-between hover:bg-slate-900/40">
                          <div className="flex items-center gap-3">
                            <span className="text-slate-500 text-[10px]">Step {s.step}</span>
                            <span className="text-cyan-400 font-bold">{s.thread}</span>
                            <span className="text-slate-200">{s.explanation}</span>
                          </div>
                          <span className="text-slate-400 font-bold">Counter: {s.shared_counter}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Sub-tab 2: Peterson's Algorithm */}
          {syncSubTab === 'peterson' && petersonResult && (
            <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4 font-mono">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <ShieldCheck size={16} className="text-cyan-400" />
                  <span>Peterson's Algorithm (2-Process Mutual Exclusion)</span>
                </h3>
                <p className="text-xs text-slate-400 font-sans mt-0.5">
                  Classic algorithmic solution demonstrating Mutual Exclusion, Progress, and Bounded Waiting using shared flags and turn variable.
                </p>
              </div>

              <div className="space-y-2">
                {petersonResult.steps.map((st: any) => (
                  <div
                    key={st.step}
                    className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between text-xs"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-cyan-400 font-bold">{st.active_process}</span>
                      <span className="text-slate-300">{st.explanation}</span>
                    </div>
                    <div className="flex items-center gap-3 text-[11px] text-slate-400">
                      <span>flag=[{st.flag.map((f: boolean) => String(f)).join(', ')}]</span>
                      <span>turn={st.turn}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Sub-tab 3: Producer-Consumer */}
          {syncSubTab === 'producer_consumer' && prodConsResult && (
            <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <Layers size={16} className="text-cyan-400" />
                    <span>Producer-Consumer (Bounded Buffer Problem)</span>
                  </h3>
                  <p className="text-xs text-slate-400">
                    Synchronized via mutex semaphore (1) and counting semaphores: empty (5) and full (0).
                  </p>
                </div>
                <button
                  onClick={runProdCons}
                  className="px-3 py-1.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-xs font-bold text-white transition flex items-center gap-1.5"
                >
                  <RotateCcw size={13} />
                  <span>Rerun Sequence</span>
                </button>
              </div>

              <div className="space-y-2 font-mono text-xs">
                {prodConsResult.steps.map((st: any) => (
                  <div
                    key={st.step}
                    className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between"
                  >
                    <div className="flex items-center gap-3">
                      <span
                        className={`font-bold ${
                          st.actor === 'Producer' ? 'text-cyan-400' : 'text-purple-400'
                        }`}
                      >
                        [{st.actor}]
                      </span>
                      <span className="text-slate-200">{st.explanation}</span>
                    </div>
                    <div className="flex items-center gap-3 text-[11px] text-slate-400">
                      <span>
                        Buffer: [{st.buffer.length}/{st.buffer_capacity}]
                      </span>
                      <span>
                        sem(empty={st.semaphores.empty}, full={st.semaphores.full})
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Sub-tab 4: Dining Philosophers */}
          {syncSubTab === 'dining' && (
            <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div>
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <AlertTriangle size={16} className="text-amber-400" />
                    <span>Dining Philosophers Concurrency Lab</span>
                  </h3>
                  <p className="text-xs text-slate-400">
                    Compare naive simultaneous left-chopstick acquisition (deadlock) vs Dijkstra's asymmetric solution.
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <select
                    value={diningStrategy}
                    onChange={(e) => setDiningStrategy(e.target.value as any)}
                    className="px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 font-semibold"
                  >
                    <option value="asymmetric">Asymmetric (Deadlock-Free Solution)</option>
                    <option value="naive_deadlock">Naive Simultaneous (Deadlock Cycle)</option>
                  </select>
                  <button
                    onClick={runDining}
                    className="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl text-xs font-bold transition flex items-center gap-1.5"
                  >
                    <Play size={13} />
                    <span>Run</span>
                  </button>
                </div>
              </div>

              {diningResult && (
                <div className="space-y-2 font-mono text-xs">
                  {diningResult.steps.map((st: any) => (
                    <div
                      key={st.step}
                      className={`p-3 rounded-xl border flex items-center justify-between ${
                        st.deadlock_detected
                          ? 'bg-rose-950/40 border-rose-800 text-rose-300'
                          : 'bg-slate-950 border-slate-800 text-slate-200'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <span className="font-bold text-cyan-400">Step {st.step}</span>
                        <span>{st.explanation}</span>
                      </div>
                      <span className="text-[11px] text-slate-400">
                        Forks: [{st.forks.map((f: boolean) => (f ? '1' : '0')).join(', ')}]
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* ======================================================== */}
      {/* TAB 2: DEADLOCK & BANKER'S LAB */}
      {/* ======================================================== */}
      {activeTab === 'deadlock' && (
        <div className="space-y-6">
          {/* Coffman Conditions Checker */}
          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <KeyRound size={16} className="text-purple-400" />
              <span>Coffman 4 Deadlock Conditions Analyzer</span>
            </h3>
            <p className="text-xs text-slate-400">
              Deadlock requires ALL FOUR conditions to hold simultaneously. Breaking any one condition prevents deadlocks.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              {[
                { name: 'Mutual Exclusion', val: coffmanMutual, set: setCoffmanMutual },
                { name: 'Hold and Wait', val: coffmanHoldWait, set: setCoffmanHoldWait },
                { name: 'No Preemption', val: coffmanNoPreempt, set: setCoffmanNoPreempt },
                { name: 'Circular Wait', val: coffmanCircularWait, set: setCoffmanCircularWait },
              ].map((c) => (
                <label
                  key={c.name}
                  className={`p-4 rounded-xl border cursor-pointer transition flex items-center justify-between ${
                    c.val
                      ? 'bg-purple-950/30 border-purple-800 text-purple-200'
                      : 'bg-slate-950 border-slate-800 text-slate-400'
                  }`}
                >
                  <span className="text-xs font-bold">{c.name}</span>
                  <input
                    type="checkbox"
                    checked={c.val}
                    onChange={(e) => {
                      c.set(e.target.checked)
                      setTimeout(checkCoffman, 50)
                    }}
                    className="rounded border-slate-700 bg-slate-800 text-purple-600 focus:ring-0"
                  />
                </label>
              ))}
            </div>

            {coffmanResult && (
              <div
                className={`p-3.5 rounded-xl border text-xs font-semibold flex items-center gap-2 ${
                  coffmanResult.deadlock_possible
                    ? 'bg-rose-950/40 border-rose-800 text-rose-300'
                    : 'bg-emerald-950/40 border-emerald-800 text-emerald-300'
                }`}
              >
                {coffmanResult.deadlock_possible ? <AlertTriangle size={16} /> : <CheckCircle2 size={16} />}
                <span>{coffmanResult.explanation}</span>
              </div>
            )}
          </div>

          {/* Banker's Algorithm Safety Check */}
          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <ShieldCheck size={16} className="text-emerald-400" />
                  <span>Dijkstra's Banker's Algorithm (Deadlock Avoidance)</span>
                </h3>
                <p className="text-xs text-slate-400">
                  Calculates Need Matrix = Max - Allocation and executes the safety algorithm using Work and Finish vectors.
                </p>
              </div>
              <button
                onClick={runBankers}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-xl text-xs font-bold transition flex items-center gap-1.5"
              >
                <Play size={14} />
                <span>Verify Safety</span>
              </button>
            </div>

            {/* Matrices Display */}
            {bankerResult && (
              <div className="space-y-4">
                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 overflow-x-auto">
                  <table className="w-full text-left text-xs font-mono">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-400">
                        <th className="pb-2">PROCESS</th>
                        <th className="pb-2">ALLOCATION (A, B, C)</th>
                        <th className="pb-2">MAX DEMAND (A, B, C)</th>
                        <th className="pb-2 text-cyan-400 font-bold">NEED = MAX - ALLOC</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {bankerResult.process_names.map((p: string, i: number) => (
                        <tr key={p}>
                          <td className="py-2 text-white font-bold">{p}</td>
                          <td className="py-2 text-slate-300">{bankerResult.allocation_matrix[i].join(', ')}</td>
                          <td className="py-2 text-slate-300">{bankerResult.max_matrix[i].join(', ')}</td>
                          <td className="py-2 text-cyan-400 font-bold">{bankerResult.need_matrix[i].join(', ')}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Verdict Callout */}
                <div
                  className={`p-4 rounded-xl border text-xs font-mono font-bold flex items-center gap-3 ${
                    bankerResult.is_safe
                      ? 'bg-emerald-950/40 border-emerald-800 text-emerald-300'
                      : 'bg-rose-950/40 border-rose-800 text-rose-300'
                  }`}
                >
                  {bankerResult.is_safe ? <CheckCircle2 size={18} /> : <AlertTriangle size={18} />}
                  <span>{bankerResult.verdict}</span>
                </div>

                {/* Step-by-Step Safety Progression */}
                <div className="space-y-2">
                  <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">
                    Safety Algorithm Execution Steps
                  </span>
                  {bankerResult.steps.map((st: any) => (
                    <div
                      key={st.step}
                      className="p-3 rounded-xl bg-slate-950 border border-slate-800 font-mono text-xs text-slate-300"
                    >
                      <span className="text-cyan-400 font-bold mr-2">Step {st.step}:</span>
                      <span>{st.explanation}</span>
                    </div>
                  ))}
                </div>

                {/* Resource-Request Algorithm Lab */}
                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
                  <h4 className="text-xs font-bold text-white uppercase tracking-wider">
                    Test Resource-Request Algorithm
                  </h4>
                  <div className="flex flex-col sm:flex-row items-center gap-3">
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-slate-400">Process:</span>
                      <select
                        value={reqProcessIdx}
                        onChange={(e) => setReqProcessIdx(Number(e.target.value))}
                        className="px-2.5 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-white"
                      >
                        {bankerResult.process_names.map((p: string, idx: number) => (
                          <option key={p} value={idx}>
                            {p}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="text-xs text-slate-400">Request Vector (A, B, C):</span>
                      {reqVector.map((val, idx) => (
                        <input
                          key={idx}
                          type="number"
                          min="0"
                          value={val}
                          onChange={(e) => {
                            const copy = [...reqVector]
                            copy[idx] = Number(e.target.value)
                            setReqVector(copy)
                          }}
                          className="w-12 px-2 py-1 bg-slate-900 border border-slate-800 rounded text-center text-xs text-cyan-400 font-mono font-bold"
                        />
                      ))}
                    </div>

                    <button
                      onClick={handleTestRequest}
                      className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition"
                    >
                      Evaluate Request
                    </button>
                  </div>

                  {reqResult && (
                    <div
                      className={`p-3 rounded-lg text-xs font-mono ${
                        reqResult.granted
                          ? 'bg-emerald-950/40 border border-emerald-800 text-emerald-300'
                          : 'bg-rose-950/40 border border-rose-800 text-rose-300'
                      }`}
                    >
                      {reqResult.granted ? reqResult.message : reqResult.error || reqResult.message}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Embedded Unit Knowledge Check (Optional) */}
      <UnitKnowledgeCheck
        unitId="unit3"
        unitTitle="Unit 3: Synchronization & Deadlocks"
        onComplete={() => setIsCompleted(true)}
      />
    </div>
  )
}
