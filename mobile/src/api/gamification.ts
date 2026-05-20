import { api } from "./client"
import type {
  AchievementsResponse,
  ChallengesListResponse,
  ChallengeResponse,
  StreakInfoResponse,
  XPInfoResponse,
} from "@/types/api"

export async function getAchievements(): Promise<AchievementsResponse> {
  return api.get("/gamification/achievements")
}

export async function getChallenges(): Promise<ChallengesListResponse> {
  return api.get("/gamification/challenges")
}

export async function startChallenge(challengeId: string): Promise<ChallengeResponse> {
  return api.post("/gamification/challenges/start", { challenge_id: challengeId })
}

export async function getStreakInfo(): Promise<StreakInfoResponse> {
  return api.get("/gamification/streak")
}

export async function getXPInfo(): Promise<XPInfoResponse> {
  return api.get("/gamification/xp")
}
