import { api } from "./client"
import type {
  QuizSubmitRequest,
  ScoreEstimateResponse,
} from "@/types/api"

export async function submitQuiz(
  answers: QuizSubmitRequest,
): Promise<{ id: string }> {
  return api.post("/quiz/submit", answers)
}

export async function getEstimatedScore(): Promise<ScoreEstimateResponse> {
  return api.get("/quiz/estimate-score")
}
