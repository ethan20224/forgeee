import { View, Text, StyleSheet } from "react-native"
import { Ionicons } from "@expo/vector-icons"
import { Colors, Spacing, Typography, Radius } from "@/constants/design"
import type { BadgeResponse } from "@/types/api"

interface AchievementBadgeProps {
  badge: BadgeResponse
  size?: "small" | "large"
}

export function AchievementBadge({ badge, size = "small" }: AchievementBadgeProps) {
  const isLarge = size === "large"
  const iconSize = isLarge ? 28 : 20
  const wrapSize = isLarge ? 56 : 40

  return (
    <View style={[styles.container, isLarge && styles.containerLarge]}>
      <View
        style={[
          styles.iconWrap,
          { width: wrapSize, height: wrapSize, borderRadius: wrapSize / 2 },
          badge.unlocked ? styles.iconUnlocked : styles.iconLocked,
        ]}
      >
        <Ionicons
          name={badge.icon as any}
          size={iconSize}
          color={badge.unlocked ? Colors.ember : Colors.muted}
        />
      </View>
      <Text
        style={[styles.name, !badge.unlocked && styles.nameLocked]}
        numberOfLines={1}
      >
        {badge.name}
      </Text>
      {isLarge && (
        <Text style={styles.description} numberOfLines={2}>
          {badge.description}
        </Text>
      )}
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    alignItems: "center",
    width: 72,
    gap: Spacing.xs,
  },
  containerLarge: {
    width: 100,
    gap: Spacing.sm,
  },
  iconWrap: {
    justifyContent: "center",
    alignItems: "center",
  },
  iconUnlocked: {
    backgroundColor: Colors.emberDim,
    borderWidth: 1.5,
    borderColor: Colors.emberBorder,
  },
  iconLocked: {
    backgroundColor: Colors.raised,
    borderWidth: 1,
    borderColor: Colors.divider,
    opacity: 0.5,
  },
  name: {
    fontSize: Typography.sizes.label,
    fontWeight: Typography.weights.medium,
    color: Colors.bone,
    textAlign: "center",
  },
  nameLocked: {
    color: Colors.muted,
  },
  description: {
    fontSize: Typography.sizes.nano,
    color: Colors.ash,
    textAlign: "center",
  },
})
