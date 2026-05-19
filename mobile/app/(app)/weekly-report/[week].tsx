import { useEffect, useState } from "react"
import {
  View,
  Text,
  ScrollView,
  ActivityIndicator,
  StyleSheet,
} from "react-native"
import { useLocalSearchParams, useRouter } from "expo-router"
import { useSafeAreaInsets } from "react-native-safe-area-context"
import { Ionicons } from "@expo/vector-icons"
import { Pressable } from "react-native"
import { Colors, Radius, Spacing, Typography } from "@/constants/design"
import { getWeeklyReport } from "@/api/coaching"
import { PillarBar } from "@/components/PillarBar"
import type { WeeklyReportResponse } from "@/types/api"

export default function WeeklyReportScreen() {
  const insets = useSafeAreaInsets()
  const router = useRouter()
  const { week } = useLocalSearchParams<{ week: string }>()
  const [report, setReport] = useState<WeeklyReportResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const weekNum = parseInt(week ?? "1", 10)
    setIsLoading(true)
    getWeeklyReport(weekNum)
      .then(setReport)
      .catch(() => {})
      .finally(() => setIsLoading(false))
  }, [week])

  if (isLoading) {
    return (
      <View style={[styles.container, styles.center, { paddingTop: insets.top }]}>
        <ActivityIndicator color={Colors.ember} />
      </View>
    )
  }

  if (!report) {
    return (
      <View style={[styles.container, styles.center, { paddingTop: insets.top }]}>
        <Text style={styles.empty}>Report not available yet</Text>
      </View>
    )
  }

  return (
    <ScrollView
      style={[styles.container, { paddingTop: insets.top }]}
      contentContainerStyle={styles.content}
    >
      <Pressable onPress={() => router.back()} style={styles.backBtn}>
        <Ionicons name="chevron-back" size={20} color={Colors.bone} />
        <Text style={styles.backText}>Program</Text>
      </Pressable>

      <Text style={styles.title}>Week {report.week_number} Report</Text>
      <Text style={styles.subtitle}>Season {report.season}</Text>

      <View style={styles.statsRow}>
        <View style={styles.stat}>
          <Text style={styles.statValue}>
            {Math.round(report.completion_rate)}%
          </Text>
          <Text style={styles.statLabel}>Completion</Text>
        </View>
        <View style={styles.stat}>
          <Text style={styles.statValue}>
            {report.completed_tasks}/{report.total_tasks}
          </Text>
          <Text style={styles.statLabel}>Tasks Done</Text>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Pillar Scores</Text>
        {report.pillar_movements.map((pm) => (
          <PillarBar
            key={pm.pillar}
            label={pm.label}
            score={pm.score}
            delta={pm.delta}
          />
        ))}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Coaching Note</Text>
        <Text style={styles.paragraph}>{report.coaching_note}</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Focus Next Week</Text>
        <Text style={styles.paragraph}>{report.focus_next_week}</Text>
      </View>
    </ScrollView>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.canvas,
  },
  center: {
    alignItems: "center",
    justifyContent: "center",
  },
  content: {
    padding: Spacing.screen,
    paddingBottom: 120,
  },
  backBtn: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: Spacing.lg,
    gap: Spacing.sm,
  },
  backText: {
    color: Colors.bone,
    fontSize: Typography.sizes.body,
  },
  title: {
    color: Colors.bone,
    fontSize: Typography.sizes.title,
    fontWeight: Typography.weights.bold,
    marginBottom: Spacing.sm,
  },
  subtitle: {
    color: Colors.ash,
    fontSize: Typography.sizes.caption,
    marginBottom: Spacing.xl,
  },
  statsRow: {
    flexDirection: "row",
    gap: Spacing.lg,
    marginBottom: Spacing.xxl,
  },
  stat: {
    flex: 1,
    backgroundColor: Colors.raised,
    borderRadius: Radius.card,
    borderWidth: 0.5,
    borderColor: Colors.divider,
    padding: Spacing.lg,
    alignItems: "center",
  },
  statValue: {
    color: Colors.ember,
    fontSize: Typography.sizes.title,
    fontWeight: Typography.weights.bold,
  },
  statLabel: {
    color: Colors.ash,
    fontSize: Typography.sizes.label,
    marginTop: Spacing.sm,
  },
  section: {
    marginBottom: Spacing.xxl,
  },
  sectionTitle: {
    color: Colors.bone,
    fontSize: Typography.sizes.heading,
    fontWeight: Typography.weights.medium,
    marginBottom: Spacing.lg,
  },
  paragraph: {
    color: Colors.boneTint,
    fontSize: Typography.sizes.body,
    lineHeight: Typography.sizes.body * Typography.lineHeights.normal,
  },
  empty: {
    color: Colors.ash,
    fontSize: Typography.sizes.body,
  },
})
