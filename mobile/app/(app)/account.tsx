import { View, Text, StyleSheet, Pressable, Alert } from "react-native"
import { router } from "expo-router"
import { useSafeAreaInsets } from "react-native-safe-area-context"
import { Ionicons } from "@expo/vector-icons"
import { Colors, Spacing, Typography, Radius } from "@/constants/design"
import { useUserStore } from "@/store/userStore"
import { api } from "@/api/client"

export default function AccountScreen() {
  const insets = useSafeAreaInsets()
  const user = useUserStore((s) => s.user)
  const signOut = useUserStore((s) => s.signOut)

  const handleDeleteAccount = () => {
    Alert.alert(
      "Delete Account",
      "This will permanently delete all your data. This action cannot be undone.",
      [
        { text: "Cancel", style: "cancel" },
        {
          text: "Delete",
          style: "destructive",
          onPress: async () => {
            try {
              await api.del("/auth/account")
              await signOut()
              router.replace("/(auth)/landing")
            } catch (e: any) {
              Alert.alert("Error", e.message || "Failed to delete account")
            }
          },
        },
      ],
    )
  }

  return (
    <View style={[styles.container, { paddingTop: insets.top + Spacing.lg }]}>
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={24} color={Colors.bone} />
        </Pressable>
        <Text style={styles.title}>Account</Text>
        <View style={{ width: 40 }} />
      </View>

      <View style={styles.card}>
        <View style={styles.row}>
          <Text style={styles.rowLabel}>Email</Text>
          <Text style={styles.rowValue}>{user?.email ?? "—"}</Text>
        </View>
        <View style={styles.divider} />
        <View style={styles.row}>
          <Text style={styles.rowLabel}>Name</Text>
          <Text style={styles.rowValue}>{user?.name ?? "—"}</Text>
        </View>
        <View style={styles.divider} />
        <View style={styles.row}>
          <Text style={styles.rowLabel}>Member since</Text>
          <Text style={styles.rowValue}>
            {user?.created_at
              ? new Date(user.created_at).toLocaleDateString()
              : "—"}
          </Text>
        </View>
      </View>

      <View style={styles.dangerZone}>
        <Text style={styles.dangerTitle}>Danger Zone</Text>
        <Pressable style={styles.deleteBtn} onPress={handleDeleteAccount}>
          <Ionicons name="trash-outline" size={18} color={Colors.danger} />
          <Text style={styles.deleteText}>Delete Account</Text>
        </Pressable>
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.canvas,
    paddingHorizontal: Spacing.screen,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: Spacing.xl,
  },
  backBtn: {
    width: 40,
    height: 40,
    justifyContent: "center",
    alignItems: "center",
  },
  title: {
    fontSize: Typography.sizes.heading,
    fontWeight: Typography.weights.bold,
    color: Colors.bone,
  },
  card: {
    backgroundColor: Colors.raised,
    borderRadius: Radius.card,
    overflow: "hidden",
    marginBottom: Spacing.xxxl,
  },
  row: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.lg,
  },
  rowLabel: {
    fontSize: Typography.sizes.body,
    color: Colors.bone,
  },
  rowValue: {
    fontSize: Typography.sizes.body,
    color: Colors.ash,
  },
  divider: {
    height: 1,
    backgroundColor: Colors.divider,
    marginHorizontal: Spacing.lg,
  },
  dangerZone: {
    gap: Spacing.lg,
  },
  dangerTitle: {
    fontSize: Typography.sizes.caption,
    fontWeight: Typography.weights.bold,
    color: Colors.danger,
    textTransform: "uppercase",
    letterSpacing: Typography.letterSpacing.wide,
  },
  deleteBtn: {
    flexDirection: "row",
    alignItems: "center",
    gap: Spacing.md,
    backgroundColor: Colors.dangerDim,
    borderRadius: Radius.lg,
    paddingVertical: Spacing.lg,
    paddingHorizontal: Spacing.xl,
    borderWidth: 1,
    borderColor: "rgba(232,69,69,0.20)",
  },
  deleteText: {
    fontSize: Typography.sizes.body,
    fontWeight: Typography.weights.bold,
    color: Colors.danger,
  },
})
