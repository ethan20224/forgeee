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

export interface ApiError {
  detail: string
}
