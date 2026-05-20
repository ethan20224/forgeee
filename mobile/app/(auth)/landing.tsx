import { useEffect } from "react"
import { View, Text, Pressable, StyleSheet } from "react-native"
import { SafeAreaView } from "react-native-safe-area-context"
import { useRouter } from "expo-router"
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withRepeat,
  withTiming,
  Easing,
} from "react-native-reanimated"
import { Colors, Typography, Spacing, Radius } from "@/constants/design"

export default function LandingScreen() {
  const router = useRouter()
  const breathe = useSharedValue(0)

  useEffect(() => {
    breathe.value = withRepeat(
      withTiming(1, { duration: 3500, easing: Easing.inOut(Easing.sin) }),
      -1,
      true,
    )
  }, [])

  const glowStyle = useAnimatedStyle(() => ({
    transform: [{ scale: 1 + breathe.value * 0.085 }],
    opacity: 0.10 + breathe.value * 0.04,
  }))

  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.container}>
        <View style={styles.hero}>
          <Animated.View style={[styles.glow, glowStyle]} />
          <Text style={styles.wordmark}>FORGE</Text>
          <Text style={styles.tagline}>
            Your appearance. Measured. Improved.
          </Text>
        </View>

        <View style={styles.actions}>
          <Pressable
            style={styles.primaryBtn}
            onPress={() => router.push("/(auth)/welcome" as never)}
          >
            <Text style={styles.primaryBtnText}>Create my program →</Text>
          </Pressable>

          <Pressable
            style={styles.secondaryBtn}
            onPress={() => router.push("/(auth)/signup?mode=login" as never)}
          >
            <Text style={styles.secondaryBtnText}>I already have an account</Text>
          </Pressable>
        </View>
      </View>
    </SafeAreaView>
  )
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: Colors.bg,
  },
  container: {
    flex: 1,
    justifyContent: "space-between",
    paddingHorizontal: Spacing.screen,
    paddingBottom: Spacing.xxxl,
  },
  hero: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    gap: 16,
  },
  glow: {
    position: "absolute",
    width: 280,
    height: 280,
    borderRadius: 140,
    backgroundColor: Colors.ember,
  },
  wordmark: {
    fontSize: Typography.sizes.display,
    fontWeight: Typography.weights.bold,
    letterSpacing: Typography.letterSpacing.widest,
    color: Colors.textPrimary,
  },
  tagline: {
    fontSize: Typography.sizes.caption,
    color: Colors.textSecond,
    textAlign: "center",
    letterSpacing: Typography.letterSpacing.wide,
  },
  actions: {
    gap: 12,
  },
  primaryBtn: {
    width: "100%",
    height: 52,
    borderRadius: Radius.full,
    backgroundColor: Colors.ember,
    alignItems: "center",
    justifyContent: "center",
  },
  primaryBtnText: {
    color: Colors.canvas,
    fontSize: Typography.sizes.caption,
    fontWeight: Typography.weights.bold,
  },
  secondaryBtn: {
    width: "100%",
    height: 52,
    borderRadius: Radius.full,
    borderWidth: 1,
    borderColor: Colors.emberBorder,
    backgroundColor: Colors.emberDim,
    alignItems: "center",
    justifyContent: "center",
  },
  secondaryBtnText: {
    color: Colors.ember,
    fontSize: Typography.sizes.caption,
    fontWeight: Typography.weights.bold,
  },
})
