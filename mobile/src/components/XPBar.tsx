import { View, Text, StyleSheet, DimensionValue } from "react-native"
import { Colors, Spacing, Typography, Radius } from "@/constants/design"

interface XPBarProps {
  totalXp: number
  currentLevel: number
  levelName: string
  xpProgress: number
  xpNeeded: number
  progressPct: number
}

export function XPBar({
  totalXp,
  currentLevel,
  levelName,
  xpProgress,
  xpNeeded,
  progressPct,
}: XPBarProps) {
  const barWidth: DimensionValue = `${Math.min(progressPct, 100)}%`

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.levelText}>
          Lv.{currentLevel} — {levelName}
        </Text>
        <Text style={styles.xpText}>
          {xpProgress}/{xpNeeded} XP
        </Text>
      </View>
      <View style={styles.track}>
        <View style={[styles.fill, { width: barWidth }]} />
      </View>
      <Text style={styles.totalXp}>{totalXp.toLocaleString()} total XP</Text>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    gap: Spacing.sm,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  levelText: {
    fontSize: Typography.sizes.caption,
    fontWeight: Typography.weights.bold,
    color: Colors.bone,
  },
  xpText: {
    fontSize: Typography.sizes.label,
    color: Colors.ash,
  },
  track: {
    height: 6,
    backgroundColor: Colors.raised,
    borderRadius: Radius.full,
    overflow: "hidden",
  },
  fill: {
    height: "100%",
    backgroundColor: Colors.ember,
    borderRadius: Radius.full,
  },
  totalXp: {
    fontSize: Typography.sizes.label,
    color: Colors.muted,
  },
})
