import {
  SystemSnapshotResponse,
  ProcessInfo,
  AlertItem,
  PredictionMetric,
  RecommendationItem,
  TaskRun,
  ScheduledJob,
  WorkflowSummary,
  ScheduleResult,
  UserProfile,
  UserBadge,
  Badge,
  Mission,
  SyllabusUnit,
} from './types'

const API_BASE = '/api'

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  })

  if (!res.ok) {
    let errMsg = `Request failed: ${res.status} ${res.statusText}`
    try {
      const errJson = await res.json()
      if (errJson.detail) errMsg = errJson.detail
    } catch {
      // ignore
    }
    throw new Error(errMsg)
  }

  return res.json()
}

export const api = {
  // System
  getSnapshot: () => request<SystemSnapshotResponse>('/system/snapshot'),
  getHistory: () => request<Record<string, number[]>>('/system/history'),
  getAggregate: (hours = 24, bucket = 'hour') =>
    request<{ bucket: string; hours: number; data: any[] }>(`/system/aggregate?hours=${hours}&bucket=${bucket}`),
  getTopProcesses: (count = 15, sort_by = 'cpu') =>
    request<ProcessInfo[]>(`/system/top-processes?count=${count}&sort_by=${sort_by}`),
  getThresholds: () => request<Record<string, number>>('/system/thresholds'),
  getAlerts: () => request<{ recent_in_memory: AlertItem[]; history: AlertItem[] }>('/alerts/recent'),
  getPredictions: (hours = 24) => request<Record<string, PredictionMetric>>(`/analytics/predictions?hours=${hours}`),
  getRecommendations: () => request<RecommendationItem[]>('/analytics/recommendations'),
  getLogs: () => request<any>('/analytics/logs'),
  generateAllReports: () => request<Record<string, string>>('/reports/all'),

  // Process Manager
  getProcesses: (search?: string, sort_by = 'cpu', limit = 100) => {
    const q = new URLSearchParams({ sort_by, limit: String(limit) })
    if (search) q.append('search', search)
    return request<ProcessInfo[]>(`/processes?${q.toString()}`)
  },
  getProcessTree: (root_pid?: number) => {
    const q = root_pid ? `?root_pid=${root_pid}` : ''
    return request<string[]>(`/processes/tree${q}`)
  },
  killProcess: (pid: number, force = false) =>
    request<{ success: boolean; message: string; pid: number }>('/processes/kill', {
      method: 'POST',
      body: JSON.stringify({ pid, force, confirmed: true }),
    }),

  // Linux Commands
  runCommand: (command: string, timeout = 30) =>
    request<any>('/command/run', {
      method: 'POST',
      body: JSON.stringify({ command, timeout }),
    }),
  runPipeline: (command_a: string, command_b: string) =>
    request<any>('/command/pipeline', {
      method: 'POST',
      body: JSON.stringify({ command_a, command_b }),
    }),
  getBackgroundJobs: () => request<Record<string, any>>('/command/background'),
  startBackgroundJob: (command: string) =>
    request<any>('/command/background/start', {
      method: 'POST',
      body: JSON.stringify({ command }),
    }),

  // Automation
  getWorkflows: () => request<WorkflowSummary[]>('/automation/workflows'),
  runWorkflow: (payload: { workflow_name?: string; tasks?: any[]; mode?: string }) =>
    request<any>('/automation/workflows/run', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  getTaskRuns: (limit = 50) => request<TaskRun[]>(`/automation/runs?limit=${limit}`),
  getScheduledJobs: () => request<ScheduledJob[]>('/automation/scheduler/jobs'),
  addScheduledJob: (job: { name: string; command: string; interval_seconds: number; retries?: number }) =>
    request<ScheduledJob>('/automation/scheduler/jobs', {
      method: 'POST',
      body: JSON.stringify(job),
    }),
  removeScheduledJob: (id: string) =>
    request<{ success: boolean; job_id: string }>(`/automation/scheduler/jobs/${id}`, {
      method: 'DELETE',
    }),
  toggleScheduledJob: (id: string) =>
    request<{ success: boolean; job_id: string }>(`/automation/scheduler/jobs/${id}/toggle`, {
      method: 'POST',
    }),

  // Simulations
  runCpuScheduling: (payload: {
    algorithm: string
    processes: any[]
    time_quantum?: number
    mlfq_config?: any
  }) =>
    request<ScheduleResult>('/simulations/scheduling', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  runRaceCondition: (payload: { iterations: number; threads_count: number; use_mutex: boolean }) =>
    request<any>('/simulations/synchronization/race', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  runPeterson: () =>
    request<any>('/simulations/synchronization/peterson', { method: 'POST' }),
  runProducerConsumer: (capacity = 5, events = 12) =>
    request<any>(`/simulations/synchronization/producer-consumer?capacity=${capacity}&events=${events}`, {
      method: 'POST',
    }),
  runDiningPhilosophers: (strategy = 'asymmetric') =>
    request<any>(`/simulations/synchronization/dining-philosophers?strategy=${strategy}`, {
      method: 'POST',
    }),
  runReadersWriters: (events = 8) =>
    request<any>(`/simulations/synchronization/readers-writers?events=${events}`, {
      method: 'POST',
    }),
  runCoffmanCheck: (params: {
    mutual_exclusion: boolean
    hold_and_wait: boolean
    no_preemption: boolean
    circular_wait: boolean
  }) => {
    const q = new URLSearchParams({
      mutual_exclusion: String(params.mutual_exclusion),
      hold_and_wait: String(params.hold_and_wait),
      no_preemption: String(params.no_preemption),
      circular_wait: String(params.circular_wait),
    })
    return request<any>(`/simulations/deadlock/coffman?${q.toString()}`, { method: 'POST' })
  },
  runRagAnalysis: (payload: any) =>
    request<any>('/simulations/deadlock/rag', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  runBankersSafety: (payload: {
    available: number[]
    allocation: number[][]
    max_matrix: number[][]
    process_names?: string[]
    resource_names?: string[]
  }) =>
    request<any>('/simulations/deadlock/bankers/safety', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  runBankersRequest: (payload: {
    available: number[]
    allocation: number[][]
    max_matrix: number[][]
    process_index: number
    request: number[]
    process_names?: string[]
    resource_names?: string[]
  }) =>
    request<any>('/simulations/deadlock/bankers/request', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  runMemoryAllocation: (payload: { algorithm: string; blocks: number[]; processes: any[] }) =>
    request<any>('/simulations/memory/allocation', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  runPagingTranslation: (logical_address: number, page_size = 1024) =>
    request<any>(`/simulations/memory/paging?logical_address=${logical_address}&page_size=${page_size}`, {
      method: 'POST',
    }),
  runSegmentationTranslation: (segment_number: number, offset: number) =>
    request<any>(`/simulations/memory/segmentation?segment_number=${segment_number}&offset=${offset}`, {
      method: 'POST',
    }),
  runPageReplacement: (payload: { algorithm: string; reference_string: number[]; frame_count: number }) =>
    request<any>('/simulations/memory/page-replacement', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  runBuddyAllocation: (total_memory = 1024) =>
    request<any>(`/simulations/memory/buddy?total_memory=${total_memory}`, { method: 'POST' }),
  runDiskSchedule: (payload: {
    algorithm: string
    requests: number[]
    initial_head?: number
    disk_size?: number
    direction?: string
  }) =>
    request<any>('/simulations/disk/schedule', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  compareDiskAlgorithms: (payload: {
    algorithm: string
    requests: number[]
    initial_head?: number
    disk_size?: number
    direction?: string
  }) =>
    request<any[]>('/simulations/disk/compare', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  runFileAllocation: (method = 'CONTIGUOUS', total_blocks = 32) =>
    request<any>(`/simulations/filesys/allocation?method=${method}&total_blocks=${total_blocks}`, {
      method: 'POST',
    }),
  getFreeSpaceMap: (total_blocks = 16) =>
    request<any>(`/simulations/filesys/freespace?total_blocks=${total_blocks}`),
  getIoBuffering: (model = 'DOUBLE') =>
    request<any>(`/simulations/filesys/buffering?model=${model}`),

  // Academy & Gamification
  getSyllabusUnits: () => request<SyllabusUnit[]>('/academy/units'),
  getMissions: () => request<Mission[]>('/academy/missions'),
  getBadges: () => request<Badge[]>('/academy/badges'),
  getQuiz: (unit_id: string) => request<any[]>(`/academy/quiz/${unit_id}`),
  submitQuiz: (unit_id: string, answers: Record<string, number>) =>
    request<any>(`/academy/quiz/${unit_id}/submit`, {
      method: 'POST',
      body: JSON.stringify({ answers }),
    }),
  getProfile: () => request<UserProfile>('/gamification/profile'),
  getProgress: () => request<any>('/gamification/progress'),
  awardXp: (payload: { activity_id: string; activity_type: string; unit_id: string; title: string; xp: number; details?: string }) =>
    request<any>('/gamification/award-xp', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  resetGamification: () =>
    request<any>('/gamification/reset', { method: 'POST' }),
}

export const gamificationApi = {
  getProgress: async () => ({ data: await api.getProgress() }),
  getBadges: async () => ({ data: await api.getBadges() }),
  getMissions: async () => ({ data: await api.getMissions() }),
  getQuiz: async (unit_id: string) => ({ data: { questions: await api.getQuiz(unit_id) } }),
  submitQuiz: async (unit_id: string, answers: Record<string, number>) => ({
    data: await api.submitQuiz(unit_id, answers),
  }),
  resetProgress: async () => ({ data: await api.resetGamification() }),
}
