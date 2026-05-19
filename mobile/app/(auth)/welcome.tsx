import { useState, useRef } from "react"
import { View, Text, ScrollView, StyleSheet } from "react-native"
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withTiming,
  Easing,
  runOnJS,
} from "react-native-reanimated"
import { SafeAreaView } from "react-native-safe-area-context"
import { useRouter } from "expo-router"
import { Feather } from "@expo/vector-icons"
import { Colors } from "@/constants/design"
import { PrimaryButton } from "@/components/ui/PrimaryButton"
import { ForgeCard } from "@/components/ui/ForgeCard"

const SLIDES = [
  {
    label: "THE TRUTH",
    headline: "Your appearance is measurable. And improvable.",
    body: "9 pillars. 90 days. A system designed around how your body actually changes.",
    cta: "Show me the system \u2192",
  },
  {
    label: "THE SCIENCE",
    headline: "Your skin renews every 28 days. Habits take 66 days to stick.",
    body: "Our program is built around those exact timelines. Not around what looks impressive in an ad.",
    cta: "Makes sense \u2192",
  },
  {
    label: "WHAT WE CAN CHANGE",
    headline: "Your appearance. Measured. Improved. Recorded.",
    body: "",
    cta: "Build my program \u2192",
  },
]

export default function WelcomeSlides() {
  const router = useRouter()
  const [slide, setSlide] = useState(0)
  const [visibleSlide, setVisibleSlide] = useState(0)
  const isAnimating = useRef(false)

  const opacity = useSharedValue(1)
  const translateX = useSharedValue(0)
  const animStyle = useAnimatedStyle(() => ({
    opacity: opacity.value,
    transform: [{ translateX: translateX.value }],
  }))

  function goToSlide(next: number) {
    if (isAnimating.current) return
    isAnimating.current = true
    opacity.value = withTiming(0, {
      duration: 150,
      easing: Easing.out(Easing.quad),
    })
    translateX.value = withTiming(
      -30,
      { duration: 150, easing: Easing.out(Easing.quad) },
      () => runOnJS(applySlide)(next),
    )
  }

  function applySlide(next: number) {
    setVisibleSlide(next)
    setSlide(next)
    translateX.value = 30
    opacity.value = withTiming(1, {
      duration: 200,
      easing: Easing.out(Easing.quad),
    })
    translateX.value = withTiming(
      0,
      { duration: 200, easing: Easing.out(Easing.quad) },
      () => runOnJS(finishAnim)(),
    )
  }

  function finishAnim() {
    isAnimating.current = false
  }

  function next() {
    if (slide < SLIDES.length - 1) goToSlide(slide + 1)
    else router.replace("/(auth)/quiz" as never)
  }

  const current = SLIDES[visibleSlide]

  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.dotsRow}>
        {SLIDES.map((_, i) => (
          <View
            key={i}
            style={[
              styles.dot,
              i === slide ? styles.dotActive : styles.dotInactive,
            ]}
          />
        ))}
      </View>

      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}
      >
        <Animated.View style={animStyle}>
          <Text style={styles.label}>{current.label}</Text>
          <Text style={styles.headline}>{current.headline}</Text>
          {current.body ? (
            <Text style={styles.body}>{current.body}</Text>
          ) : null}
          {visibleSlide === 0 && <Slide0 />}
          {visibleSlide === 1 && <Slide1 />}
          {visibleSlide === 2 && <Slide2 />}
        </Animated.View>
      </ScrollView>

      <View style={styles.footer}>
        <PrimaryButton onPress={next}>{current.cta}</PrimaryButton>
      </View>
    </SafeAreaView>
  )
}

function Slide0() {
  const pillars = [
    { label: "Skin" },
    { label: "Grooming" },
    { label: "Posture" },
  ]
  return (
    <View style={{ gap: 8, marginTop: 8 }}>
      {pillars.map(({ label }) => (
        <ForgeCard key={label} style={s0.row}>
          <View style={s0.check}>
            <Feather
              name="check"
              size={10}
              color={Colors.iconOnLight}
              strokeWidth={3}
            />
          </View>
          <View style={{ flex: 1 }}>
            <Text style={s0.pillarLabel}>{label}</Text>
          </View>
          <View style={s0.badge}>
            <Text style={s0.badgeText}>TRAINABLE</Text>
          </View>
        </ForgeCard>
      ))}
    </View>
  )
}

const s0 = StyleSheet.create({
  row: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    padding: 14,
    paddingHorizontal: 16,
  },
  check: {
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: Colors.ember,
    alignItems: "center",
    justifyContent: "center",
    flexShrink: 0,
  },
  pillarLabel: {
    color: Colors.textPrimary,
    fontSize: 13,
    fontWeight: "700",
  },
  badge: {
    backgroundColor: Colors.emberDim,
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 999,
  },
  badgeText: {
    color: Colors.ember,
    fontSize: 9,
    fontWeight: "700",
    letterSpacing: 1.2,
  },
})

function Slide1() {
  const rings = [
    { size: 180, opacity: 0.15 },
    { size: 130, opacity: 0.25 },
    { size: 80, opacity: 0.5 },
  ]
  return (
    <View style={{ alignItems: "center", marginTop: 24 }}>
      <View
        style={{
          width: 180,
          height: 180,
          position: "relative",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        {rings.map(({ size, opacity: op }) => (
          <View
            key={size}
            style={{
              position: "absolute",
              width: size,
              height: size,
              borderRadius: size / 2,
              borderWidth: 1.5,
              borderColor: Colors.ember,
              opacity: op,
              top: (180 - size) / 2,
              left: (180 - size) / 2,
            }}
          />
        ))}
        <View style={{ alignItems: "center" }}>
          <Text
            style={{
              color: Colors.ember,
              fontSize: 17,
              fontWeight: "700",
            }}
          >
            90
          </Text>
          <Text
            style={{
              color: Colors.textSecond,
              fontSize: 11,
              marginTop: 2,
            }}
          >
            Days
          </Text>
        </View>
      </View>
    </View>
  )
}

function Slide2() {
  const locked = ["Bone structure", "Facial geometry", "Genetics"]
  const optimise = ["Skin", "Grooming", "Style", "Frame"]
  return (
    <View style={{ marginTop: 8, gap: 16 }}>
      <View>
        <Text style={s2.sectionLabel}>{"WHAT WE CAN'T CHANGE"}</Text>
        <View style={{ gap: 6, marginTop: 8 }}>
          {locked.map((item) => (
            <View
              key={item}
              style={{
                flexDirection: "row",
                alignItems: "center",
                gap: 10,
                opacity: 0.4,
              }}
            >
              <Feather name="lock" size={12} color={Colors.textTertiary} />
              <Text style={{ fontSize: 13, color: Colors.textTertiary }}>
                {item}
              </Text>
            </View>
          ))}
        </View>
      </View>
      <View>
        <Text style={[s2.sectionLabel, { color: Colors.ember }]}>
          WHAT WE CAN OPTIMIZE
        </Text>
        <View style={{ gap: 6, marginTop: 8 }}>
          {optimise.map((item) => (
            <View key={item} style={s2.optimiseRow}>
              <Feather name="check" size={12} color={Colors.ember} />
              <Text style={{ fontSize: 13, color: Colors.textPrimary }}>
                {item}
              </Text>
            </View>
          ))}
        </View>
      </View>
    </View>
  )
}

const s2 = StyleSheet.create({
  sectionLabel: {
    fontSize: 9,
    fontWeight: "700",
    letterSpacing: 1.2,
    textTransform: "uppercase",
    color: Colors.textTertiary,
  },
  optimiseRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    backgroundColor: Colors.accentSubtle,
    borderRadius: 8,
    padding: 10,
    paddingHorizontal: 12,
  },
})

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: Colors.bg },
  dotsRow: {
    flexDirection: "row",
    justifyContent: "center",
    gap: 6,
    paddingTop: 20,
    paddingBottom: 32,
  },
  dot: { height: 6, borderRadius: 999 },
  dotActive: { width: 16, backgroundColor: Colors.ember },
  dotInactive: { width: 6, backgroundColor: "rgba(255,255,255,0.2)" },
  scroll: { flex: 1 },
  content: { paddingHorizontal: 24, paddingBottom: 140 },
  label: {
    color: Colors.ember,
    fontSize: 9,
    fontWeight: "700",
    letterSpacing: 1.2,
    textTransform: "uppercase",
    marginBottom: 12,
  },
  headline: {
    color: Colors.textPrimary,
    fontSize: 24,
    fontWeight: "700",
    lineHeight: 24 * 1.2,
    marginBottom: 12,
  },
  body: {
    color: Colors.textSecond,
    fontSize: 13,
    lineHeight: 13 * 1.6,
    marginBottom: 8,
  },
  footer: {
    position: "absolute",
    bottom: 32,
    left: 24,
    right: 24,
    gap: 12,
  },
})
