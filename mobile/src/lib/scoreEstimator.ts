import type { QuizSubmitRequest, PillarEstimate } from "@/types/api"

const PILLARS = [
  "skin",
  "hair",
  "grooming",
  "facial_composition",
  "posture",
  "style",
  "sleep",
  "nutrition",
  "voice",
]

const PILLAR_LABELS: Record<string, string> = {
  skin: "Skin",
  hair: "Hair",
  grooming: "Grooming",
  facial_composition: "Facial Composition",
  posture: "Posture",
  style: "Style",
  sleep: "Sleep",
  nutrition: "Nutrition",
  voice: "Voice",
}

const BASE = 50

const ROUTINE_SHIFT: Record<string, number> = {
  none: -15,
  basic: -5,
  moderate: 5,
  advanced: 12,
}

const TIME_BOOST: Record<string, number> = {
  "10min": -3,
  "20min": 0,
  "30min": 2,
  "45min": 4,
  "60min": 6,
}

const AGE_SKIN_HAIR: Record<string, number> = {
  "16-19": 6,
  "20-24": 4,
  "25-29": 2,
  "30-34": 0,
  "35-39": -2,
  "40+": -4,
}

const CONCERN_TO_PILLAR: Record<string, string[]> = {
  skin: ["skin"],
  hair: ["hair"],
  grooming: ["grooming"],
  style: ["style"],
  posture: ["posture"],
  overall: [],
}

const GOAL_BOOST = 5
const CONCERN_PENALTY = -8
const PHOTO_BONUS = 3

function clamp(value: number, lo = 0, hi = 100): number {
  return Math.max(lo, Math.min(hi, value))
}

export interface EstimatedScoreResult {
  pillarScores: PillarEstimate[]
  optimisationScore: number
  tier: string
  summary: string
}

export function estimateScoreFromQuiz(
  answers: QuizSubmitRequest,
): EstimatedScoreResult {
  const routineShift = ROUTINE_SHIFT[answers.routine_level] ?? 0
  const timeBoost = TIME_BOOST[answers.daily_time] ?? 0
  const ageAdj = AGE_SKIN_HAIR[answers.age_range] ?? 0
  const concernPillars = CONCERN_TO_PILLAR[answers.main_concern] ?? []

  const pillarScores: PillarEstimate[] = []
  let total = 0

  for (const pillar of PILLARS) {
    let score = BASE + routineShift + timeBoost

    if (answers.has_photo) score += PHOTO_BONUS
    if (answers.goals.includes(pillar)) score += GOAL_BOOST
    if (concernPillars.includes(pillar)) score += CONCERN_PENALTY
    if (answers.main_concern === "overall") score -= 3
    if (pillar === "skin" || pillar === "hair") score += ageAdj

    const clamped = clamp(score)
    pillarScores.push({
      pillar,
      score: clamped,
      label: PILLAR_LABELS[pillar] ?? pillar,
    })
    total += clamped
  }

  const optimisationScore =
    pillarScores.length > 0
      ? Math.round((total / pillarScores.length) * 100) / 100
      : 50

  let tier: string
  if (optimisationScore >= 70) tier = "advanced"
  else if (optimisationScore >= 45) tier = "intermediate"
  else tier = "beginner"

  const concernLabel =
    PILLAR_LABELS[answers.main_concern] ??
    answers.main_concern.charAt(0).toUpperCase() +
      answers.main_concern.slice(1)

  let summary: string
  if (tier === "advanced") {
    summary = `Strong foundation at ${Math.round(optimisationScore)}/100. Focus on ${concernLabel} refinement for your next season.`
  } else if (tier === "intermediate") {
    summary = `Solid base at ${Math.round(optimisationScore)}/100. Your ${concernLabel} area has the most room for growth.`
  } else {
    summary = `Starting at ${Math.round(optimisationScore)}/100. We'll build from ${concernLabel} fundamentals first.`
  }

  return { pillarScores, optimisationScore, tier, summary }
}
