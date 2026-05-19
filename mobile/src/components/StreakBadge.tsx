import { View, Text, StyleSheet } from "react-native"
import { Colors, Radius, Spacing, Typography } from "@/constants/design"

interface StreakBadgeProps {
  streak: number
  milestone?: number | null
}

export function StreakBadge({ streak, milestone }: StreakBadgeProps) {
  const isHot = streak >= 7

  return (
    <View style={[styles.badge, isHot && styles.badgeHot]}>
      <Text style={styles.flame}>🔥</Text>
      <Text style={[styles.count, isHot && styles.countHot]}>{streak}</Text>
      {milestone && (
        <View style={styles.milestone}>
          <Text style={styles.milestoneText}>{milestone}d!</Text>
        </View>
      )}
    </View>
  )
}

const styles = StyleSheet.create({
  badge: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: Colors.raised,
    borderRadius: Radius.full,
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.md,
    borderWidth: 0.5,
    borderColor: Colors.divider,
    gap: Spacing.sm,
  },
  badgeHot: {
    borderColor: Colors.emberBorder,
    backgroundColor: Colors.emberDim,
  },
  flame: {
    fontSize: 16,
  },
  count: {
    color: Colors.bone,
    fontSize: Typography.sizes.body,
    fontWeight: Typography.weights.bold,
  },
  countHot: {
    color: Colors.ember,
  },
  milestone: {
    backgroundColor: Colors.ember,
    borderRadius: Radius.full,
    paddingHorizontal: 6,
    paddingVertical: 2,
    marginLeft: Spacing.sm,
  },
  milestoneText: {
    color: Colors.canvas,
    fontSize: Typography.sizes.label,
    fontWeight: Typography.weights.bold,
  },
})
