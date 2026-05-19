import { api } from "./client"
import { saveTokens } from "@/store/authStorage"
import type { TokenResponse, UserResponse } from "@/types/api"

export async function signup(
  email: string,
  password: string,
  name?: string,
): Promise<TokenResponse> {
  const data = await api.postPublic<TokenResponse>("/auth/signup", {
    email,
    password,
    name: name || null,
  })
  await saveTokens(data.access_token, data.refresh_token)
  return data
}

export async function login(
  email: string,
  password: string,
): Promise<TokenResponse> {
  const data = await api.postPublic<TokenResponse>("/auth/login", {
    email,
    password,
  })
  await saveTokens(data.access_token, data.refresh_token)
  return data
}

export async function getMe(): Promise<UserResponse> {
  return api.get<UserResponse>("/auth/me")
}

export async function deleteAccount(): Promise<void> {
  return api.del("/auth/account")
}

export async function completeOnboarding(): Promise<UserResponse> {
  return api.post<UserResponse>("/auth/complete-onboarding")
}
