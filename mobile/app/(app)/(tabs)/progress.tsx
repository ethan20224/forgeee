import { useEffect } from "react"
import {
  View,
  Text,
  ScrollView,
  RefreshControl,
  StyleSheet,
} from "react-native"
import { useSafeAreaInsets } from "react-native-safe-area-context"
import { Colors, Spacing, Typography, Radius } from "@/constants/design"
import { useProgressStore } from "@/store/progressStore"
import { PillarBar } from "@/components/PillarBar"

export default function ProgressScreen() {
  const insets = useSafeAreaInsets()
  const {
    optimisationScore,
    deltaVsBaseline,
    totalXp,
    level,
    pillarScores,
    isLoading,
    fetchProgress,
  } = useProgressStore()

  useEffect(() => {
    fetchProgress()
  }, [])

  const visiblePillars = pillarScores.filter((p) => p.weight > 0)

  return (
    <ScrollView
      style={[styles.container, { paddingTop: insets.top }]}
      contentContainerStyle={styles.content}
      refreshControl={
        <RefreshControl
          refreshing={isLoading}
          onRefresh={fetchProgress}
          tintColor={Colors.ember}
        />
      }
    >
      <Text style={styles.screenTitle}>Progress</Text>

      <View style={styles.heroCard}>
        <Text style={styles.heroLabel}>FORGE Score</Text>
        <Text style={styles.heroScore}>{Math.round(optimisationScore)}</Text>
        <Text
          style={[
            styles.heroDelta,
            deltaVsBaseline >= 0 ? styles.deltaUp : styles.deltaDown,
          ]}
        >
          {deltaVsBaseline >= 0 ? "+" : ""}
          {Math.round(deltaVsBaseline)} vs baseline
        </Text>
        <View style={styles.xpRow}>
          <Text style={styles.xpText}>Level {level}</Text>
          <Text style={styles.xpDot}>•</Text>
          <Text style={styles.xpText}>{totalXp.toLocaleString()} XP</Text>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Pillar Scores</Text>
        {visiblePillars.length === 0 && (
          <Text style={styles.emptyText}>
            Complete tasks to see your pillar scores
          </Text>
        )}
        {visiblePillars.map((pillar) => (
          <PillarBar
            key={pillar.pillar}
            label={pillar.label}
            score={pillar.score}
            delta={pillar.delta_vs_baseline}
          />
        ))}
      </View>
    </ScrollView>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.canvas,
  },
  content: {
    padding: Spacing.screen,
    paddingBottom: 120,
  },
  screenTitle: {
    color: Colors.bone,
    fontSize: Typography.sizes.title,
    fontWeight: Typography.weights.bold,
    letterSpacing: Typography.letterSpacing.snug,
    marginBottom: Spacing.xl,
  },
  heroCard: {
    backgroundColor: Colors.raised,
    borderRadius: Radius.card,
    borderWidth: 0.5,
    borderColor: Colors.emberBorder,
    padding: Spacing.xl,
    alignItems: "center",
    marginBottom: Spacing.xxl,
  },
  heroLabel: {
    color: Colors.ash,
    fontSize: Typography.sizes.caption,
    fontWeight: Typography.weights.medium,
    letterSpacing: Typography.letterSpacing.wide,
    textTransform: "uppercase",
    marginBottom: Spacing.md,
  },
  heroScore: {
    color: Colors.ember,
    fontSize: Typography.sizes.hero,
    fontWeight: Typography.weights.bold,
    letterSpacing: Typography.letterSpacing.tight,
  },
  heroDelta: {
    fontSize: Typography.sizes.caption,
    fontWeight: Typography.weights.medium,
    marginTop: Spacing.sm,
  },
  deltaUp: {
    color: Colors.checkDone,
  },
  deltaDown: {
    color: Colors.danger,
  },
  xpRow: {
    flexDirection: "row",
    alignItems: "center",
    marginTop: Spacing.lg,
    gap: Spacing.md,
  },
  xpText: {
    color: Colors.ash,
    fontSize: Typography.sizes.caption,
  },
  xpDot: {
    color: Colors.muted,
    fontSize: Typography.sizes.caption,
  },
  section: {
    marginBottom: Spacing.xl,
  },
  sectionTitle: {
    color: Colors.bone,
    fontSize: Typography.sizes.heading,
    fontWeight: Typography.weights.medium,
    marginBottom: Spacing.lg,
  },
  emptyText: {
    color: Colors.ash,
    fontSize: Typography.sizes.caption,
    textAlign: "center",
    paddingVertical: Spacing.xl,
  },
})
