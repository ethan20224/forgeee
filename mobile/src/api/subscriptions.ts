import { api } from "./client"

export interface SubscriptionStatus {
  tier: string
  provider: string
  expires_at: string | null
  is_active: boolean
  can_access_premium: boolean
}

export async function getSubscriptionStatus(): Promise<SubscriptionStatus> {
  return api.get("/subscriptions/status")
}
