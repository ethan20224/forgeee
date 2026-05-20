import { useEffect, useState } from "react"
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  Pressable,
  ActivityIndicator,
} from "react-native"
import { router, useLocalSearchParams } from "expo-router"
import { useSafeAreaInsets } from "react-native-safe-area-context"
import { Ionicons } from "@expo/vector-icons"
import { Colors, Spacing, Typography, Radius } from "@/constants/design"
import { getCycleDetail } from "@/api/cycles"
import type { CycleAnalysisResponse } from "@/types/api"

const PILLAR_LABELS: Record<string, string> = {
  facial_composition: "Face",
  skin: "Skin",
  grooming: "Grooming",
  hair: "Hair",
  posture: "Posture",
  style: "Style",
  sleep: "Sleep",
  nutrition: "Nutrition",
  voice: "Voice",
}

export default function CycleResultScreen() {
  const { cycleId } = useLocalSearchParams<{ cycleId: string }>()
  const insets = useSafeAreaInsets()
  const [analysis, setAnalysis] = useState<CycleAnalysisResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (cycleId) {
      getCycleDetail(cycleId)
        .then(setAnalysis)
        .finally(() => setLoading(false))
    }
  }, [cycleId])

  if (loading) {
    return (
      <View style={[styles.center, { paddingTop: insets.top + 100 }]}>
        <ActivityIndicator size="large" color={Colors.ember} />
      </View>
    )
  }

  if (!analysis) {
    return (
      <View style={[styles.center, { paddingTop: insets.top + 100 }]}>
        <Text style={styles.errorText}>Analysis not found</Text>
      </View>
    )
  }

  const scoreEntries = Object.entries(analysis.scores)
    .filter(([_, v]) => v !== null)
    .map(([key, value]) => ({
      pillar: key.replace("_score", ""),
      score: value as number,
    }))

  const avgScore =
    scoreEntries.length > 0
      ? Math.round(scoreEntries.reduce((sum, e) => sum + e.score, 0) / scoreEntries.length)
      : 0

  return (
    <View style={[styles.container, { paddingTop: insets.top + Spacing.lg }]}>
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={24} color={Colors.bone} />
        </Pressable>
        <Text style={styles.title}>Cycle #{analysis.cycle_number}</Text>
        <Pressable onPress={() => router.replace("/(app)/(tabs)")} style={styles.backBtn}>
          <Ionicons name="home-outline" size={22} color={Colors.bone} />
        </Pressable>
      </View>

      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scroll}>
        <View style={styles.scoreHero}>
          <Text style={styles.heroNumber}>{avgScore}</Text>
          <Text style={styles.heroLabel}>Average Score</Text>
        </View>

        {analysis.face_shape && (
          <View style={styles.badge}>
            <Text style={styles.badgeText}>Face shape: {analysis.face_shape}</Text>
          </View>
        )}

        <View style={styles.scoreGrid}>
          {scoreEntries.map(({ pillar, score }) => (
            <View key={pillar} style={styles.scoreCard}>
              <Text style={styles.scoreValue}>{score}</Text>
              <Text style={styles.scoreLabel}>{PILLAR_LABELS[pillar] || pillar}</Text>
            </View>
          ))}
        </View>

        {analysis.ai_insight && (
          <View style={styles.insightCard}>
            <Ionicons name="sparkles" size={16} color={Colors.ember} />
            <Text style={styles.insightText}>{analysis.ai_insight}</Text>
          </View>
        )}

        {analysis.next_focus && (
          <View style={styles.focusCard}>
            <Ionicons name="flag" size={16} color={Colors.ember} />
            <Text style={styles.focusText}>{analysis.next_focus}</Text>
          </View>
        )}
      </ScrollView>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.canvas,
    paddingHorizontal: Spacing.screen,
  },
  center: {
    flex: 1,
    backgroundColor: Colors.canvas,
    justifyContent: "center",
    alignItems: "center",
  },
  errorText: {
    color: Colors.ash,
    fontSize: Typography.sizes.body,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: Spacing.xl,
  },
  backBtn: {
    width: 40,
    height: 40,
    justifyContent: "center",
    alignItems: "center",
  },
  title: {
    fontSize: Typography.sizes.heading,
    fontWeight: Typography.weights.bold,
    color: Colors.bone,
  },
  scroll: {
    paddingBottom: 60,
  },
  scoreHero: {
    alignItems: "center",
    marginBottom: Spacing.xl,
  },
  heroNumber: {
    fontSize: Typography.sizes.hero,
    fontWeight: Typography.weights.bold,
    color: Colors.ember,
    letterSpacing: Typography.letterSpacing.tight,
  },
  heroLabel: {
    fontSize: Typography.sizes.caption,
    color: Colors.ash,
    marginTop: Spacing.xs,
  },
  badge: {
    alignSelf: "center",
    backgroundColor: Colors.emberDim,
    borderRadius: Radius.full,
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.md,
    marginBottom: Spacing.xl,
  },
  badgeText: {
    fontSize: Typography.sizes.caption,
    fontWeight: Typography.weights.medium,
    color: Colors.ember,
    textTransform: "capitalize",
  },
  scoreGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: Spacing.md,
    marginBottom: Spacing.xl,
  },
  scoreCard: {
    backgroundColor: Colors.raised,
    borderRadius: Radius.card,
    paddingVertical: Spacing.lg,
    paddingHorizontal: Spacing.lg,
    alignItems: "center",
    width: "30%",
    flexGrow: 1,
  },
  scoreValue: {
    fontSize: Typography.sizes.title,
    fontWeight: Typography.weights.bold,
    color: Colors.bone,
  },
  scoreLabel: {
    fontSize: Typography.sizes.label,
    color: Colors.ash,
    marginTop: Spacing.xs,
  },
  insightCard: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: Spacing.md,
    backgroundColor: Colors.raised,
    borderRadius: Radius.card,
    padding: Spacing.lg,
    marginBottom: Spacing.lg,
  },
  insightText: {
    flex: 1,
    fontSize: Typography.sizes.caption,
    color: Colors.bone,
    lineHeight: Typography.sizes.caption * Typography.lineHeights.normal,
  },
  focusCard: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: Spacing.md,
    backgroundColor: Colors.emberDim,
    borderColor: Colors.emberBorder,
    borderWidth: 1,
    borderRadius: Radius.card,
    padding: Spacing.lg,
  },
  focusText: {
    flex: 1,
    fontSize: Typography.sizes.caption,
    color: Colors.ember,
    lineHeight: Typography.sizes.caption * Typography.lineHeights.normal,
  },
})
