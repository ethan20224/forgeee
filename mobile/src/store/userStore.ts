import { create } from "zustand"
import { clearTokens } from "./authStorage"
import type { UserResponse } from "@/types/api"

interface UserState {
  user: UserResponse | null
  isAuthChecked: boolean

  setUser: (user: UserResponse | null) => void
  setAuthChecked: () => void
  signOut: () => Promise<void>
  reset: () => void
}

const initialState = {
  user: null as UserResponse | null,
  isAuthChecked: false,
}

export const useUserStore = create<UserState>((set) => ({
  ...initialState,

  setUser: (user) => set({ user }),

  setAuthChecked: () => set({ isAuthChecked: true }),

  signOut: async () => {
    await clearTokens()
    set(initialState)
  },

  reset: () => set(initialState),
}))
