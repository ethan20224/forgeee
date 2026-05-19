import { View, Text, StyleSheet } from "react-native"
import Svg, { Circle } from "react-native-svg"
import { Colors, Typography } from "@/constants/design"

interface CompletionRingProps {
  completed: number
  total: number
  size?: number
  strokeWidth?: number
}

export function CompletionRing({
  completed,
  total,
  size = 64,
  strokeWidth = 5,
}: CompletionRingProps) {
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const progress = total > 0 ? completed / total : 0
  const strokeDashoffset = circumference * (1 - progress)

  return (
    <View style={[styles.container, { width: size, height: size }]}>
      <Svg width={size} height={size}>
        <Circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={Colors.divider}
          strokeWidth={strokeWidth}
          fill="none"
        />
        <Circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={Colors.ember}
          strokeWidth={strokeWidth}
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
        />
      </Svg>
      <View style={styles.label}>
        <Text style={styles.count}>
          {completed}/{total}
        </Text>
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    alignItems: "center",
    justifyContent: "center",
  },
  label: {
    position: "absolute",
    alignItems: "center",
    justifyContent: "center",
  },
  count: {
    color: Colors.bone,
    fontSize: Typography.sizes.caption,
    fontWeight: Typography.weights.bold,
  },
})
