# Feature: Gamification (XP, Streaks, Challenges, Badges)

**Actor:** User (Member)
**Phase:** MVP ✅ Done
**Related flows:** [daily-routine-flow.md](../flows/daily-routine-flow.md)
**Implementation:** `src/services/xp/xpService.ts`, `src/services/streak/streakService.ts`, `src/services/challenges/challengeEngine.ts`, `src/constants/levels.ts`, `src/constants/challenges.ts`, `src/constants/badges.ts`, `src/services/firstStrike/firstStrikeService.ts`, `src/hooks/useXP.ts`, `src/hooks/useStreak.ts`, `src/hooks/useChallenges.ts`, `src/hooks/useAchievements.ts`, `src/hooks/useFirstStrike.ts`

## Purpose

Drive daily engagement through XP-based leveling, streak tracking, challenge participation, and badge collection. Every mechanic ties back to actual task completion — no vanity metrics. Gamification reinforces consistency without guilt, making the 90-day program feel like deliberate progress rather than a chore.

## Design Principles

- **No guilt mechanics:** Streaks reset factually, not dramatically. No "you're losing your streak!" language. Streak is just a number.
- **Progress over punishment:** Every mechanic rewards forward motion. There are no penalties or loss mechanics.
- **Ground in reality:** All XP, levels, and badges derive from actual task completion — never from app opens or passive metrics.
- **Visible but not dominant:** Gamification elements complement the core experience, never overshadow coaching and scores.

---

## Subsections

### 6.1 XP System

**Implementation:** `xpService.awardXP(userId, amount)`

Experience points are the primary numeric progression metric. XP is earned exclusively through task completion and challenge milestones.

**XP Values:**

| Event | XP Awarded |
|-------|-----------|
| Task completion (base) | 10 |
| Streak bonus (streak > 3) | +20 per task |
| Challenge completion | 100 |
| Milestone reached (streak milestone) | 250 |
| Cycle check-in | 25 |
| Weekly report (read/viewed) | 15 |

**Award Pipeline:**
1. **Validation:** Amount must be integer, 0 < amount ≤ 500. Throws if invalid.
2. **Fetch:** Read current `total_xp` from `progress` table.
3. **Compute:** `newTotal = currentXP + amount`.
4. **Level Check:** `calculateLevel(newTotal)` determines if level-up occurred.
5. **Write:** Update `progress` with `total_xp = newTotal, level = newLevel` — using optimistic concurrency guard `.eq("total_xp", currentXP)`.
6. **Retry:** If guard fails (concurrent write detected), retry up to 3 times with exponential backoff (100ms, 300ms, 900ms). On each retry, re-read current XP and recompute.
7. **Return:** `{ newTotal, leveledUp, newLevel?, newLevelName? }`.

**Idempotency:**
- XP award is always tied to a specific event (task completion, challenge completion, etc.).
- Task completion has its own idempotency guard (`.eq("is_completed", false)` on update). XP is only awarded when that guard passes.
- Challenge completion is idempotent via the `challenge_progress.status = 'completed'` check.
- No direct guard on the XP award function itself — idempotency is at the event level.

**Display:**
- `XPBar` component at top of home screen (in `StatusStrip`).
- Shows: current level name (e.g., "Initiate"), XP progress bar (fill from 0 to `xpToNextLevel`), current XP / next level XP (e.g., "85 / 100 XP").
- On level-up: `leveledUp` flag triggers a full-screen pulse animation with new level name display (3 seconds).
- Level name changes colour at higher tiers: Initiate (grey), Apex (gold).

**Acceptance Criteria:**
- AC-1.1: 10 XP awarded per task completion.
- AC-1.2: +20 streak bonus when `current_streak > 3`.
- AC-1.3: 100 XP for challenge completion.
- AC-1.4: 250 XP for streak milestones.
- AC-1.5: 25 XP for cycle check-in.
- AC-1.6: 15 XP for viewing weekly report.
- AC-1.7: Invalid amount (≤0, >500, non-integer) throws error.
- AC-1.8: Optimistic concurrency guard prevents race conditions.
- AC-1.9: Retry with backoff (up to 3 attempts).
- AC-1.10: XP bar updates immediately after award.

---

### 6.2 Levels

**Implementation:** `xpService.calculateLevel(totalXP)`

Six levels representing the user's progression through the FORGE system. Each level has an XP threshold and a thematic name.

**Level Table:**

| Level # | Name | Min XP | Cumulative XP to Next |
|---------|------|--------|----------------------|
| 1 | Initiate | 0 | 100 |
| 2 | Foundation | 100 | 300 |
| 3 | Optimizer | 300 | 600 |
| 4 | Contender | 600 | 1000 |
| 5 | Elite | 1000 | 1500 |
| 6 | Apex | 1500 | — (max level) |

**Level Calculation:**
```typescript
function calculateLevel(totalXP: number): { level: number; name: string; nextThreshold: number } {
  // Iterate levels in order, find highest level where totalXP >= minXP
  // Return { level, name, nextThreshold (next level's minXP, or current if max) }
}
```

**XP to Next Level:**
```typescript
function getXPToNextLevel(totalXP: number): number {
  // Returns nextThreshold - totalXP. 0 if at max level.
}
```

**Level-Up Behaviour:**
- `useXP` hook detects level-up by comparing `level` before and after XP award.
- Stores `previousLevel` in state. If `level > previousLevel` after refresh, sets `leveledUp = true`.
- `leveledUp` flag resets after 3 seconds (auto-dismiss of level-up animation).
- Level-up animation: full-screen translucent overlay with teal pulse, new level name in display size (32), fades out after 3 seconds.

**Max Level (Apex):**
- XP continues to accumulate beyond 1500 (there is no cap), but level stays at 6.
- `xpToNextLevel` returns 0 at Apex.
- XP bar at Apex shows "MAX" instead of "to next level".

**Acceptance Criteria:**
- AC-2.1: All 6 levels correctly defined with thresholds.
- AC-2.2: `calculateLevel(0)` returns Initiate/1.
- AC-2.3: `calculateLevel(1500)` returns Apex/6.
- AC-2.4: `getXPToNextLevel` returns correct values at each boundary.
- AC-2.5: Level-up detected when XP crosses threshold.
- AC-2.6: Level-up animation displays correctly for 3 seconds.
- AC-2.7: Apex level shows "MAX" and no next threshold.
- AC-2.8: XP accumulates beyond Apex without error.

---

### 6.3 Streak

**Implementation:** `streakService.updateStreak(userId)`

Consecutive days with at least one task completed. Streak is the core consistency metric — it drives XP bonuses, challenge progress, and milestone celebrations.

**Streak Logic:**
1. Compute today's date string (`YYYY-MM-DD`) in user's local timezone.
2. Fetch `current_streak`, `last_active_date` from `progress` table.
3. **Comparison:**
   - `last_active_date === today` → already counted today, no change. Return current state.
   - `last_active_date === yesterday` (1 day gap) → increment streak by 1.
   - `last_active_date === null` or gap > 1 day → reset streak to 1. Set `wasReset = true` if previous streak > 0.
4. Compute `newLongest = max(newStreak, current_longest)`.
5. Detect milestone: `newStreak ∈ [7, 14, 30, 60, 90]`.
6. Persist: update `progress.current_streak`, `progress.longest_streak`, `progress.last_active_date`.
7. Return: `{ newStreak, longestStreak, isMilestone, milestoneValue?, wasReset }`.

**Milestone Values and Celebrations:**
| Streak | Milestone | Badge Unlocked | XP Awarded |
|--------|-----------|---------------|------------|
| 7 days | First week | streak_7 | — |
| 14 days | Two weeks | streak_14 | 250 |
| 30 days | One month | streak_30 | 250 |
| 60 days | Two months | streak_60 | 250 |
| 90 days | Full season | streak_90 | 250 |

**StreakMilestoneModal:**
- Triggered when `isMilestone === true` in `useStreak` hook.
- Displays: streak number (large, teal), milestone message ("Day 7 — a streak worth noting."), dismiss button.
- Message language: factual, non-guilting, non-hyping. Never "amazing achievement" or "incredible dedication".
- Badge unlock triggered in parallel (non-blocking).
- XP (250) awarded on milestone 14+ via `awardXP`.

**Streak Reset Handling:**
- `wasStreakReset` flag detected in `useStreak` hook using AsyncStorage-persisted `prev_streak` value.
- If previous streak was > 0 and current streak is 0 → `wasStreakReset = true`.
- No special modal/popup on reset — streak indicator simply shows "1" without drama.
- `longestStreak` preserves the high-water mark.

**Streak "At Risk" Detection:**
- `isStreakAtRisk(lastActiveDate)` returns true if user hasn't completed a task today AND yesterday was their last active day.
- Used for internal metrics only (MVP) — no user-facing "at risk" notifications per guilt-free notification policy.
- Streak risk notifications were removed; replaced with factual "tasks available today" in-app messaging.

**Acceptance Criteria:**
- AC-3.1: Consecutive days increment streak correctly.
- AC-3.2: Gap > 1 day resets streak to 1.
- AC-3.3: Same-day repeat task does not change streak.
- AC-3.4: Milestones detected at 7, 14, 30, 60, 90.
- AC-3.5: Milestone modal displays with factual language.
- AC-3.6: `longestStreak` preserves high-water mark.
- AC-3.7: `wasReset` flag set on streak reset.
- AC-3.8: No guilt language in streak UI or modals.
- AC-3.9: Streak data persists correctly across app restarts.

---

### 6.4 Challenges

**Implementation:** `challengeEngine.ts` — `startChallenge`, `onTaskComplete`, `onCycleCheckIn`, `getActiveChallenges`, `checkChallengeComplete`

Structured goal-tracking system that auto-advances based on user activity. Challenges provide medium-term engagement targets beyond daily tasks.

**Challenge Catalogue** (`src/constants/challenges.ts`):

| ID | Name | Type | Target | XP Reward | Trigger |
|----|------|------|--------|-----------|---------|
| `streak_defend_7` | 7-Day Streak Defend | streak | 7 days | 150 | Streak reaches 7 |
| `streak_defend_14` | 14-Day Streak Defend | streak | 14 days | 300 | Streak reaches 14 |
| `skin_transformation` | Skin Transformation | task_count | 30 tasks | 250 | Any skin task completed |
| `season_complete` | Season 1 Complete | season | 90 days | 500 | program_day reaches 90 |
| `grooming_week` | Grooming Week | task_count | 7 tasks | 200 | Any grooming task completed |

**Challenge Types:**
- **`streak`:** Progress is the user's current streak. Updated on cycle check-in via `onCycleCheckIn`. Not updated on individual task completion (streak challenges track the streak itself, not tasks).
- **`task_count`:** Progress increments by 1 for each matching task completion. Matching logic:
  - `skin_transformation`: matches tasks with `category === "skin"`.
  - `grooming_week`: matches tasks with `category === "grooming"`.
  - Generic: any task completion advances.
- **`season`:** Triggers when program day reaches 90 (season complete). Updated via `onCycleCheckIn` or season rollover handler.

**Challenge Lifecycle:**
1. **Start:** `startChallenge(userId, challengeId)` — creates `challenge_progress` row with `status = 'active', progress = 0, target = challenge.target`.
   - Checks for existing active challenge (prevents duplicates).
   - Throws "This challenge is already in progress or completed." if duplicate.
2. **Progress:** Auto-advances on task completion via `onTaskComplete(userId, task)`:
   - Fetches all active challenges.
   - For each, checks if completed task matches challenge criteria.
   - Increments progress by 1 for matching challenges.
   - Checks if progress ≥ target → calls `completeChallenge`.
3. **Complete:** `completeChallenge(userId, challengeId)`:
   - Updates `challenge_progress` to `status = 'completed', progress = target, completed_at = NOW()`.
   - Awards XP via `awardXP(userId, challenge.xpReward)`.
   - Unlocks corresponding badge via `unlockBadge(userId, badgeId)`.
   - Badge unlock is non-blocking — failure doesn't prevent challenge completion.

**Challenge Progress Display:**
- `Goals` tab shows active and completed challenges.
- Each active challenge shows: name, description, progress bar (progress/target), XP reward badge.
- Completed challenges show: name, completed date, checkmark icon, XP awarded.
- "Start Challenge" CTA for challenges not yet started.

**Acceptance Criteria:**
- AC-4.1: All 5 challenges defined in catalogue.
- AC-4.2: Challenge starts with correct target and XP reward.
- AC-4.3: Duplicate start prevented.
- AC-4.4: Task completion auto-advances matching challenges.
- AC-4.5: Streak challenges update on cycle check-in.
- AC-4.6: Challenge completion awards XP.
- AC-4.7: Challenge completion unlocks corresponding badge.
- AC-4.8: Badge unlock failure doesn't block challenge completion.
- AC-4.9: Goals screen shows active and completed challenges correctly.

---

### 6.5 Badges

**Implementation:** `challengeEngine.unlockBadge(userId, badgeId)` → `achievements` table

Visual achievements unlocked through challenge completion and milestone attainment. Badges are displayed on the Goals tab and provide social proof.

**Badge Catalogue** (`src/constants/badges.ts`):

| ID | Name | Description | XP Reward |
|----|------|-------------|-----------|
| `streak_7` | 7-Day Streak | Complete 7 consecutive days | 150 |
| `streak_14` | 14-Day Streak | Maintain streak for 14 consecutive days | 300 |
| `streak_30` | 30-Day Streak | Hit a 30-day streak milestone | 500 |
| `streak_60` | 60-Day Streak | Reach a 60-day streak | 1000 |
| `streak_90` | 90-Day Streak | Achieve the maximum streak | 2000 |
| `skin_transformation` | Skin Transformation | Complete 30 skin-focused tasks | 250 |
| `season_complete` | Season 1 Complete | Complete your first full Season | 500 |
| `grooming_week` | Grooming Week | Complete all grooming tasks for 7 days | 200 |

**Unlock Mechanism:**
1. `unlockBadge(userId, badgeId)`:
   - Checks if badge already awarded: `SELECT * FROM achievements WHERE user_id = X AND badge_id = Y`.
   - If exists: return (idempotent).
   - If not: insert row `{ user_id, badge_id, unlocked_at: NOW() }` into `achievements` table.
2. Database constraint: `UNIQUE(user_id, badge_id)` on `achievements` prevents duplicate awards.
3. Badge is always unlocked as a side effect of challenge completion or milestone reached — never independently.

**Display:**
- `Goals` tab shows "Achievements" section with badge grid.
- Each badge: icon, name, unlocked date (or "Locked" overlay if not yet earned).
- Locked badges shown with reduced opacity and lock icon.
- Unlocked badges shown full colour with subtle glow effect.
- Total unlocked count displayed: "8 badges earned" or "3 of 8 unlocked".

**Acceptance Criteria:**
- AC-5.1: All 8 badges defined in catalogue.
- AC-5.2: Badge unlocked on challenge completion.
- AC-5.3: Badge unlocked on milestone reached.
- AC-5.4: UNIQUE constraint prevents duplicate awards.
- AC-5.5: Unlocked badges display full colour on Goals tab.
- AC-5.6: Locked badges display reduced opacity.
- AC-5.7: Badge awarded count displayed correctly.

---

### 6.6 First Strike

**Implementation:** `firstStrikeService.ts` — `evaluateFirstStrike`, `completeFirstStrike` — triggered on day 1 first task completion.

A special day-1 celebration module that combines micro-score disclosure with AI-generated insight. Designed to create a memorable "first moment of progress" that hooks the user.

**Trigger Conditions:**
- `programDay === 1` (first day).
- First task completion event.
- `users.first_strike_completed === false`.

**Pipeline:**
1. Check eligibility: `evaluateFirstStrike(userId)` — returns `{ allCompleted: false }` if first strike not yet done.
2. Complete: `completeFirstStrike(userId)`:
   a. Set `users.first_strike_completed = true`.
   b. Read current `optimisation_score` from progress.
   c. Compute `microScore = min(optimisation_score + 5, 100)` — a slight bump to reflect immediate progress.
   d. Update `progress.optimisation_score = microScore`.
   e. Call Claude with `FIRST_STRIKE_SYSTEM_PROMPT` for one-sentence insight.
   f. Fallback insight: "You already changed something. Before day 1 ends."

**AI Insight Generation:**
```
System Prompt: "You are FORGE's First Strike insight engine. A user just completed
Day 1 — three quick tasks that produced visible change: Face wash ritual (skin care),
Brow cleanup (grooming), Posture reset (posture). Write ONE sentence celebrating this.
Keep it grounded and real, not hype. No exclamation marks. Never say 'great job',
'keep it up', 'you're doing amazing', 'consistency is key'.
Example tone: 'You already changed something. Before day 1 ends.'
Respond with ONLY the sentence. No quotes."
```

**FirstStrikeModal Component:**
- Full-screen overlay triggered after day 1 first task completion.
- Headline: "First Strike — Day 1" (display size, 32).
- Micro-score: animated number counting up from current score to `microScore`.
- AI insight: one sentence, secondary text colour, centred.
- "Continue" button dismisses modal.
- One-time display — never shown again after completion.

**Acceptance Criteria:**
- AC-6.1: First Strike triggers only on day 1, first task, and only once.
- AC-6.2: `first_strike_completed` flag prevents re-trigger.
- AC-6.3: Micro-score computed as min(score + 5, 100).
- AC-6.4: AI insight is one sentence, grounded, non-hype.
- AC-6.5: Fallback insight used on Claude failure.
- AC-6.6: Modal dismisses on Continue tap.
- AC-6.7: Progress `optimisation_score` updated.

---

### 6.7 Micro-Sprints

**Implementation:** `src/services/sprints/microSprintEngine.ts`, `src/constants/microSprints.ts`

7-day task overrides that replace standard daily tasks with focused sprint objectives. Triggered by cycle check-in results (stalled pillar detection) or user choice from the sprints tab.

**Sprint Types:**
| Sprint | Trigger | Description |
|--------|---------|-------------|
| **Skin Reset** | Stalled skin score, or user choice | 7 days of intensive skin care tasks |
| **Posture Fix** | Stalled posture score, or user choice | Daily posture reset exercises and awareness |
| **Grooming Intensive** | Stalled grooming score, or user choice | Advanced grooming routine for 7 days |
| **Style Upgrade** | User choice only | 7-day wardrobe audit and style refinement |

**Sprint Lifecycle:**
1. **Detection:** After cycle check-in, if a pillar score has stalled (< 1 point change over 2 cycles), the cycle result screen shows a sprint suggestion: "Your skin score hasn't moved much — try a 7-day Skin Reset sprint."
2. **Selection:** User taps suggestion → `SprintSelectionModal` shows sprint details (tasks, duration, expected outcome). User confirms or declines.
3. **Activation:** `startSprint(userId, sprintId)` stores active sprint in `micro_sprints` table (JSONB with sprint config + task overrides).
4. **Duration:** 7 days. Sprint tasks replace standard daily tasks in the `daily_tasks` table (inserted as day_number rows for the sprint period).
5. **Display:** Sprint detail screen (`app/(app)/sprint-detail.tsx`) shows sprint progress, daily tasks, remaining days.
6. **Completion:** After 7 days, sprint auto-completes. Progress returns to standard plan tasks. Sprint badge awarded.
7. **Cancellation:** User can cancel sprint early from sprint detail screen. Reverts to standard tasks.

**Sprint-Specific XP:**
- Sprint tasks award standard XP (10 per task).
- Sprint completion bonus: 100 XP.
- Sprint badge awarded on completion.

**Acceptance Criteria:**
- AC-7.1: Sprint suggested when pillar score stalls for 2+ cycles.
- AC-7.2: Sprint selection modal shows task list and expected outcome.
- AC-7.3: Sprint replaces standard tasks for 7 days.
- AC-7.4: Sprint progress tracked on detail screen.
- AC-7.5: Sprint auto-completes after 7 days.
- AC-7.6: Sprint cancellation reverts to standard tasks.
- AC-7.7: Sprint completion awards XP and badge.
- AC-7.8: Sprint tasks use standard task completion pipeline (XP, streak, drift).
