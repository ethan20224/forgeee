import { useEffect, useState } from "react"
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  Pressable,
  ActivityIndicator,
} from "react-native"
import { router } from "expo-router"
import { useSafeAreaInsets } from "react-native-safe-area-context"
import { Ionicons } from "@expo/vector-icons"
import { Colors, Spacing, Typography, Radius } from "@/constants/design"
import { useCycleStore } from "@/store/cycleStore"
import { getAchievements, getChallenges, getXPInfo, startChallenge } from "@/api/gamification"
import { XPBar } from "@/components/XPBar"
import { ChallengeCard } from "@/components/ChallengeCard"
import { AchievementBadge } from "@/components/AchievementBadge"
import type {
  AchievementsResponse,
  ChallengesListResponse,
  XPInfoResponse,
} from "@/types/api"

export default function GoalsScreen() {
  const insets = useSafeAreaInsets()
  const { eligibility, history, fetchEligibility, fetchHistory } = useCycleStore()

  const [xp, setXP] = useState<XPInfoResponse | null>(null)
  const [achievements, setAchievements] = useState<AchievementsResponse | null>(null)
  const [challenges, setChallenges] = useState<ChallengesListResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      fetchEligibility(),
      fetchHistory(),
      getXPInfo().then(setXP),
      getAchievements().then(setAchievements),
      getChallenges().then(setChallenges),
    ]).finally(() => setLoading(false))
  }, [])

  const handleStartChallenge = async (challengeId: string) => {
    try {
      await startChallenge(challengeId)
      const updated = await getChallenges()
      setChallenges(updated)
    } catch {}
  }

  if (loading) {
    return (
      <View style={[styles.center, { paddingTop: insets.top + 100 }]}>
        <ActivityIndicator size="large" color={Colors.ember} />
      </View>
    )
  }

  const unlockedBadges = achievements?.badges.filter((b) => b.unlocked) ?? []
  const lockedBadges = achievements?.badges.filter((b) => !b.unlocked).slice(0, 6) ?? []

  return (
    <ScrollView
      style={[styles.container, { paddingTop: insets.top }]}
      contentContainerStyle={styles.content}
      showsVerticalScrollIndicator={false}
    >
      <Text style={styles.title}>Goals</Text>

      {/* XP Bar */}
      {xp && (
        <View style={styles.section}>
          <XPBar
            totalXp={xp.total_xp}
            currentLevel={xp.current_level}
            levelName={xp.level_name}
            xpProgress={xp.xp_progress}
            xpNeeded={xp.xp_needed}
            progressPct={xp.progress_pct}
          />
        </View>
      )}

      {/* Cycle Check-in CTA */}
      <Pressable
        style={[
          styles.checkinBtn,
          eligibility && !eligibility.eligible && styles.checkinBtnDisabled,
        ]}
        onPress={() => router.push("/(app)/cycle-checkin")}
        disabled={eligibility !== null && !eligibility.eligible}
      >
        <Ionicons name="camera" size={20} color={Colors.canvas} />
        <Text style={styles.checkinBtnText}>
          {eligibility?.eligible !== false ? "New Cycle Check-in" : "Check-in Locked"}
        </Text>
      </Pressable>
      {eligibility && !eligibility.eligible && eligibility.reason && (
        <Text style={styles.cooldownText}>{eligibility.reason}</Text>
      )}

      {/* Active Challenges */}
      {challenges && challenges.active.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Active Challenges</Text>
          <View style={styles.cardList}>
            {challenges.active.map((c) => (
              <ChallengeCard key={c.id || c.challenge_id} challenge={c} />
            ))}
          </View>
        </View>
      )}

      {/* Available Challenges */}
      {challenges && challenges.available.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Available Challenges</Text>
          <View style={styles.cardList}>
            {challenges.available.map((c) => (
              <ChallengeCard
                key={c.challenge_id}
                challenge={c}
                onStart={() => handleStartChallenge(c.challenge_id)}
              />
            ))}
          </View>
        </View>
      )}

      {/* Achievements */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Achievements</Text>
          <Text style={styles.badgeCount}>
            {achievements?.total_unlocked ?? 0}/{achievements?.total_available ?? 0}
          </Text>
        </View>

        {unlockedBadges.length > 0 && (
          <View style={styles.badgeGrid}>
            {unlockedBadges.slice(0, 8).map((badge) => (
              <AchievementBadge key={badge.badge_id} badge={badge} />
            ))}
          </View>
        )}

        {lockedBadges.length > 0 && (
          <View style={styles.badgeGrid}>
            {lockedBadges.map((badge) => (
              <AchievementBadge key={badge.badge_id} badge={badge} />
            ))}
          </View>
        )}
      </View>

      {/* Cycle History */}
      {history.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Cycle History</Text>
          <View style={styles.cardList}>
            {history.slice(0, 5).map((cycle) => (
              <Pressable
                key={cycle.cycle_id}
                style={styles.cycleRow}
                onPress={() =>
                  router.push({
                    pathname: "/(app)/cycle-result",
                    params: { cycleId: cycle.cycle_id },
                  })
                }
              >
                <View style={styles.cycleLeft}>
                  <Text style={styles.cycleNumber}>#{cycle.cycle_number}</Text>
                  <Text style={styles.cycleDate}>
                    {new Date(cycle.checked_in_at).toLocaleDateString()}
                  </Text>
                </View>
                <View style={styles.cycleRight}>
                  {cycle.optimisation_score !== null && (
                    <Text style={styles.cycleScore}>
                      {Math.round(cycle.optimisation_score)}
                    </Text>
                  )}
                  <Ionicons name="chevron-forward" size={16} color={Colors.muted} />
                </View>
              </Pressable>
            ))}
          </View>
        </View>
      )}
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
    paddingBottom: 100,
  },
  center: {
    flex: 1,
    backgroundColor: Colors.canvas,
    justifyContent: "center",
    alignItems: "center",
  },
  title: {
    color: Colors.bone,
    fontSize: Typography.sizes.title,
    fontWeight: Typography.weights.bold,
    marginBottom: Spacing.xl,
  },
  section: {
    marginBottom: Spacing.xl,
  },
  sectionHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: Spacing.lg,
  },
  sectionTitle: {
    fontSize: Typography.sizes.heading,
    fontWeight: Typography.weights.bold,
    color: Colors.bone,
    marginBottom: Spacing.lg,
  },
  badgeCount: {
    fontSize: Typography.sizes.caption,
    color: Colors.ash,
  },
  cardList: {
    gap: Spacing.md,
  },
  badgeGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: Spacing.lg,
    marginBottom: Spacing.lg,
  },
  checkinBtn: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: Spacing.md,
    backgroundColor: Colors.ember,
    borderRadius: Radius.lg,
    paddingVertical: Spacing.lg,
    marginBottom: Spacing.md,
  },
  checkinBtnDisabled: {
    opacity: 0.4,
  },
  checkinBtnText: {
    fontSize: Typography.sizes.body,
    fontWeight: Typography.weights.bold,
    color: Colors.canvas,
  },
  cooldownText: {
    fontSize: Typography.sizes.label,
    color: Colors.ash,
    textAlign: "center",
    marginBottom: Spacing.lg,
  },
  cycleRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    backgroundColor: Colors.raised,
    borderRadius: Radius.card,
    padding: Spacing.lg,
  },
  cycleLeft: {
    gap: Spacing.xs,
  },
  cycleNumber: {
    fontSize: Typography.sizes.body,
    fontWeight: Typography.weights.bold,
    color: Colors.bone,
  },
  cycleDate: {
    fontSize: Typography.sizes.label,
    color: Colors.ash,
  },
  cycleRight: {
    flexDirection: "row",
    alignItems: "center",
    gap: Spacing.md,
  },
  cycleScore: {
    fontSize: Typography.sizes.heading,
    fontWeight: Typography.weights.bold,
    color: Colors.ember,
  },
})
