import { useEffect, useState } from "react"
import { View, Text, ScrollView, StyleSheet } from "react-native"
import { SafeAreaView } from "react-native-safe-area-context"
import Animated, {
  useSharedValue,
  withTiming,
  withSpring,
  useAnimatedStyle,
} from "react-native-reanimated"
import { useRouter } from "expo-router"
import { Colors, Spacing, Typography, Radius } from "@/constants/design"
import { getCachedPlan, getCachedEstimatedScore } from "@/lib/planCache"
import { getCachedQuizAnswers } from "@/lib/quizCache"
import { useUserStore } from "@/store/userStore"
import * as authApi from "@/api/auth"
import { PHASE_DISPLAY, type PhaseId } from "@/constants/phases"

const PHASE_ORDER: PhaseId[] = ["foundation", "activation", "optimisation"]

const DAILY_TIME_READABLE: Record<string, string> = {
  "10min": "10 min/day",
  "20min": "20 min/day",
  "30min": "30 min/day",
  "45min": "45 min/day",
  "60min": "60 min/day",
}

const TIMELINE_READABLE: Record<string, string> = {
  "30days": "30 days",
  "60days": "60 days",
  "90days": "90 days",
}

const CONCERN_READABLE: Record<string, string> = {
  skin: "skin",
  grooming: "grooming",
  hair: "hair",
  style: "style",
  posture: "posture",
  overall: "overall improvement",
}

const DEFAULT_IMPROVEMENTS = [
  "Clearer, smoother skin",
  "Sharper, more defined grooming",
  "Less facial puffiness",
  "Better sleep habits",
  "A system you can actually stick to",
]

const FOCUS_TO_IMPROVEMENTS: Record<string, string[]> = {
  skin: [
    "Clearer, smoother skin",
    "Less facial puffiness",
    "A more even complexion",
  ],
  grooming: [
    "Sharper, more defined grooming",
    "Cleaner facial hair lines",
    "Better product results",
  ],
  hair: [
    "Healthier-looking hair",
    "Better styling control",
    "Thicker appearance",
  ],
  style: [
    "Clothes that fit your frame better",
    "A clear personal style direction",
    "Confidence in what you wear",
  ],
  posture: [
    "Better posture naturally",
    "Standing taller without thinking",
    "Less shoulder tension",
  ],
}

export default function PlanRevealScreen() {
  const router = useRouter()
  const setUser = useUserStore((s) => s.setUser)
  const plan = getCachedPlan()
  const estimatedScore = getCachedEstimatedScore()
  const quizAnswers = getCachedQuizAnswers()
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const opacity = useSharedValue(0)
  const translateY = useSharedValue(40)
  const entryStyle = useAnimatedStyle(() => ({
    opacity: opacity.value,
    transform: [{ translateY: translateY.value }],
  }))

  useEffect(() => {
    opacity.value = withTiming(1, { duration: 300 })
    translateY.value = withSpring(0, { damping: 20, stiffness: 120 })
  }, [])

  const handleStartTransformation = async () => {
    if (!plan) {
      setError("Plan not found. Please go back and try again.")
      return
    }

    setIsSaving(true)
    setError(null)

    try {
      const updatedUser = await authApi.completeOnboarding()
      setUser(updatedUser)
      setIsSaving(false)
      router.replace("/(app)/(tabs)" as never)
    } catch (err) {
      setIsSaving(false)
      const message =
        err instanceof Error
          ? err.message
          : "Could not save your plan. Please try again."
      setError(message)
    }
  }

  const programName = plan?.program_name ?? "Barrier & Clarity Protocol"
  const focusAreas =
    plan?.focus_summary ??
    "skin clarity, grooming consistency, and physical frame"

  function getImprovements(): string[] {
    if (quizAnswers?.main_concern) {
      const mapped = FOCUS_TO_IMPROVEMENTS[quizAnswers.main_concern]
      if (mapped && mapped.length >= 3) return mapped.slice(0, 5)
    }
    return DEFAULT_IMPROVEMENTS
  }

  const improvements = getImprovements()

  return (
    <SafeAreaView style={styles.safe}>
      <Animated.View style={[{ flex: 1 }, entryStyle]}>
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          <Text style={styles.eyebrow}>YOUR PROGRAM IS READY</Text>

          {estimatedScore && (
            <View style={styles.scoreBanner}>
              <Text style={styles.scoreBannerLabel}>
                STARTING FORGE SCORE
              </Text>
              <Text style={styles.scoreBannerValue}>
                {Math.round(estimatedScore.optimisationScore)}
                <Text style={styles.scoreBannerMax}>/100</Text>
              </Text>
              <Text style={styles.scoreBannerSub}>
                Your real score unlocks on day 3 with your baseline photo
              </Text>
            </View>
          )}

          <Text style={styles.sectionTitle}>Your Programme</Text>
          <Text style={styles.programName}>{programName}</Text>
          <Text style={styles.programMeta}>90 days. Daily tasks.</Text>
          <Text style={styles.programFocus}>
            Built around your answers \u2014 targeting {focusAreas}.
          </Text>

          {quizAnswers && (
            <View style={styles.chipsRow}>
              {quizAnswers.main_concern && (
                <View style={styles.chip}>
                  <Text style={styles.chipText}>
                    {CONCERN_READABLE[quizAnswers.main_concern] ??
                      quizAnswers.main_concern}
                  </Text>
                </View>
              )}
              {quizAnswers.daily_time && (
                <View style={styles.chip}>
                  <Text style={styles.chipText}>
                    {DAILY_TIME_READABLE[quizAnswers.daily_time] ??
                      quizAnswers.daily_time}
                  </Text>
                </View>
              )}
              {quizAnswers.timeline && (
                <View style={styles.chip}>
                  <Text style={styles.chipText}>
                    {TIMELINE_READABLE[quizAnswers.timeline] ??
                      quizAnswers.timeline}
                  </Text>
                </View>
              )}
            </View>
          )}

          <View style={styles.sectionGap} />
          <Text style={styles.sectionTitle}>
            What This Programme Will Improve
          </Text>
          <View style={styles.improvementList}>
            {improvements.map((item) => (
              <View key={item} style={styles.improvementRow}>
                <Text style={styles.checkMark}>{"\u2713"}</Text>
                <Text style={styles.improvementText}>{item}</Text>
              </View>
            ))}
          </View>

          <View style={styles.sectionGap} />
          <View style={styles.cantChangeBox}>
            <Text style={styles.sectionTitle}>
              {"What FORGE Can\u2019t Change"}
            </Text>
            <View style={styles.limitationList}>
              {[
                "Bone structure \u2014 your jaw and cheekbone shape",
                "Height",
                "Hairline position",
                "Eye or nose shape",
              ].map((item) => (
                <View key={item} style={styles.improvementRow}>
                  <Text style={styles.crossMark}>{"\u00d7"}</Text>
                  <Text style={styles.limitationText}>{item}</Text>
                </View>
              ))}
            </View>
            <Text style={styles.cantChangeFooter}>
              Everything listed above can measurably improve in 90 days.
              Your programme targets what{"'"}s actually within reach.
            </Text>
          </View>

          <View style={styles.sectionGap} />
          <Text style={styles.sectionTitle}>What To Expect</Text>

          <View style={styles.timelineItem}>
            <Text style={styles.timelineLabel}>After 7 days:</Text>
            <Text style={styles.timelineBody}>
              Grooming edges are cleaner. People might notice something is
              different but not know what.
            </Text>
          </View>

          <View style={styles.timelineItem}>
            <Text style={styles.timelineLabel}>After 28 days:</Text>
            <Text style={styles.timelineBody}>
              Skin is measurably clearer. Every cell on your face is new.
              The base is built.
            </Text>
          </View>

          <View style={styles.timelineItem}>
            <Text style={styles.timelineLabel}>After 90 days:</Text>
            <Text style={styles.timelineBody}>
              Compound results. Skin, grooming, posture, style \u2014
              everything shows at once. This is the transformation point.
            </Text>
          </View>

          <View style={styles.timelineItem}>
            <Text style={styles.timelineWarning}>NOT after 90 days:</Text>
            <Text style={styles.timelineBody}>
              Permanent structural change. That takes Season 2 and beyond.
              This is the foundation.
            </Text>
          </View>

          <View style={styles.sectionGap} />
          <Text style={styles.sectionTitle}>Your Roadmap</Text>
          {PHASE_ORDER.map((phaseId, index) => {
            const phase = PHASE_DISPLAY[phaseId]
            return (
              <View key={phaseId} style={styles.phaseCard}>
                <View style={styles.phaseHeader}>
                  <Text style={styles.phaseNumber}>{index + 1}</Text>
                  <View>
                    <Text style={styles.phaseName}>
                      Phase {index + 1}: {phase.name}
                    </Text>
                    <Text style={styles.phaseRange}>{phase.range}</Text>
                  </View>
                </View>
                <Text style={styles.phaseTagline}>{phase.tagline}</Text>
              </View>
            )
          })}

          <View style={{ height: Spacing.xxxl }} />
        </ScrollView>

        <View style={styles.footer}>
          {error && (
            <View style={styles.errorContainer}>
              <Text style={styles.errorText}>{error}</Text>
              <Text style={styles.retryText}>
                Tap the button to try again
              </Text>
            </View>
          )}
          <Animated.View
            style={[styles.ctaOuter, isSaving && styles.ctaDisabled]}
          >
            <Animated.View
              style={styles.ctaInner}
              pointerEvents={isSaving ? "none" : "auto"}
              onTouchEnd={isSaving ? undefined : handleStartTransformation}
            >
              <Text style={styles.ctaText}>
                {isSaving ? "Saving..." : "Start Day 1 →"}
              </Text>
            </Animated.View>
          </Animated.View>
        </View>
      </Animated.View>
    </SafeAreaView>
  )
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: Colors.bg },
  scrollContent: {
    paddingHorizontal: Spacing.xl,
    paddingTop: Spacing.xxl,
    paddingBottom: Spacing.xl,
  },
  eyebrow: {
    color: Colors.ember,
    fontSize: Typography.sizes.nano,
    fontWeight: "700",
    letterSpacing: 1.2,
    textTransform: "uppercase",
    marginBottom: Spacing.lg,
  },
  sectionTitle: {
    color: Colors.bone,
    fontSize: Typography.sizes.title,
    fontWeight: "700",
    lineHeight: Typography.sizes.title * Typography.lineHeights.tight,
    marginBottom: Spacing.md,
  },
  sectionGap: { height: Spacing.xl },
  programName: {
    color: Colors.bone,
    fontSize: Typography.sizes.title,
    fontWeight: "700",
    lineHeight: Typography.sizes.title * Typography.lineHeights.normal,
    marginBottom: Spacing.sm,
  },
  programMeta: {
    color: Colors.ash,
    fontSize: Typography.sizes.caption,
    fontWeight: "400",
    lineHeight: Typography.sizes.caption * Typography.lineHeights.relaxed,
    marginBottom: Spacing.sm,
  },
  programFocus: {
    color: Colors.ash,
    fontSize: Typography.sizes.caption,
    fontWeight: "400",
    lineHeight: Typography.sizes.caption * Typography.lineHeights.relaxed,
  },
  scoreBanner: {
    backgroundColor: Colors.surface,
    borderWidth: 1,
    borderColor: Colors.border,
    borderRadius: Radius.card,
    padding: Spacing.lg,
    alignItems: "center",
    marginBottom: Spacing.xl,
  },
  scoreBannerLabel: {
    color: Colors.ember,
    fontSize: Typography.sizes.nano,
    fontWeight: "700",
    letterSpacing: 1.2,
    textTransform: "uppercase",
    marginBottom: Spacing.sm,
  },
  scoreBannerValue: {
    color: Colors.bone,
    fontSize: Typography.sizes.display,
    fontWeight: "700",
    lineHeight: Typography.sizes.display * Typography.lineHeights.tight,
  },
  scoreBannerMax: {
    color: Colors.ash,
    fontSize: Typography.sizes.title,
    fontWeight: "400",
  },
  scoreBannerSub: {
    color: Colors.ash,
    fontSize: Typography.sizes.label,
    fontWeight: "400",
    textAlign: "center",
    marginTop: Spacing.sm,
    lineHeight: Typography.sizes.label * Typography.lineHeights.relaxed,
  },
  chipsRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: Spacing.sm,
    marginTop: Spacing.md,
  },
  chip: {
    backgroundColor: Colors.surface,
    borderWidth: 1,
    borderColor: Colors.border,
    borderRadius: Radius.full,
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.xs,
  },
  chipText: {
    color: Colors.ash,
    fontSize: Typography.sizes.label,
    fontWeight: "400",
  },
  improvementList: { gap: Spacing.md },
  improvementRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: Spacing.md,
  },
  checkMark: {
    color: Colors.ember,
    fontSize: Typography.sizes.body,
    fontWeight: "700",
    marginTop: -1,
  },
  improvementText: {
    color: Colors.ash,
    fontSize: Typography.sizes.caption,
    fontWeight: "400",
    lineHeight: Typography.sizes.caption * Typography.lineHeights.relaxed,
    flex: 1,
  },
  cantChangeBox: {
    borderWidth: 1,
    borderColor: Colors.brass,
    borderRadius: Radius.card,
    padding: Spacing.xl,
  },
  limitationList: { gap: Spacing.md, marginBottom: Spacing.lg },
  crossMark: {
    color: Colors.ash,
    fontSize: Typography.sizes.body,
    fontWeight: "700",
    marginTop: -1,
  },
  limitationText: {
    color: Colors.ash,
    fontSize: Typography.sizes.caption,
    fontWeight: "400",
    lineHeight: Typography.sizes.caption * Typography.lineHeights.relaxed,
    flex: 1,
  },
  cantChangeFooter: {
    color: Colors.ash,
    fontSize: Typography.sizes.caption,
    fontWeight: "400",
    lineHeight: Typography.sizes.caption * Typography.lineHeights.relaxed,
  },
  timelineItem: { marginBottom: Spacing.lg },
  timelineLabel: {
    color: Colors.bone,
    fontSize: Typography.sizes.heading,
    fontWeight: "700",
    lineHeight: Typography.sizes.heading * Typography.lineHeights.normal,
    marginBottom: Spacing.sm,
  },
  timelineWarning: {
    color: Colors.ember,
    fontSize: Typography.sizes.heading,
    fontWeight: "700",
    lineHeight: Typography.sizes.heading * Typography.lineHeights.normal,
    marginBottom: Spacing.sm,
  },
  timelineBody: {
    color: Colors.ash,
    fontSize: Typography.sizes.caption,
    fontWeight: "400",
    lineHeight: Typography.sizes.caption * Typography.lineHeights.relaxed,
  },
  phaseCard: {
    backgroundColor: Colors.surface,
    borderWidth: 1,
    borderColor: Colors.border,
    borderRadius: Radius.card,
    padding: Spacing.lg,
    marginBottom: Spacing.md,
  },
  phaseHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: Spacing.md,
    marginBottom: Spacing.sm,
  },
  phaseNumber: {
    color: Colors.ember,
    fontSize: Typography.sizes.display,
    fontWeight: "700",
    lineHeight: Typography.sizes.display * Typography.lineHeights.tight,
  },
  phaseName: {
    color: Colors.bone,
    fontSize: Typography.sizes.heading,
    fontWeight: "700",
    lineHeight: Typography.sizes.heading * Typography.lineHeights.tight,
  },
  phaseRange: {
    color: Colors.ash,
    fontSize: Typography.sizes.label,
    fontWeight: "400",
  },
  phaseTagline: {
    color: Colors.ash,
    fontSize: Typography.sizes.caption,
    fontWeight: "400",
    lineHeight: Typography.sizes.caption * Typography.lineHeights.relaxed,
  },
  footer: {
    paddingHorizontal: Spacing.xl,
    paddingBottom: Spacing.xl,
    paddingTop: Spacing.md,
  },
  errorContainer: {
    backgroundColor: Colors.dangerDim,
    borderWidth: 1,
    borderColor: Colors.danger,
    borderRadius: Radius.card,
    padding: Spacing.lg,
    marginBottom: Spacing.md,
  },
  errorText: {
    color: Colors.danger,
    fontSize: Typography.sizes.caption,
    fontWeight: "700",
    marginBottom: Spacing.xs,
  },
  retryText: {
    color: Colors.ash,
    fontSize: Typography.sizes.label,
    fontWeight: "400",
  },
  ctaOuter: {
    width: "100%",
    height: 52,
    borderRadius: Radius.full,
    backgroundColor: Colors.ember,
    overflow: "hidden",
  },
  ctaDisabled: {
    backgroundColor: Colors.muted,
    opacity: 0.5,
  },
  ctaInner: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
  },
  ctaText: {
    color: "#FFFFFF",
    fontSize: Typography.sizes.caption,
    fontWeight: "700",
  },
})
