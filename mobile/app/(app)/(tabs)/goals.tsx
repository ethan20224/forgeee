import { View, Text, StyleSheet } from "react-native"
import { useSafeAreaInsets } from "react-native-safe-area-context"
import { Colors, Spacing, Typography } from "@/constants/design"

export default function GoalsScreen() {
  const insets = useSafeAreaInsets()

  return (
    <View style={[styles.container, { paddingTop: insets.top }]}>
      <Text style={styles.title}>Goals</Text>
      <Text style={styles.subtitle}>
        Challenges and achievements — coming soon
      </Text>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.canvas,
    padding: Spacing.screen,
  },
  title: {
    color: Colors.bone,
    fontSize: Typography.sizes.title,
    fontWeight: Typography.weights.bold,
    marginBottom: Spacing.md,
  },
  subtitle: {
    color: Colors.ash,
    fontSize: Typography.sizes.body,
  },
})
