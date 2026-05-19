import { View, Text, StyleSheet, type DimensionValue } from "react-native"
import { Colors, Radius, Spacing, Typography } from "@/constants/design"

interface PillarBarProps {
  label: string
  score: number
  delta: number
  color?: string
}

export function PillarBar({
  label,
  score,
  delta,
  color = Colors.ember,
}: PillarBarProps) {
  const barWidth: DimensionValue = `${Math.min(Math.max(score, 0), 100)}%`

  return (
    <View style={styles.row}>
      <View style={styles.labelCol}>
        <Text style={styles.label} numberOfLines={1}>
          {label}
        </Text>
      </View>
      <View style={styles.barContainer}>
        <View style={styles.barBg}>
          <View style={[styles.barFill, { width: barWidth, backgroundColor: color }]} />
        </View>
      </View>
      <View style={styles.scoreCol}>
        <Text style={styles.score}>{score}</Text>
        {delta !== 0 && (
          <Text style={[styles.delta, delta > 0 ? styles.deltaUp : styles.deltaDown]}>
            {delta > 0 ? "+" : ""}
            {delta}
          </Text>
        )}
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  row: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: Spacing.lg,
  },
  labelCol: {
    width: 80,
  },
  label: {
    color: Colors.ash,
    fontSize: Typography.sizes.caption,
    fontWeight: Typography.weights.medium,
  },
  barContainer: {
    flex: 1,
    marginHorizontal: Spacing.md,
  },
  barBg: {
    height: 6,
    backgroundColor: Colors.divider,
    borderRadius: Radius.full,
    overflow: "hidden",
  },
  barFill: {
    height: "100%",
    borderRadius: Radius.full,
  },
  scoreCol: {
    width: 48,
    alignItems: "flex-end",
  },
  score: {
    color: Colors.bone,
    fontSize: Typography.sizes.caption,
    fontWeight: Typography.weights.bold,
  },
  delta: {
    fontSize: Typography.sizes.label,
    fontWeight: Typography.weights.medium,
  },
  deltaUp: {
    color: Colors.checkDone,
  },
  deltaDown: {
    color: Colors.danger,
  },
})
