import { api } from "./client"
import type { ProgressResponse, PillarDetailResponse } from "@/types/api"

export async function getProgress(): Promise<ProgressResponse> {
  return api.get("/progress/")
}

export async function getPillarDetail(
  pillar: string,
): Promise<PillarDetailResponse> {
  return api.get(`/progress/pillar/${pillar}`)
}
