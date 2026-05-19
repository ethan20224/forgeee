import { View, Text, StyleSheet } from "react-native"
import { Colors, Radius, Spacing, Typography } from "@/constants/design"

interface InsightCardProps {
  message: string
  stage: string
  pillar: string | null
}

const STAGE_LABELS: Record<string, string> = {
  outcome: "Results",
  habit: "Habit",
  mechanism: "Science",
}

export function InsightCard({ message, stage, pillar }: InsightCardProps) {
  const stageLabel = STAGE_LABELS[stage] ?? stage

  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <View style={styles.stageBadge}>
          <Text style={styles.stageText}>{stageLabel}</Text>
        </View>
        {pillar && <Text style={styles.pillar}>{pillar}</Text>}
      </View>
      <Text style={styles.message}>{message}</Text>
    </View>
  )
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: Colors.raised,
    borderRadius: Radius.card,
    borderWidth: 0.5,
    borderColor: Colors.divider,
    padding: Spacing.lg,
    marginBottom: Spacing.lg,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: Spacing.md,
    gap: Spacing.md,
  },
  stageBadge: {
    backgroundColor: Colors.emberDim,
    borderRadius: Radius.full,
    paddingHorizontal: Spacing.md,
    paddingVertical: 2,
  },
  stageText: {
    color: Colors.ember,
    fontSize: Typography.sizes.label,
    fontWeight: Typography.weights.bold,
    textTransform: "uppercase",
    letterSpacing: Typography.letterSpacing.wide,
  },
  pillar: {
    color: Colors.ash,
    fontSize: Typography.sizes.label,
    fontWeight: Typography.weights.medium,
  },
  message: {
    color: Colors.bone,
    fontSize: Typography.sizes.body,
    lineHeight: Typography.sizes.body * Typography.lineHeights.normal,
  },
})
