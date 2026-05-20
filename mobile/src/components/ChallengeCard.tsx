import { View, Text, StyleSheet, Pressable, DimensionValue } from "react-native"
import { Ionicons } from "@expo/vector-icons"
import { Colors, Spacing, Typography, Radius } from "@/constants/design"
import type { ChallengeResponse } from "@/types/api"

interface ChallengeCardProps {
  challenge: ChallengeResponse
  onStart?: () => void
}

export function ChallengeCard({ challenge, onStart }: ChallengeCardProps) {
  const progressPct = challenge.target > 0
    ? Math.round((challenge.progress / challenge.target) * 100)
    : 0
  const barWidth: DimensionValue = `${Math.min(progressPct, 100)}%`
  const isActive = challenge.status === "active"

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View style={styles.iconWrap}>
          <Ionicons
            name={challenge.icon as any}
            size={18}
            color={Colors.ember}
          />
        </View>
        <View style={styles.info}>
          <Text style={styles.name}>{challenge.name}</Text>
          <Text style={styles.description}>{challenge.description}</Text>
        </View>
        <Text style={styles.reward}>+{challenge.xp_reward} XP</Text>
      </View>

      {isActive && (
        <View style={styles.progressSection}>
          <View style={styles.track}>
            <View style={[styles.fill, { width: barWidth }]} />
          </View>
          <Text style={styles.progressText}>
            {challenge.progress}/{challenge.target}
          </Text>
        </View>
      )}

      {!isActive && onStart && (
        <Pressable style={styles.startBtn} onPress={onStart}>
          <Text style={styles.startText}>Start</Text>
        </Pressable>
      )}
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: Colors.raised,
    borderRadius: Radius.card,
    padding: Spacing.lg,
    gap: Spacing.md + 2,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    gap: Spacing.md,
  },
  iconWrap: {
    width: 36,
    height: 36,
    borderRadius: Radius.lg,
    backgroundColor: Colors.emberDim,
    justifyContent: "center",
    alignItems: "center",
  },
  info: {
    flex: 1,
    gap: 2,
  },
  name: {
    fontSize: Typography.sizes.caption,
    fontWeight: Typography.weights.bold,
    color: Colors.bone,
  },
  description: {
    fontSize: Typography.sizes.label,
    color: Colors.ash,
  },
  reward: {
    fontSize: Typography.sizes.label,
    fontWeight: Typography.weights.bold,
    color: Colors.ember,
  },
  progressSection: {
    flexDirection: "row",
    alignItems: "center",
    gap: Spacing.md,
  },
  track: {
    flex: 1,
    height: 5,
    backgroundColor: Colors.surface,
    borderRadius: Radius.full,
    overflow: "hidden",
  },
  fill: {
    height: "100%",
    backgroundColor: Colors.ember,
    borderRadius: Radius.full,
  },
  progressText: {
    fontSize: Typography.sizes.label,
    color: Colors.ash,
    minWidth: 32,
    textAlign: "right",
  },
  startBtn: {
    alignSelf: "flex-start",
    backgroundColor: Colors.emberDim,
    borderColor: Colors.emberBorder,
    borderWidth: 1,
    borderRadius: Radius.lg,
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.md,
  },
  startText: {
    fontSize: Typography.sizes.label,
    fontWeight: Typography.weights.bold,
    color: Colors.ember,
  },
})
