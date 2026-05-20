import { useEffect, useState } from "react"
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  Pressable,
} from "react-native"
import { router } from "expo-router"
import { useSafeAreaInsets } from "react-native-safe-area-context"
import { Ionicons } from "@expo/vector-icons"
import { Colors, Spacing, Typography, Radius } from "@/constants/design"
import { useUserStore } from "@/store/userStore"
import { useProgressStore } from "@/store/progressStore"
import { getSubscriptionStatus, SubscriptionStatus } from "@/api/subscriptions"
import { getXPInfo } from "@/api/gamification"
import type { XPInfoResponse } from "@/types/api"

const TIER_LABELS: Record<string, string> = {
  none: "Free",
  pro: "Pro",
  premium: "Premium",
}

export default function ProfileScreen() {
  const insets = useSafeAreaInsets()
  const user = useUserStore((s) => s.user)
  const { currentStreak, totalXp, fetchProgress } = useProgressStore()
  const [subscription, setSubscription] = useState<SubscriptionStatus | null>(null)
  const [xpInfo, setXPInfo] = useState<XPInfoResponse | null>(null)

  useEffect(() => {
    fetchProgress()
    getSubscriptionStatus().then(setSubscription).catch(() => {})
    getXPInfo().then(setXPInfo).catch(() => {})
  }, [])

  const tierLabel = TIER_LABELS[subscription?.tier ?? user?.subscription_tier ?? "none"] ?? "Free"

  return (
    <ScrollView
      style={[styles.container, { paddingTop: insets.top }]}
      contentContainerStyle={styles.content}
      showsVerticalScrollIndicator={false}
    >
      <Text style={styles.title}>Profile</Text>

      {/* Avatar / Identity */}
      <View style={styles.avatarSection}>
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>
            {(user?.name?.[0] ?? user?.email?.[0] ?? "?").toUpperCase()}
          </Text>
        </View>
        <View style={styles.identity}>
          <Text style={styles.name}>{user?.name ?? "—"}</Text>
          <Text style={styles.email}>{user?.email ?? "—"}</Text>
        </View>
        <View style={styles.tierBadge}>
          <Text style={styles.tierText}>{tierLabel}</Text>
        </View>
      </View>

      {/* Stats Row */}
      <View style={styles.statsRow}>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>
            {user?.season ?? 1}
          </Text>
          <Text style={styles.statLabel}>Season</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>
            {user?.program_day ?? 1}
          </Text>
          <Text style={styles.statLabel}>Day</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>{currentStreak}</Text>
          <Text style={styles.statLabel}>Streak</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>
            {xpInfo?.current_level ?? 1}
          </Text>
          <Text style={styles.statLabel}>Level</Text>
        </View>
      </View>

      {/* XP */}
      {xpInfo && (
        <View style={styles.xpSection}>
          <Text style={styles.xpLabel}>
            {xpInfo.level_name} — {xpInfo.total_xp.toLocaleString()} XP
          </Text>
          <View style={styles.xpTrack}>
            <View style={[styles.xpFill, { width: `${Math.min(xpInfo.progress_pct, 100)}%` as any }]} />
          </View>
          <Text style={styles.xpNext}>
            {xpInfo.xp_progress}/{xpInfo.xp_needed} to next level
          </Text>
        </View>
      )}

      {/* Menu Items */}
      <View style={styles.menu}>
        <MenuItem
          icon="settings-outline"
          label="Settings"
          onPress={() => router.push("/(app)/settings")}
        />
        <MenuItem
          icon="person-outline"
          label="Account"
          onPress={() => router.push("/(app)/account")}
        />
        <MenuItem
          icon="log-out-outline"
          label="Sign Out"
          onPress={async () => {
            await useUserStore.getState().signOut()
            router.replace("/(auth)/login")
          }}
          destructive
        />
      </View>
    </ScrollView>
  )
}

function MenuItem({
  icon,
  label,
  onPress,
  destructive = false,
}: {
  icon: string
  label: string
  onPress: () => void
  destructive?: boolean
}) {
  return (
    <Pressable style={styles.menuItem} onPress={onPress}>
      <Ionicons
        name={icon as any}
        size={20}
        color={destructive ? Colors.danger : Colors.bone}
      />
      <Text style={[styles.menuLabel, destructive && styles.menuLabelDanger]}>
        {label}
      </Text>
      <Ionicons name="chevron-forward" size={16} color={Colors.muted} />
    </Pressable>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.canvas,
  },
  content: {
    padding: Spacing.screen,
    paddingBottom: 100,
  },
  title: {
    color: Colors.bone,
    fontSize: Typography.sizes.title,
    fontWeight: Typography.weights.bold,
    marginBottom: Spacing.xl,
  },
  avatarSection: {
    flexDirection: "row",
    alignItems: "center",
    gap: Spacing.lg,
    marginBottom: Spacing.xl,
  },
  avatar: {
    width: 52,
    height: 52,
    borderRadius: 26,
    backgroundColor: Colors.emberDim,
    borderWidth: 1.5,
    borderColor: Colors.emberBorder,
    justifyContent: "center",
    alignItems: "center",
  },
  avatarText: {
    fontSize: Typography.sizes.title,
    fontWeight: Typography.weights.bold,
    color: Colors.ember,
  },
  identity: {
    flex: 1,
    gap: 2,
  },
  name: {
    fontSize: Typography.sizes.heading,
    fontWeight: Typography.weights.bold,
    color: Colors.bone,
  },
  email: {
    fontSize: Typography.sizes.caption,
    color: Colors.ash,
  },
  tierBadge: {
    backgroundColor: Colors.emberDim,
    borderRadius: Radius.full,
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.sm + 2,
    borderWidth: 1,
    borderColor: Colors.emberBorder,
  },
  tierText: {
    fontSize: Typography.sizes.label,
    fontWeight: Typography.weights.bold,
    color: Colors.ember,
  },
  statsRow: {
    flexDirection: "row",
    gap: Spacing.md,
    marginBottom: Spacing.xl,
  },
  statCard: {
    flex: 1,
    backgroundColor: Colors.raised,
    borderRadius: Radius.card,
    paddingVertical: Spacing.lg,
    alignItems: "center",
    gap: Spacing.xs,
  },
  statValue: {
    fontSize: Typography.sizes.title,
    fontWeight: Typography.weights.bold,
    color: Colors.bone,
  },
  statLabel: {
    fontSize: Typography.sizes.label,
    color: Colors.ash,
  },
  xpSection: {
    backgroundColor: Colors.raised,
    borderRadius: Radius.card,
    padding: Spacing.lg,
    gap: Spacing.md,
    marginBottom: Spacing.xl,
  },
  xpLabel: {
    fontSize: Typography.sizes.caption,
    fontWeight: Typography.weights.bold,
    color: Colors.bone,
  },
  xpTrack: {
    height: 6,
    backgroundColor: Colors.surface,
    borderRadius: Radius.full,
    overflow: "hidden",
  },
  xpFill: {
    height: "100%",
    backgroundColor: Colors.ember,
    borderRadius: Radius.full,
  },
  xpNext: {
    fontSize: Typography.sizes.label,
    color: Colors.ash,
  },
  menu: {
    gap: Spacing.sm,
  },
  menuItem: {
    flexDirection: "row",
    alignItems: "center",
    gap: Spacing.lg,
    backgroundColor: Colors.raised,
    borderRadius: Radius.card,
    padding: Spacing.lg,
  },
  menuLabel: {
    flex: 1,
    fontSize: Typography.sizes.body,
    color: Colors.bone,
  },
  menuLabelDanger: {
    color: Colors.danger,
  },
})
