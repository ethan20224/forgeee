export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface UserResponse {
  id: string
  email: string
  name: string | null
  created_at: string
  program_day: number
  season: number
  onboarded: boolean
  subscription_tier: string
}

export interface QuizSubmitRequest {
  goals: string[]
  routine_level: string
  daily_time: string
  timeline: string
  main_concern: string
  age_range: string
  has_photo: boolean
}

export interface PillarEstimate {
  pillar: string
  score: number
  label: string
}

export interface ScoreEstimateResponse {
  pillar_scores: PillarEstimate[]
  optimisation_score: number
  tier: string
  summary: string
}

export interface DailyTaskOut {
  id: string
  title: string
  category: string
  pillar: string
  tier: string
  why_it_works: string | null
  duration_mins: number | null
  day_number: number
  week_number: number | null
  xp_value: number
  is_completed: boolean
  completed_at: string | null
  library_task_id: string | null
}

export interface PlanDetail {
  id: string
  season: number
  program_name: string | null
  focus_summary: string | null
  honest_expectation: string | null
  created_at: string
  daily_tasks: DailyTaskOut[]
}

export interface GeneratePlanResponse {
  plan: PlanDetail
  from_cache: boolean
}

// --- Tasks ---

export interface TaskResponse {
  id: string
  title: string
  category: string
  pillar: string
  tier: string
  why_it_works: string | null
  duration_mins: number | null
  day_number: number
  week_number: number | null
  xp_value: number
  is_completed: boolean
  completed_at: string | null
}

export interface CompleteTaskResponse {
  task_id: string
  xp_earned: number
  streak_bonus: number
  total_xp: number
  new_streak: number
  level: number
  pillar_affected: string
  new_pillar_score: number
  streak_milestone: number | null
}

export interface HeatmapDay {
  day_number: number
  total_tasks: number
  completed_tasks: number
  completion_rate: number
  primary_pillar: string | null
}

export interface HeatmapResponse {
  days: HeatmapDay[]
  total_days: number
  overall_completion_rate: number
}

// --- Progress ---

export interface PillarScoreData {
  pillar: string
  label: string
  score: number
  delta_vs_baseline: number
  weight: number
}

export interface ProgressResponse {
  optimisation_score: number
  delta_vs_baseline: number
  current_streak: number
  longest_streak: number
  total_xp: number
  level: number
  pillar_scores: PillarScoreData[]
}

export interface PillarHistoryPoint {
  day_number: number
  score: number
}

export interface PillarDetailResponse {
  pillar: string
  label: string
  score: number
  delta_vs_baseline: number
  weight: number
  rank: number
  tasks_completed: number
  history: PillarHistoryPoint[]
}

// --- Coaching ---

export interface InsightResponse {
  stage: string
  context_type: string
  pillar: string | null
  message: string
  program_day: number
}

export interface PillarMovement {
  pillar: string
  label: string
  score: number
  delta: number
}

export interface WeeklyReportResponse {
  week_number: number
  season: number
  completion_rate: number
  completed_tasks: number
  total_tasks: number
  pillar_movements: PillarMovement[]
  coaching_note: string
  focus_next_week: string
  generated_at: string | null
}

export interface WeeklyReportSummary {
  week_number: number
  season: number
  completion_rate: number
  generated_at: string | null
}

export interface SeasonReportResponse {
  season: number
  opening: string
  biggest_mover: string
  needs_work: string
  next_focus: string
  score_start: number
  score_end: number
  score_delta: number
  total_tasks_completed: number
  completion_rate: number
  streak_best: number
}

// --- Common ---

export interface ApiError {
  detail: string
}
