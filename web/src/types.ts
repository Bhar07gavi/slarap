export interface SystemSnapshot {
  timestamp: number
  cpu: number
  cpu_per_core: number[]
  memory: number
  memory_used_gb: number
  memory_total_gb: number
  swap: number
  disk: number
  disk_free_gb: number
  disk_total_gb: number
  network_sent: number
  network_received: number
  network_upload_kbps: number
  network_download_kbps: number
  load: [number, number, number]
  process_count: number
  uptime: number
  cpu_count: number
}

export interface SystemSnapshotResponse {
  sample: SystemSnapshot
  health_score: number
  health_label: string
  human_uptime: string
}

export interface ProcessInfo {
  pid: number
  name: string
  username?: string
  cpu_percent?: number
  memory_percent?: number
  status?: string
}

export interface AlertItem {
  id?: number
  timestamp?: number
  date_time?: string
  time?: string
  level: string
  category: string
  message: string
  value?: number
  threshold?: number
}

export interface PredictionMetric {
  current: number
  moving_avg: number
  ewma: number
  forecast: number[]
  next: number
  horizon: number
  slope: number
  trend: string
  samples: number
  growth_per_day?: number
  days_until_full?: number | null
}

export interface RecommendationItem {
  priority: string
  title: string
  detail: string
}

export interface TaskRun {
  id?: number
  date_time: string
  workflow?: string
  task_name: string
  command: string
  execution_mode: string
  status: string
  exit_code: number
  duration: number
  attempts: number
  process_id?: number
  output?: string
}

export interface ScheduledJob {
  id: string
  name: string
  command: string
  interval: number
  next_run: number
  enabled: boolean
  runs: number
  retries?: number
}

export interface WorkflowSummary {
  file_name: string
  name: string
  mode: string
  tasks: Array<{ name: string; command: string }>
}

export interface ProcessScheduleInput {
  id: string
  arrival_time: number
  burst_time: number
  priority?: number
}

export interface ScheduleEvent {
  time: number
  event_type: string
  running: string | null
  ready_queue: string[]
  waiting_queue: string[]
  process_states: Record<string, {
    id: string
    state: string
    arrival_time: number
    burst_time: number
    remaining_burst: number
    priority: number
    start_time: number | null
    completion_time: number | null
    waiting_time: number
    turnaround_time: number
    response_time: number | null
  }>
  explanation: string
  gantt: Array<{ id: string; start: number; end: number; duration: number }>
}

export interface ScheduleResult {
  algorithm: string
  time_quantum?: number
  events: ScheduleEvent[]
  gantt: Array<{ id: string; start: number; end: number; duration: number }>
  metrics: {
    process_metrics: Record<string, any>
    avg_waiting_time: number
    avg_turnaround_time: number
    avg_response_time: number
    cpu_utilization: number
    throughput: number
    total_time: number
  }
}

export interface UserProfile {
  id: number
  username: string
  total_xp: number
  current_level: number
  streak_days: number
  last_active: number
}

export interface UserBadge {
  id?: number
  badge_id: string
  title: string
  description: string
  icon?: string
  earned_at: number
  date_time?: string
}

export interface Mission {
  id: string
  title: string
  unit_id?: string
  category: string
  difficulty?: string
  xp_reward: number
  description: string
  badge_unlock?: string
  badge_id?: string
  completed?: boolean
  progress?: string
}

export interface GamificationProgress {
  user_id: string
  xp: number
  level: number
  level_name: string
  next_level_xp: number
  badges_count: number
  tasks_completed: number
  simulations_run: number
  recent_actions: Array<{
    id: number
    action_type: string
    xp_gained: number
    details: string
    created_at: string
  }>
}

export interface QuizQuestion {
  id: string
  question: string
  options: string[]
  correct_index?: number
  explanation?: string
}

export interface Badge {
  id: string
  name: string
  category: string
  description: string
  icon: string
  earned: boolean
  earned_at?: string
}

export interface SyllabusUnit {
  id: string
  number: number
  title: string
  description: string
  topics: Array<{
    id: string
    title: string
    content: string
    key_takeaways: string[]
  }>
}
