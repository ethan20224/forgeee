import { useEffect, useState } from "react"
import { View, Text, ScrollView, RefreshControl, StyleSheet } from "react-native"
import { useRouter } from "expo-router"
import { useSafeAreaInsets } from "react-native-safe-area-context"
import { Colors, Radius, Spacing, Typography } from "@/constants/design"
import { useUserStore } from "@/store/userStore"
import { useProgramStore } from "@/store/programStore"
import { getWeeklyReports } from "@/api/coaching"
import { getHeatmap } from "@/api/tasks"
import { WeekRow } from "@/components/WeekRow"
import { HeatmapGrid } from "@/components/HeatmapGrid"
import { phaseForDay, PHASE_DISPLAY } from "@/constants/phases"
import type { WeeklyReportSummary, HeatmapDay } from "@/types/api"

export default function ProgramScreen() {
  const insets = useSafeAreaInsets()
  const router = useRouter()
  const user = useUserStore((s) => s.user)
  const { plan, fetchPlan } = useProgramStore()
  const [weeks, setWeeks] = useState<WeeklyReportSummary[]>([])
  const [heatmapDays, setHeatmapDays] = useState<HeatmapDay[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const programDay = user?.program_day ?? 1
  const currentWeek = Math.ceil(programDay / 7)
  const phaseId = phaseForDay(programDay)
  const phase = PHASE_DISPLAY[phaseId]

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setIsLoading(true)
    try {
      const [weekData, heatmapData] = await Promise.all([
        getWeeklyReports().catch(() => []),
        getHeatmap().catch(() => ({ days: [] })),
      ])
      setWeeks(weekData)
      setHeatmapDays(heatmapData.days ?? [])
      fetchPlan()
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <ScrollView
      style={[styles.container, { paddingTop: insets.top }]}
      contentContainerStyle={styles.content}
      refreshControl={
        <RefreshControl
          refreshing={isLoading}
          onRefresh={loadData}
          tintColor={Colors.ember}
        />
      }
    >
      <Text style={styles.screenTitle}>Program</Text>

      <View style={styles.phaseBanner}>
        <Text style={styles.phaseLabel}>CURRENT PHASE</Text>
        <Text style={styles.phaseName}>{phase.name}</Text>
        <Text style={styles.phaseRange}>
          {phase.range} • Week {currentWeek}/13
        </Text>
      </View>

      {plan?.program_name && (
        <Text style={styles.programName}>{plan.program_name}</Text>
      )}

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Weekly Roadmap</Text>
        {Array.from({ length: 13 }, (_, i) => i + 1).map((week) => {
          const weekData = weeks.find((w) => w.week_number === week)
          return (
            <WeekRow
              key={week}
              weekNumber={week}
              completionRate={weekData?.completion_rate ?? 0}
              isCurrent={week === currentWeek}
              onPress={() =>
                router.push(`/(app)/weekly-report/${week}` as never)
              }
            />
          )
        })}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>90-Day Heatmap</Text>
        <HeatmapGrid days={heatmapDays} currentDay={programDay} />
      </View>
    </ScrollView>
  )
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
  screenTitle: {
    color: Colors.bone,
    fontSize: Typography.sizes.title,
    fontWeight: Typography.weights.bold,
    letterSpacing: Typography.letterSpacing.snug,
    marginBottom: Spacing.xl,
  },
  phaseBanner: {
    backgroundColor: Colors.raised,
    borderRadius: Radius.card,
    borderWidth: 0.5,
    borderColor: Colors.emberBorder,
    padding: Spacing.lg,
    marginBottom: Spacing.xl,
    alignItems: "center",
  },
  phaseLabel: {
    color: Colors.ash,
    fontSize: Typography.sizes.label,
    fontWeight: Typography.weights.medium,
    letterSpacing: Typography.letterSpacing.wider,
    marginBottom: Spacing.sm,
  },
  phaseName: {
    color: Colors.ember,
    fontSize: Typography.sizes.title,
    fontWeight: Typography.weights.bold,
  },
  phaseRange: {
    color: Colors.ash,
    fontSize: Typography.sizes.caption,
    marginTop: Spacing.sm,
  },
  programName: {
    color: Colors.boneTint,
    fontSize: Typography.sizes.heading,
    fontWeight: Typography.weights.medium,
    marginBottom: Spacing.xl,
    textAlign: "center",
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
})
