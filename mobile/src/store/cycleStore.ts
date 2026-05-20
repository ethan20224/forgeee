import { create } from "zustand"
import type {
  CycleAnalysisResponse,
  CycleHistoryItem,
  EligibilityResponse,
} from "@/types/api"
import {
  checkEligibility,
  getCycleHistory,
  analyseCycle,
  getUploadUrl,
  uploadPhotoToR2,
} from "@/api/cycles"

interface CycleState {
  eligibility: EligibilityResponse | null
  latestAnalysis: CycleAnalysisResponse | null
  history: CycleHistoryItem[]
  historyTotal: number
  loading: boolean
  analysing: boolean
  error: string | null

  fetchEligibility: () => Promise<void>
  fetchHistory: () => Promise<void>
  submitCheckin: (photoUri: string, scanMode?: string) => Promise<CycleAnalysisResponse>
  reset: () => void
}

export const useCycleStore = create<CycleState>((set, get) => ({
  eligibility: null,
  latestAnalysis: null,
  history: [],
  historyTotal: 0,
  loading: false,
  analysing: false,
  error: null,

  fetchEligibility: async () => {
    set({ loading: true, error: null })
    try {
      const eligibility = await checkEligibility()
      set({ eligibility, loading: false })
    } catch (e: any) {
      set({ error: e.message || "Failed to check eligibility", loading: false })
    }
  },

  fetchHistory: async () => {
    set({ loading: true, error: null })
    try {
      const response = await getCycleHistory()
      set({ history: response.cycles, historyTotal: response.total, loading: false })
    } catch (e: any) {
      set({ error: e.message || "Failed to fetch history", loading: false })
    }
  },

  submitCheckin: async (photoUri: string, scanMode: string = "face") => {
    set({ analysing: true, error: null })
    try {
      const { upload_url, object_key } = await getUploadUrl("front", scanMode)
      await uploadPhotoToR2(upload_url, photoUri)
      const analysis = await analyseCycle(object_key, scanMode)
      set({ latestAnalysis: analysis, analysing: false })
      get().fetchHistory()
      get().fetchEligibility()
      return analysis
    } catch (e: any) {
      set({ error: e.message || "Analysis failed", analysing: false })
      throw e
    }
  },

  reset: () => {
    set({
      eligibility: null,
      latestAnalysis: null,
      history: [],
      historyTotal: 0,
      loading: false,
      analysing: false,
      error: null,
    })
  },
}))
