import { create } from "zustand"
import type { PillarScoreData, ProgressResponse } from "@/types/api"
import { getProgress } from "@/api/progress"

interface ProgressState {
  optimisationScore: number
  deltaVsBaseline: number
  currentStreak: number
  longestStreak: number
  totalXp: number
  level: number
  pillarScores: PillarScoreData[]
  isLoading: boolean
  error: string | null

  fetchProgress: () => Promise<void>
  reset: () => void
}

const initialState = {
  optimisationScore: 50,
  deltaVsBaseline: 0,
  currentStreak: 0,
  longestStreak: 0,
  totalXp: 0,
  level: 1,
  pillarScores: [] as PillarScoreData[],
  isLoading: false,
  error: null as string | null,
}

export const useProgressStore = create<ProgressState>((set) => ({
  ...initialState,

  fetchProgress: async () => {
    set({ isLoading: true, error: null })
    try {
      const data: ProgressResponse = await getProgress()
      set({
        optimisationScore: data.optimisation_score,
        deltaVsBaseline: data.delta_vs_baseline,
        currentStreak: data.current_streak,
        longestStreak: data.longest_streak,
        totalXp: data.total_xp,
        level: data.level,
        pillarScores: data.pillar_scores,
        isLoading: false,
      })
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Failed to load progress"
      set({ error: msg, isLoading: false })
    }
  },

  reset: () => set(initialState),
}))
