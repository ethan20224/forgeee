import type { PlanDetail } from "@/types/api"
import type { EstimatedScoreResult } from "./scoreEstimator"

let cachedPlan: PlanDetail | null = null
let cachedEstimatedScore: EstimatedScoreResult | null = null

export function setCachedPlan(plan: PlanDetail): void {
  cachedPlan = plan
}

export function getCachedPlan(): PlanDetail | null {
  return cachedPlan
}

export function clearCachedPlan(): void {
  cachedPlan = null
}

export function setCachedEstimatedScore(
  score: EstimatedScoreResult,
): void {
  cachedEstimatedScore = score
}

export function getCachedEstimatedScore(): EstimatedScoreResult | null {
  return cachedEstimatedScore
}

export function clearCachedEstimatedScore(): void {
  cachedEstimatedScore = null
}
