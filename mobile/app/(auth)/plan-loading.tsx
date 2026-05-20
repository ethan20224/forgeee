import { useEffect, useState } from "react"
import { View, Text, StyleSheet } from "react-native"
import Animated, {
  useSharedValue,
  withRepeat,
  withTiming,
  useAnimatedStyle,
  Easing,
  runOnJS,
} from "react-native-reanimated"
import { useRouter } from "expo-router"
import { Colors } from "@/constants/design"
import { setCachedPlan } from "@/lib/planCache"
import { getCachedQuizAnswers } from "@/lib/quizCache"
import * as quizApi from "@/api/quiz"
import * as plansApi from "@/api/plans"

const MESSAGES = [
  "Mapping your 9 pillars...",
  "Scanning 150+ tasks in the library...",
  "Calibrating to your goals...",
  "Building your 90-day arc...",
]

const MIN_DISPLAY_MS = 4000

export default function PlanLoadingScreen() {
  const router = useRouter()
  const [msgIdx, setMsgIdx] = useState(0)
  const [visibleIdx, setVisibleIdx] = useState(0)
  const [hasError, setHasError] = useState(false)
  const [errorMsg, setErrorMsg] = useState("")

  const rotation = useSharedValue(0)
  const spinStyle = useAnimatedStyle(() => ({
    transform: [{ rotate: `${rotation.value}deg` }],
  }))

  const msgOpacity = useSharedValue(1)
  const msgY = useSharedValue(0)
  const msgStyle = useAnimatedStyle(() => ({
    opacity: msgOpacity.value,
    transform: [{ translateY: msgY.value }],
  }))

  useEffect(() => {
    rotation.value = withRepeat(
      withTiming(360, { duration: 1500, easing: Easing.linear }),
      -1,
      false,
    )
  }, [])

  useEffect(() => {
    const iv = setInterval(
      () => setMsgIdx((m) => (m + 1) % MESSAGES.length),
      1500,
    )
    return () => clearInterval(iv)
  }, [])

  useEffect(() => {
    msgOpacity.value = withTiming(0, { duration: 150 })
    msgY.value = withTiming(-6, { duration: 150 }, () => {
      runOnJS(setVisibleIdx)(msgIdx)
      msgY.value = 6
      msgOpacity.value = withTiming(1, { duration: 200 })
      msgY.value = withTiming(0, { duration: 200 })
    })
  }, [msgIdx])

  useEffect(() => {
    loadPlan()
  }, [])

  async function loadPlan() {
    const answers = getCachedQuizAnswers()
    if (!answers) {
      setErrorMsg("Quiz answers could not be read. Please start over.")
      setHasError(true)
      return
    }

    try {
      const [planResponse] = await Promise.all([
        (async () => {
          await quizApi.submitQuiz(answers)
          return plansApi.generatePlan()
        })(),
        new Promise<void>((r) => setTimeout(r, MIN_DISPLAY_MS)),
      ])

      setCachedPlan(planResponse.plan)
      router.replace("/(auth)/plan-reveal" as never)
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Something went wrong."
      setErrorMsg(message)
      setHasError(true)
    }
  }

  if (hasError) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>{errorMsg}</Text>
        <Text
          style={styles.retryLink}
          onPress={() => router.replace("/(auth)/landing" as never)}
        >
          Start over
        </Text>
      </View>
    )
  }

  return (
    <View style={styles.container}>
      <Animated.View style={[styles.ring, spinStyle]} />
      <Animated.View style={msgStyle}>
        <Text style={styles.msgText}>{MESSAGES[visibleIdx]}</Text>
      </Animated.View>
      <Text style={styles.subText}>Personalised to your answers</Text>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.bg,
    alignItems: "center",
    justifyContent: "center",
    gap: 24,
  },
  ring: {
    width: 64,
    height: 64,
    borderRadius: 32,
    borderWidth: 3,
    borderColor: Colors.textTertiary,
    borderTopColor: Colors.ember,
  },
  msgText: {
    color: Colors.textPrimary,
    fontSize: 17,
    fontWeight: "700",
    textAlign: "center",
  },
  subText: { color: Colors.textSecond, fontSize: 11, textAlign: "center" },
  errorText: {
    color: Colors.textPrimary,
    fontSize: 13,
    textAlign: "center",
    lineHeight: 13 * 1.6,
    paddingHorizontal: 24,
  },
  retryLink: {
    color: Colors.ember,
    fontSize: 13,
    fontWeight: "700",
    marginTop: 12,
  },
})
