import { View, Text, ScrollView, StyleSheet, Switch } from "react-native"
import { useState } from "react"
import { useSafeAreaInsets } from "react-native-safe-area-context"
import { Pressable } from "react-native"
import { router } from "expo-router"
import { Ionicons } from "@expo/vector-icons"
import { Colors, Spacing, Typography, Radius } from "@/constants/design"

export default function SettingsScreen() {
  const insets = useSafeAreaInsets()
  const [notificationsEnabled, setNotificationsEnabled] = useState(true)
  const [dailyReminders, setDailyReminders] = useState(true)

  return (
    <View style={[styles.container, { paddingTop: insets.top + Spacing.lg }]}>
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={24} color={Colors.bone} />
        </Pressable>
        <Text style={styles.title}>Settings</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.content}>
        <Text style={styles.sectionTitle}>Notifications</Text>
        <View style={styles.card}>
          <SettingRow
            label="Push Notifications"
            value={notificationsEnabled}
            onToggle={setNotificationsEnabled}
          />
          <View style={styles.divider} />
          <SettingRow
            label="Daily Reminders"
            value={dailyReminders}
            onToggle={setDailyReminders}
          />
        </View>

        <Text style={styles.sectionTitle}>About</Text>
        <View style={styles.card}>
          <InfoRow label="Version" value="1.0.0" />
          <View style={styles.divider} />
          <InfoRow label="Build" value="2026.05.19" />
        </View>

        <Text style={styles.sectionTitle}>Legal</Text>
        <View style={styles.card}>
          <LinkRow label="Privacy Policy" />
          <View style={styles.divider} />
          <LinkRow label="Terms of Service" />
        </View>
      </ScrollView>
    </View>
  )
}

function SettingRow({
  label,
  value,
  onToggle,
}: {
  label: string
  value: boolean
  onToggle: (v: boolean) => void
}) {
  return (
    <View style={styles.row}>
      <Text style={styles.rowLabel}>{label}</Text>
      <Switch
        value={value}
        onValueChange={onToggle}
        trackColor={{ false: Colors.surface, true: Colors.ember }}
        thumbColor={Colors.bone}
      />
    </View>
  )
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.row}>
      <Text style={styles.rowLabel}>{label}</Text>
      <Text style={styles.rowValue}>{value}</Text>
    </View>
  )
}

function LinkRow({ label }: { label: string }) {
  return (
    <Pressable style={styles.row}>
      <Text style={styles.rowLabel}>{label}</Text>
      <Ionicons name="chevron-forward" size={16} color={Colors.muted} />
    </Pressable>
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
  content: {
    paddingBottom: 60,
  },
  sectionTitle: {
    fontSize: Typography.sizes.caption,
    fontWeight: Typography.weights.bold,
    color: Colors.ash,
    textTransform: "uppercase",
    letterSpacing: Typography.letterSpacing.wide,
    marginBottom: Spacing.md,
    marginTop: Spacing.xl,
  },
  card: {
    backgroundColor: Colors.raised,
    borderRadius: Radius.card,
    overflow: "hidden",
  },
  row: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.lg - 2,
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
})
