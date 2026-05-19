import { useEffect } from "react"
import { View, ActivityIndicator } from "react-native"
import { useRouter } from "expo-router"
import { Colors } from "@/constants/design"

export default function QuizIndex() {
  const router = useRouter()

  useEffect(() => {
    router.replace("/(auth)/quiz/1" as never)
  }, [])

  return (
    <View
      style={{
        flex: 1,
        backgroundColor: Colors.bg,
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <ActivityIndicator color={Colors.ember} />
    </View>
  )
}
