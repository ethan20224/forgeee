import { useEffect } from "react"
import { Stack, router } from "expo-router"
import { Colors } from "@/constants/design"
import { useUserStore } from "@/store/userStore"
import { getTokens } from "@/store/authStorage"
import { getMe } from "@/api/auth"

export default function RootLayout() {
  const setUser = useUserStore((s) => s.setUser)
  const setAuthChecked = useUserStore((s) => s.setAuthChecked)

  useEffect(() => {
    checkAuth()
  }, [])

  async function checkAuth() {
    try {
      const { accessToken } = await getTokens()
      if (!accessToken) {
        setAuthChecked()
        return
      }

      const user = await getMe()
      setUser(user)
      setAuthChecked()

      if (user.onboarded) {
        router.replace("/(app)/(tabs)" as never)
      }
    } catch {
      setAuthChecked()
    }
  }

  return (
    <Stack
      screenOptions={{
        headerShown: false,
        contentStyle: { backgroundColor: Colors.bg },
      }}
    />
  )
}
