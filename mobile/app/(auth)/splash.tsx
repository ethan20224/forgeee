import { useEffect, useRef, useState } from "react"
import { View, Text, StyleSheet } from "react-native"
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withTiming,
} from "react-native-reanimated"
import { useRouter } from "expo-router"
import { Colors } from "@/constants/design"
import { useUserStore } from "@/store/userStore"

export default function SplashScreen() {
  const router = useRouter()
  const [pct, setPct] = useState(0)
  const barWidth = useSharedValue(0)
  const hasNavigated = useRef(false)
  const isAuthChecked = useUserStore((s) => s.isAuthChecked)

  const tryNavigate = () => {
    if (hasNavigated.current) return
    const { isAuthChecked: checked, user } = useUserStore.getState()
    if (!checked) return
    hasNavigated.current = true
    if (user?.onboarded) {
      router.replace("/(app)/(tabs)" as never)
    } else {
      router.replace("/(auth)/welcome" as never)
    }
  }

  useEffect(() => {
    if (isAuthChecked) tryNavigate()
  }, [isAuthChecked])

  const barStyle = useAnimatedStyle(() => ({
    width: `${barWidth.value}%` as `${number}%`,
  }))

  useEffect(() => {
    const start = setTimeout(() => {
      let current = 0
      const interval = setInterval(() => {
        current = Math.min(current + 2, 100)
        setPct(current)
        barWidth.value = withTiming(current, { duration: 30 })
        if (current >= 100) {
          clearInterval(interval)
          setTimeout(() => {
            tryNavigate()
            if (!hasNavigated.current) {
              hasNavigated.current = true
              router.replace("/(auth)/welcome" as never)
            }
          }, 300)
        }
      }, 40)
      return () => clearInterval(interval)
    }, 200)
    return () => clearTimeout(start)
  }, [])

  return (
    <View style={styles.container}>
      <View style={styles.glow} />
      <Text style={styles.wordmark}>FORGE</Text>
      <View style={styles.barWrapper}>
        <View style={styles.track}>
          <Animated.View style={[styles.fill, barStyle]} />
        </View>
        <View style={styles.barLabels}>
          <Text style={styles.barText}>Calibrating algorithms...</Text>
          <Text style={styles.barText}>{pct}%</Text>
        </View>
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.bg,
    alignItems: "center",
    justifyContent: "center",
    gap: 40,
  },
  glow: {
    position: "absolute",
    width: 280,
    height: 280,
    borderRadius: 140,
    backgroundColor: Colors.emberDim,
  },
  wordmark: {
    fontSize: 32,
    fontWeight: "700",
    letterSpacing: 4,
    color: Colors.textPrimary,
  },
  barWrapper: { width: 180, gap: 6 },
  track: {
    height: 2,
    borderRadius: 999,
    backgroundColor: Colors.textTertiary,
    overflow: "hidden",
  },
  fill: {
    height: "100%",
    backgroundColor: Colors.ember,
    borderRadius: 999,
  },
  barLabels: {
    flexDirection: "row",
    justifyContent: "space-between",
  },
  barText: {
    fontSize: 9,
    color: Colors.textTertiary,
    letterSpacing: 0.5,
  },
})
