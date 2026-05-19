import type { QuizSubmitRequest } from "@/types/api"

let cachedAnswers: QuizSubmitRequest | null = null

export function setCachedQuizAnswers(answers: QuizSubmitRequest): void {
  cachedAnswers = answers
}

export function getCachedQuizAnswers(): QuizSubmitRequest | null {
  return cachedAnswers
}

export function clearCachedQuizAnswers(): void {
  cachedAnswers = null
}
