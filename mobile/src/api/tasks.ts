import { api } from "./client"
import type {
  TaskResponse,
  CompleteTaskResponse,
  HeatmapResponse,
} from "@/types/api"

export async function getTodaysTasks(): Promise<TaskResponse[]> {
  return api.get("/tasks/today")
}

export async function completeTask(
  taskId: string,
): Promise<CompleteTaskResponse> {
  return api.post(`/tasks/${taskId}/complete`)
}

export async function getHeatmap(): Promise<HeatmapResponse> {
  return api.get("/tasks/heatmap")
}
