import { Pressable, View, Text, StyleSheet } from "react-native"
import { Colors, Radius, Spacing, Typography } from "@/constants/design"

interface WeekRowProps {
  weekNumber: number
  completionRate: number
  isCurrent: boolean
  onPress: () => void
}

export function WeekRow({
  weekNumber,
  completionRate,
  isCurrent,
  onPress,
}: WeekRowProps) {
  const statusColor =
    completionRate >= 80
      ? Colors.checkDone
      : completionRate >= 50
        ? Colors.ember
        : Colors.muted

  return (
    <Pressable onPress={onPress} style={[styles.row, isCurrent && styles.rowCurrent]}>
      <View style={styles.weekCol}>
        <Text style={[styles.weekLabel, isCurrent && styles.weekLabelCurrent]}>
          Week {weekNumber}
        </Text>
        {isCurrent && <View style={styles.currentDot} />}
      </View>
      <View style={styles.rateCol}>
        <Text style={[styles.rate, { color: statusColor }]}>
          {Math.round(completionRate)}%
        </Text>
      </View>
      <View style={[styles.pill, { backgroundColor: statusColor + "20" }]}>
        <Text style={[styles.pillText, { color: statusColor }]}>
          {completionRate >= 80
            ? "Strong"
            : completionRate >= 50
              ? "Building"
              : completionRate > 0
                ? "Starting"
                : "Upcoming"}
        </Text>
      </View>
    </Pressable>
  )
}

const styles = StyleSheet.create({
  row: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: Spacing.lg,
    paddingHorizontal: Spacing.lg,
    borderBottomWidth: 0.5,
    borderBottomColor: Colors.divider,
  },
  rowCurrent: {
    backgroundColor: Colors.emberDim,
    borderRadius: Radius.md,
    borderBottomWidth: 0,
    marginBottom: Spacing.sm,
  },
  weekCol: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    gap: Spacing.md,
  },
  weekLabel: {
    color: Colors.bone,
    fontSize: Typography.sizes.body,
    fontWeight: Typography.weights.medium,
  },
  weekLabelCurrent: {
    color: Colors.ember,
  },
  currentDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: Colors.ember,
  },
  rateCol: {
    width: 48,
    alignItems: "flex-end",
    marginRight: Spacing.lg,
  },
  rate: {
    fontSize: Typography.sizes.body,
    fontWeight: Typography.weights.bold,
  },
  pill: {
    paddingHorizontal: Spacing.md,
    paddingVertical: 3,
    borderRadius: Radius.full,
  },
  pillText: {
    fontSize: Typography.sizes.label,
    fontWeight: Typography.weights.medium,
  },
})
