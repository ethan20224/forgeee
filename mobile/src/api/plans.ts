import { api } from "./client"
import type { GeneratePlanResponse, PlanDetail } from "@/types/api"

export async function generatePlan(): Promise<GeneratePlanResponse> {
  return api.post("/plans/generate")
}

export async function getCurrentPlan(): Promise<PlanDetail> {
  return api.get("/plans/current")
}

export async function getPlan(planId: string): Promise<PlanDetail> {
  return api.get(`/plans/${planId}`)
}
