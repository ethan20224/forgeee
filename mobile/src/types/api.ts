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

// --- Cycles ---

export interface UploadUrlResponse {
  upload_url: string
  object_key: string
  expires_in: number
}

export interface PillarScores {
  facial_composition_score: number | null
  skin_score: number | null
  grooming_score: number | null
  hair_score: number | null
  posture_score: number | null
  style_score: number | null
  sleep_score: number | null
  nutrition_score: number | null
  voice_score: number | null
}

export interface CycleAnalysisResponse {
  cycle_id: string
  cycle_number: number
  scan_mode: string
  scores: PillarScores
  face_shape: string | null
  ai_insight: string | null
  next_focus: string | null
  checked_in_at: string
}

export interface CycleHistoryItem {
  cycle_id: string
  cycle_number: number
  cycle_type: string
  face_shape: string | null
  optimisation_score: number | null
  checked_in_at: string
}

export interface CycleHistoryResponse {
  cycles: CycleHistoryItem[]
  total: number
}

export interface CycleCompareResponse {
  current: PillarScores
  previous: PillarScores
  deltas: Record<string, number | null>
  days_between: number
}

export interface EligibilityResponse {
  eligible: boolean
  next_eligible_at: string | null
  reason: string | null
  current_cycle_number: number
}

// --- Gamification ---

export interface BadgeResponse {
  badge_id: string
  name: string
  description: string
  icon: string
  category: string
  unlocked: boolean
  unlocked_at: string | null
}

export interface AchievementsResponse {
  badges: BadgeResponse[]
  total_unlocked: number
  total_available: number
}

export interface ChallengeResponse {
  id: string | null
  challenge_id: string
  name: string
  description: string
  icon: string
  target: number
  progress: number
  duration_days: number
  xp_reward: number
  status: string
  started_at: string | null
  pillar: string | null
}

export interface ChallengesListResponse {
  active: ChallengeResponse[]
  available: ChallengeResponse[]
  completed_count: number
}

export interface StreakInfoResponse {
  current_streak: number
  longest_streak: number
  milestones: number[]
  next_milestone: number | null
  streak_badges_unlocked: string[]
}

export interface XPInfoResponse {
  total_xp: number
  current_level: number
  level_name: string
  xp_progress: number
  xp_needed: number
  progress_pct: number
  xp_for_next_level: number | null
}

// --- Common ---

export interface ApiError {
  detail: string
}
