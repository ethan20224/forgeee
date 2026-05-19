import { View, Text, StyleSheet } from "react-native"
import { useSafeAreaInsets } from "react-native-safe-area-context"
import { Colors, Spacing, Typography } from "@/constants/design"
import { useUserStore } from "@/store/userStore"

export default function ProfileScreen() {
  const insets = useSafeAreaInsets()
  const user = useUserStore((s) => s.user)

  return (
    <View style={[styles.container, { paddingTop: insets.top }]}>
      <Text style={styles.title}>Profile</Text>
      <Text style={styles.name}>{user?.name ?? "—"}</Text>
      <Text style={styles.email}>{user?.email ?? "—"}</Text>
      <Text style={styles.meta}>
        Season {user?.season ?? 1} • Day {user?.program_day ?? 1} •{" "}
        {user?.subscription_tier ?? "free"}
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
    marginBottom: Spacing.xl,
  },
  name: {
    color: Colors.bone,
    fontSize: Typography.sizes.heading,
    fontWeight: Typography.weights.medium,
    marginBottom: Spacing.sm,
  },
  email: {
    color: Colors.ash,
    fontSize: Typography.sizes.body,
    marginBottom: Spacing.lg,
  },
  meta: {
    color: Colors.muted,
    fontSize: Typography.sizes.caption,
  },
})
