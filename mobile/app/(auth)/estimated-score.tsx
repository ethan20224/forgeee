import { useEffect, useState } from "react"
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  Pressable,
} from "react-native"
import { SafeAreaView } from "react-native-safe-area-context"
import { useRouter } from "expo-router"
import { Feather } from "@expo/vector-icons"
import { Colors, Spacing, Typography, Radius } from "@/constants/design"
import { ForgeCard } from "@/components/ui/ForgeCard"
import { PrimaryButton } from "@/components/ui/PrimaryButton"
import { getCachedQuizAnswers } from "@/lib/quizCache"
import { setCachedEstimatedScore } from "@/lib/planCache"
import {
  estimateScoreFromQuiz,
  type EstimatedScoreResult,
} from "@/lib/scoreEstimator"
import { PILLAR_DISPLAY, type Pillar } from "@/constants/pillars"

const PILLAR_INSIGHTS: Record<string, string> = {
  facial_composition:
    "Structure-adjacent habits unlock maximum facial contrast",
  skin: "Consistent barrier care creates visible texture change in 28 days",
  grooming: "Sharpness compounds \u2014 precision adds perceived structure",
  hair: "Scalp health and styling consistency change perceived density",
  posture: "Frame expansion is underrated \u2014 immediate visual effect",
  style: "Fit and color coordination amplify everything else you do",
  sleep: "Sleep drives cellular repair \u2014 the foundation of skin quality",
  nutrition: "Internal inflammation shows on your face",
  voice: "Vocal clarity signals confidence \u2014 underrated lever",
}

const PROTOCOL_BULLETS = [
  "90 days of personalized daily tasks",
  "Photo check-ins every 3 days to track progress",
  "Weekly AI coaching reports",
]

function getTopLevers(
  pillarEstimates: { pillar: string; score: number }[],
  count: number,
): string[] {
  return [...pillarEstimates]
    .sort((a, b) => a.score - b.score)
    .slice(0, count)
    .map((p) => p.pillar)
}

function pillarLabel(key: string): string {
  const display = PILLAR_DISPLAY[key as Pillar]
  if (display) return display.plain
  return key
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ")
}

export default function EstimatedScoreScreen() {
  const router = useRouter()
  const [score, setScore] = useState<EstimatedScoreResult | null>(null)
  const [topLevers, setTopLevers] = useState<string[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    try {
      const answers = getCachedQuizAnswers()
      if (!answers) {
        setError(
          "Quiz answers not found. Please go back and complete the quiz.",
        )
        return
      }

      const result = estimateScoreFromQuiz(answers)
      setCachedEstimatedScore(result)

      const levers = getTopLevers(result.pillarScores, 3)
      setScore(result)
      setTopLevers(levers)
    } catch {
      setError(
        "Something went wrong calculating your score. Please try again.",
      )
    }
  }, [])

  const handleCTA = () => {
    router.replace("/(auth)/signup")
  }

  if (error) {
    return (
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.errorContainer}>
          <Text style={styles.errorTitle}>Something went wrong</Text>
          <Text style={styles.errorBody}>{error}</Text>
          <Pressable style={styles.backButton} onPress={() => router.back()}>
            <Text style={styles.backButtonText}>Go back</Text>
          </Pressable>
        </View>
      </SafeAreaView>
    )
  }

  if (!score) {
    return (
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.loadingContainer}>
          <View style={styles.skeletonScore} />
          <View style={styles.skeletonLabel} />
          <View style={[styles.skeletonCard, { marginTop: Spacing.xxl }]} />
          <View style={[styles.skeletonCard, { marginTop: Spacing.md }]} />
          <View style={[styles.skeletonCard, { marginTop: Spacing.md }]} />
        </View>
      </SafeAreaView>
    )
  }

  const rangeLow = Math.max(0, Math.round(score.optimisationScore) - 5)
  const rangeHigh = Math.min(100, Math.round(score.optimisationScore) + 5)

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.headerSection}>
          <Text style={styles.eyebrow}>YOUR STARTING FORGE SCORE</Text>
          <Text style={styles.heroScore}>
            {Math.round(score.optimisationScore)}
          </Text>
          <Text style={styles.rangeLabel}>
            Estimated range: {rangeLow}\u2013{rangeHigh}
          </Text>
          <Text style={styles.subCopy}>
            Based on your current routine and goals. Your real score unlocks
            on day 3.
          </Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionLabel}>YOUR BIGGEST LEVERS</Text>
          {topLevers.map((key) => (
            <ForgeCard key={key} style={styles.leverCard}>
              <Text style={styles.leverPillar}>{pillarLabel(key)}</Text>
              <Text style={styles.leverInsight}>
                {PILLAR_INSIGHTS[key] ??
                  "Consistent effort compounds over 90 days."}
              </Text>
            </ForgeCard>
          ))}
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionLabel}>
            WHAT YOUR PROTOCOL BUILDS
          </Text>
          {PROTOCOL_BULLETS.map((bullet) => (
            <View key={bullet} style={styles.bulletRow}>
              <Feather
                name="check"
                size={14}
                color={Colors.ember}
                style={styles.bulletIcon}
              />
              <Text style={styles.bulletText}>{bullet}</Text>
            </View>
          ))}
        </View>

        <View style={styles.footerSpacer} />
      </ScrollView>

      <View style={styles.footer}>
        <PrimaryButton onPress={handleCTA}>
          Save my protocol →
        </PrimaryButton>
        <Text style={styles.footerNote}>
          Free to start. No card required.
        </Text>
      </View>
    </SafeAreaView>
  )
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: Colors.canvas },
  scroll: { flex: 1 },
  scrollContent: {
    paddingHorizontal: Spacing.screen,
    paddingTop: Spacing.xxl,
  },
  headerSection: { alignItems: "center", marginBottom: Spacing.xxl },
  eyebrow: {
    color: Colors.ember,
    fontSize: Typography.sizes.nano,
    fontWeight: "700",
    letterSpacing: 1.8,
    textTransform: "uppercase",
    marginBottom: Spacing.lg,
  },
  heroScore: {
    color: Colors.bone,
    fontSize: Typography.sizes.hero,
    fontWeight: "700",
    letterSpacing: Typography.letterSpacing.tight,
    lineHeight: Typography.sizes.hero * Typography.lineHeights.tight,
  },
  rangeLabel: {
    color: Colors.ash,
    fontSize: Typography.sizes.caption,
    fontWeight: "400",
    marginTop: Spacing.sm,
  },
  subCopy: {
    color: Colors.ash,
    fontSize: Typography.sizes.caption,
    fontWeight: "400",
    textAlign: "center",
    marginTop: Spacing.md,
    lineHeight: Typography.sizes.caption * Typography.lineHeights.normal,
    maxWidth: 280,
  },
  section: { marginBottom: Spacing.xxl },
  sectionLabel: {
    color: Colors.ember,
    fontSize: Typography.sizes.nano,
    fontWeight: "700",
    letterSpacing: 1.8,
    textTransform: "uppercase",
    marginBottom: Spacing.lg,
  },
  leverCard: { marginBottom: Spacing.md },
  leverPillar: {
    color: Colors.bone,
    fontSize: Typography.sizes.heading,
    fontWeight: "700",
    marginBottom: Spacing.sm,
  },
  leverInsight: {
    color: Colors.ash,
    fontSize: Typography.sizes.caption,
    fontWeight: "400",
    lineHeight: Typography.sizes.caption * Typography.lineHeights.normal,
  },
  bulletRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    marginBottom: Spacing.md,
  },
  bulletIcon: { marginTop: 1, marginRight: Spacing.md },
  bulletText: {
    flex: 1,
    color: Colors.bone,
    fontSize: Typography.sizes.caption,
    fontWeight: "400",
    lineHeight: Typography.sizes.caption * Typography.lineHeights.normal,
  },
  footerSpacer: { height: 120 },
  footer: {
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    paddingHorizontal: Spacing.screen,
    paddingBottom: Spacing.xxl,
    paddingTop: Spacing.lg,
    backgroundColor: Colors.canvas,
    borderTopWidth: 0.5,
    borderTopColor: Colors.divider,
  },
  footerNote: {
    color: Colors.muted,
    fontSize: Typography.sizes.label,
    fontWeight: "400",
    textAlign: "center",
    marginTop: Spacing.md,
  },
  errorContainer: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: Spacing.screen,
  },
  errorTitle: {
    color: Colors.bone,
    fontSize: Typography.sizes.title,
    fontWeight: "700",
    marginBottom: Spacing.md,
    textAlign: "center",
  },
  errorBody: {
    color: Colors.ash,
    fontSize: Typography.sizes.caption,
    fontWeight: "400",
    textAlign: "center",
    lineHeight: Typography.sizes.caption * Typography.lineHeights.normal,
    marginBottom: Spacing.xxl,
  },
  backButton: {
    paddingVertical: Spacing.md,
    paddingHorizontal: Spacing.xl,
    borderRadius: Radius.full,
    borderWidth: 0.5,
    borderColor: Colors.divider,
  },
  backButtonText: {
    color: Colors.ash,
    fontSize: Typography.sizes.caption,
    fontWeight: "400",
  },
  loadingContainer: {
    flex: 1,
    alignItems: "center",
    paddingHorizontal: Spacing.screen,
    paddingTop: Spacing.xxl,
  },
  skeletonScore: {
    width: 120,
    height: 80,
    borderRadius: Radius.md,
    backgroundColor: Colors.raised,
  },
  skeletonLabel: {
    width: 180,
    height: 16,
    borderRadius: Radius.md,
    backgroundColor: Colors.raised,
    marginTop: Spacing.md,
  },
  skeletonCard: {
    width: "100%",
    height: 72,
    borderRadius: Radius.card,
    backgroundColor: Colors.raised,
  },
})
