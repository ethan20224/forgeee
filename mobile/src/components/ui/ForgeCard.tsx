import { View, StyleSheet, type StyleProp, type ViewStyle } from "react-native"
import { Colors, Radius, Spacing } from "@/constants/design"

interface ForgeCardProps {
  children: React.ReactNode
  style?: StyleProp<ViewStyle>
}

export function ForgeCard({ children, style }: ForgeCardProps) {
  return <View style={[styles.card, style]}>{children}</View>
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: Colors.raised,
    borderWidth: 0.5,
    borderColor: Colors.divider,
    borderRadius: Radius.card,
    padding: Spacing.lg,
  },
})
