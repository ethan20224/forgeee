import { api } from "./client"
import type {
  InsightResponse,
  WeeklyReportResponse,
  WeeklyReportSummary,
  SeasonReportResponse,
} from "@/types/api"

export async function getDailyInsight(): Promise<InsightResponse> {
  return api.get("/coaching/daily-insight")
}

export async function getWeeklyReport(
  week: number,
): Promise<WeeklyReportResponse> {
  return api.get(`/coaching/weekly-report/${week}`)
}

export async function getWeeklyReports(): Promise<WeeklyReportSummary[]> {
  return api.get("/coaching/weekly-reports")
}

export async function getSeasonReport(): Promise<SeasonReportResponse> {
  return api.get("/coaching/season-report")
}
