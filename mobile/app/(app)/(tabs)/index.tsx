import { useEffect } from "react"
import {
  View,
  Text,
  ScrollView,
  RefreshControl,
  StyleSheet,
} from "react-native"
import { useSafeAreaInsets } from "react-native-safe-area-context"
import { Colors, Spacing, Typography } from "@/constants/design"
import { useUserStore } from "@/store/userStore"
import { useProgramStore } from "@/store/programStore"
import { useProgressStore } from "@/store/progressStore"
import { TaskCard } from "@/components/TaskCard"
import { StreakBadge } from "@/components/StreakBadge"
import { CompletionRing } from "@/components/CompletionRing"

export default function HomeScreen() {
  const insets = useSafeAreaInsets()
  const user = useUserStore((s) => s.user)
  const { todaysTasks, isLoadingTasks, fetchTodaysTasks, completeTask } =
    useProgramStore()
  const { currentStreak, fetchProgress } = useProgressStore()

  useEffect(() => {
    fetchTodaysTasks()
    fetchProgress()
  }, [])

  const handleComplete = async (taskId: string) => {
    await completeTask(taskId)
    fetchProgress()
  }

  const completedCount = todaysTasks.filter((t) => t.is_completed).length
  const totalCount = todaysTasks.length
  const greeting = getGreeting()
  const firstName = user?.name?.split(" ")[0] ?? "there"

  return (
    <ScrollView
      style={[styles.container, { paddingTop: insets.top }]}
      contentContainerStyle={styles.content}
      refreshControl={
        <RefreshControl
          refreshing={isLoadingTasks}
          onRefresh={() => {
            fetchTodaysTasks()
            fetchProgress()
          }}
          tintColor={Colors.ember}
        />
      }
    >
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>
            {greeting}, {firstName}
          </Text>
          <Text style={styles.subtitle}>
            Day {user?.program_day ?? 1} • Season {user?.season ?? 1}
          </Text>
        </View>
        <View style={styles.headerRight}>
          <StreakBadge streak={currentStreak} />
        </View>
      </View>

      <View style={styles.progressRow}>
        <CompletionRing completed={completedCount} total={totalCount} />
        <View style={styles.progressText}>
          <Text style={styles.progressTitle}>Today&apos;s Tasks</Text>
          <Text style={styles.progressSubtitle}>
            {completedCount} of {totalCount} completed
          </Text>
        </View>
      </View>

      <View style={styles.taskList}>
        {todaysTasks.length === 0 && !isLoadingTasks && (
          <View style={styles.emptyState}>
            <Text style={styles.emptyTitle}>No tasks today</Text>
            <Text style={styles.emptySubtitle}>
              Complete your first task to see progress
            </Text>
          </View>
        )}
        {todaysTasks.map((task) => (
          <TaskCard key={task.id} task={task} onComplete={handleComplete} />
        ))}
      </View>
    </ScrollView>
  )
}

function getGreeting(): string {
  const hour = new Date().getHours()
  if (hour < 12) return "Good morning"
  if (hour < 17) return "Good afternoon"
  return "Good evening"
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
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: Spacing.xl,
  },
  greeting: {
    color: Colors.bone,
    fontSize: Typography.sizes.title,
    fontWeight: Typography.weights.bold,
    letterSpacing: Typography.letterSpacing.snug,
  },
  subtitle: {
    color: Colors.ash,
    fontSize: Typography.sizes.caption,
    marginTop: Spacing.sm,
  },
  headerRight: {
    alignItems: "flex-end",
  },
  progressRow: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: Colors.raised,
    borderRadius: 12,
    padding: Spacing.lg,
    marginBottom: Spacing.xl,
    borderWidth: 0.5,
    borderColor: Colors.divider,
    gap: Spacing.lg,
  },
  progressText: {
    flex: 1,
  },
  progressTitle: {
    color: Colors.bone,
    fontSize: Typography.sizes.body,
    fontWeight: Typography.weights.medium,
  },
  progressSubtitle: {
    color: Colors.ash,
    fontSize: Typography.sizes.caption,
    marginTop: Spacing.xs,
  },
  taskList: {
    gap: 0,
  },
  emptyState: {
    alignItems: "center",
    paddingVertical: Spacing.xxxl,
  },
  emptyTitle: {
    color: Colors.bone,
    fontSize: Typography.sizes.body,
    fontWeight: Typography.weights.medium,
    marginBottom: Spacing.md,
  },
  emptySubtitle: {
    color: Colors.ash,
    fontSize: Typography.sizes.caption,
    textAlign: "center",
  },
})
