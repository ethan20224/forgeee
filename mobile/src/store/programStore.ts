import { create } from "zustand"
import type { TaskResponse, PlanDetail } from "@/types/api"
import { getTodaysTasks, completeTask as apiCompleteTask } from "@/api/tasks"
import { getCurrentPlan } from "@/api/plans"

interface ProgramState {
  plan: PlanDetail | null
  todaysTasks: TaskResponse[]
  isLoadingTasks: boolean
  isLoadingPlan: boolean
  error: string | null

  fetchPlan: () => Promise<void>
  fetchTodaysTasks: () => Promise<void>
  completeTask: (taskId: string) => Promise<void>
  reset: () => void
}

const initialState = {
  plan: null as PlanDetail | null,
  todaysTasks: [] as TaskResponse[],
  isLoadingTasks: false,
  isLoadingPlan: false,
  error: null as string | null,
}

export const useProgramStore = create<ProgramState>((set, get) => ({
  ...initialState,

  fetchPlan: async () => {
    set({ isLoadingPlan: true, error: null })
    try {
      const plan = await getCurrentPlan()
      set({ plan, isLoadingPlan: false })
    } catch {
      set({ isLoadingPlan: false })
    }
  },

  fetchTodaysTasks: async () => {
    set({ isLoadingTasks: true, error: null })
    try {
      const tasks = await getTodaysTasks()
      set({ todaysTasks: tasks, isLoadingTasks: false })
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Failed to load tasks"
      set({ error: msg, isLoadingTasks: false })
    }
  },

  completeTask: async (taskId: string) => {
    try {
      await apiCompleteTask(taskId)
      set((state) => ({
        todaysTasks: state.todaysTasks.map((t) =>
          t.id === taskId
            ? { ...t, is_completed: true, completed_at: new Date().toISOString() }
            : t,
        ),
      }))
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Failed to complete task"
      set({ error: msg })
    }
  },

  reset: () => set(initialState),
}))
