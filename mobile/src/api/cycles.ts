import { api } from "./client"
import type {
  UploadUrlResponse,
  CycleAnalysisResponse,
  CycleHistoryResponse,
  CycleCompareResponse,
  EligibilityResponse,
} from "@/types/api"

export async function getUploadUrl(
  angle: string = "front",
  scanMode: string = "face",
): Promise<UploadUrlResponse> {
  return api.post("/cycles/upload-url", { angle, scan_mode: scanMode })
}

export async function checkEligibility(): Promise<EligibilityResponse> {
  return api.get("/cycles/eligibility")
}

export async function analyseCycle(
  objectKey: string,
  scanMode: string = "face",
): Promise<CycleAnalysisResponse> {
  return api.post("/cycles/analyse", { object_key: objectKey, scan_mode: scanMode })
}

export async function getCycleHistory(
  limit: number = 20,
  offset: number = 0,
): Promise<CycleHistoryResponse> {
  return api.get(`/cycles/history?limit=${limit}&offset=${offset}`)
}

export async function getCycleDetail(cycleId: string): Promise<CycleAnalysisResponse> {
  return api.get(`/cycles/${cycleId}`)
}

export async function compareCycles(
  currentId: string,
  previousId: string,
): Promise<CycleCompareResponse> {
  return api.get(`/cycles/compare/${currentId}/${previousId}`)
}

export async function uploadPhotoToR2(
  uploadUrl: string,
  photoUri: string,
): Promise<void> {
  const response = await fetch(photoUri)
  const blob = await response.blob()

  await fetch(uploadUrl, {
    method: "PUT",
    headers: { "Content-Type": "image/jpeg" },
    body: blob,
  })
}
