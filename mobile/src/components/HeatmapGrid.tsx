import { View, Text, StyleSheet } from "react-native"
import { Colors, Radius, Spacing, Typography } from "@/constants/design"
import type { HeatmapDay } from "@/types/api"

interface HeatmapGridProps {
  days: HeatmapDay[]
  currentDay: number
}

export function HeatmapGrid({ days, currentDay }: HeatmapGridProps) {
  const cells = Array.from({ length: 90 }, (_, i) => {
    const dayNum = i + 1
    const dayData = days.find((d) => d.day_number === dayNum)
    return { dayNum, dayData }
  })

  return (
    <View style={styles.container}>
      <View style={styles.grid}>
        {cells.map(({ dayNum, dayData }) => {
          const isCurrent = dayNum === currentDay
          const rate = dayData?.completion_rate ?? 0
          const bgColor = getCellColor(rate, dayNum <= currentDay)

          return (
            <View
              key={dayNum}
              style={[
                styles.cell,
                { backgroundColor: bgColor },
                isCurrent && styles.cellCurrent,
              ]}
            />
          )
        })}
      </View>
      <View style={styles.legend}>
        <Text style={styles.legendText}>0%</Text>
        <View style={styles.legendBar}>
          <View style={[styles.legendSegment, { backgroundColor: Colors.divider }]} />
          <View style={[styles.legendSegment, { backgroundColor: "rgba(212,165,116,0.3)" }]} />
          <View style={[styles.legendSegment, { backgroundColor: "rgba(212,165,116,0.6)" }]} />
          <View style={[styles.legendSegment, { backgroundColor: Colors.ember }]} />
        </View>
        <Text style={styles.legendText}>100%</Text>
      </View>
    </View>
  )
}

function getCellColor(rate: number, isPast: boolean): string {
  if (!isPast) return Colors.surface
  if (rate === 0) return Colors.divider
  if (rate < 33) return "rgba(212,165,116,0.2)"
  if (rate < 66) return "rgba(212,165,116,0.5)"
  return Colors.ember
}

const styles = StyleSheet.create({
  container: {
    marginVertical: Spacing.lg,
  },
  grid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 3,
  },
  cell: {
    width: 14,
    height: 14,
    borderRadius: 2,
  },
  cellCurrent: {
    borderWidth: 1.5,
    borderColor: Colors.bone,
  },
  legend: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    marginTop: Spacing.lg,
    gap: Spacing.md,
  },
  legendBar: {
    flexDirection: "row",
    gap: 2,
  },
  legendSegment: {
    width: 14,
    height: 14,
    borderRadius: 2,
  },
  legendText: {
    color: Colors.ash,
    fontSize: Typography.sizes.label,
  },
})
