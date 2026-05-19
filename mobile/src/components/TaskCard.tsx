import { Pressable, Text, View, StyleSheet } from "react-native"
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withSpring,
} from "react-native-reanimated"
import { Colors, Radius, Spacing, Typography } from "@/constants/design"
import { PILLAR_DISPLAY, type Pillar } from "@/constants/pillars"
import type { TaskResponse } from "@/types/api"

interface TaskCardProps {
  task: TaskResponse
  onComplete: (taskId: string) => void
}

export function TaskCard({ task, onComplete }: TaskCardProps) {
  const scale = useSharedValue(1)

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }))

  const handlePress = () => {
    if (task.is_completed) return
    scale.value = withSpring(0.95, { damping: 15 }, () => {
      scale.value = withSpring(1)
    })
    onComplete(task.id)
  }

  const pillarLabel =
    PILLAR_DISPLAY[task.pillar as Pillar]?.plain ?? task.pillar

  return (
    <Animated.View style={animatedStyle}>
      <Pressable
        onPress={handlePress}
        style={[styles.card, task.is_completed && styles.cardDone]}
      >
        <View style={styles.checkbox}>
          {task.is_completed && <View style={styles.checkFill} />}
        </View>
        <View style={styles.content}>
          <Text
            style={[styles.title, task.is_completed && styles.titleDone]}
            numberOfLines={2}
          >
            {task.title}
          </Text>
          <View style={styles.meta}>
            <Text style={styles.pillar}>{pillarLabel}</Text>
            {task.duration_mins && (
              <Text style={styles.duration}>{task.duration_mins} min</Text>
            )}
            <Text style={styles.xp}>+{task.xp_value} XP</Text>
          </View>
        </View>
      </Pressable>
    </Animated.View>
  )
}

const styles = StyleSheet.create({
  card: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: Colors.raised,
    borderWidth: 0.5,
    borderColor: Colors.divider,
    borderRadius: Radius.card,
    padding: Spacing.lg,
    marginBottom: Spacing.md,
  },
  cardDone: {
    opacity: 0.6,
    backgroundColor: Colors.surface,
  },
  checkbox: {
    width: 22,
    height: 22,
    borderRadius: Radius.md,
    borderWidth: 1.5,
    borderColor: Colors.ember,
    alignItems: "center",
    justifyContent: "center",
    marginRight: Spacing.lg,
  },
  checkFill: {
    width: 12,
    height: 12,
    borderRadius: 2,
    backgroundColor: Colors.checkDone,
  },
  content: {
    flex: 1,
  },
  title: {
    color: Colors.bone,
    fontSize: Typography.sizes.body,
    fontWeight: Typography.weights.medium,
    marginBottom: Spacing.sm,
  },
  titleDone: {
    textDecorationLine: "line-through",
    color: Colors.muted,
  },
  meta: {
    flexDirection: "row",
    alignItems: "center",
    gap: Spacing.md,
  },
  pillar: {
    color: Colors.ember,
    fontSize: Typography.sizes.caption,
    fontWeight: Typography.weights.medium,
  },
  duration: {
    color: Colors.ash,
    fontSize: Typography.sizes.caption,
  },
  xp: {
    color: Colors.ash,
    fontSize: Typography.sizes.caption,
  },
})
