# Feature: Daily Tasks

**Actor:** User (Member)
**Phase:** MVP ✅ Done
**Related flows:** [daily-routine-flow.md](../flows/daily-routine-flow.md)
**Implementation:** `app/(app)/(tabs)/index.tsx`, `app/(app)/task/[taskId].tsx`, `src/hooks/useTasks.ts`, `src/hooks/useTodaysTasks.ts`, `src/services/tasks/taskEngine.ts`, `src/components/ui/TaskCard.tsx`

## Purpose

Deliver 2-5 curated daily tasks to the user, allow completion with immediate feedback (XP, streak, challenge progress, pillar score drift), and surface the task's "why it works" context. Daily tasks are the core engagement loop — every game mechanic, score, and coaching insight flows from task completion.

## Data Model

Tasks are stored in the `daily_tasks` Supabase table. Each row represents one task for one user on one program day (of 90).

| Column | Type | Description |
|--------|------|-------------|
| `id` | uuid | Primary key |
| `user_id` | uuid | FK to users |
| `plan_id` | uuid | FK to plans |
| `title` | text | Task title (clinical/descriptive) |
| `category` | text | Task category (skin, grooming, hair, posture, style, sleep, nutrition) |
| `why_it_works` | text | Short explanation of mechanism |
| `duration_mins` | integer | Estimated time to complete |
| `day_number` | integer | Program day (1-90) |
| `xp_value` | integer | XP awarded (default 10) |
| `is_completed` | boolean | Completion status |
| `completed_at` | timestamptz | When completed (null if not completed) |
| `library_task_id` | text | FK to Master Task Library entry |
| `pillar` | text | Primary pillar this task improves |
| `tier` | text | Task tier (beginner, intermediate, advanced) |
| `week_number` | integer | Program week (1-13) |
| `created_at` | timestamptz | When row was created |

Master Task Library entries (`src/constants/taskLibrary.ts`) provide enriched data joined at runtime: `outcomeTitle` (user-facing benefit title), `whyShort` (one-line why it works), `whyItWorks` (expanded explanation).

---

## Subsections

### 2.1 Task Display

**Screen:** `app/(app)/(tabs)/index.tsx` (Home tab)

Tasks loaded via `useTasks()` → `useProgramStore.loadTodaysTasks(userId)` → `taskEngine.getTodaysTasks(userId, programDay)`.

**Loading:**
- `getTodaysTasks` queries `daily_tasks` where `user_id = userId AND day_number = programDay`.
- Ordered: `is_completed ASC` (incomplete first), then `duration_mins ASC` (shortest first).
- Tasks are enriched with `outcomeTitle` from `TASK_LIBRARY` if `library_task_id` is present.
- During fetch, 3 skeleton `TaskCard` placeholders pulse with gradient animation.

**Display (Each TaskCard):**
- **Title:** `outcomeTitle` if available and `day < 57` (phase names visible), otherwise `title`. Always imported from the library — never the clinical `daily_tasks.title`.
- **Pillar Badge:** Small coloured badge showing the pillar name from `PILLAR_DISPLAY`. Colour from design tokens (`Colors.pillars[pillar]`).
- **Duration:** "5 min" / "15 min" / "30 min" / "60 min" formatted from `duration_mins`.
- **XP Value:** "+10 XP" / "+15 XP" badge (small, muted colour).
- **Why It Works:** Collapsed by default — shown on tap (expandable section). One-line `whyShort` shown initially; expanded shows `whyItWorks` full text.
- **Category Dots:** If `showCategoryDots(day)` is true (days 15-28), pill-shaped category indicators replace full category names.
- **Category Names:** If `showCategoryNames(day)` is true (day 29+), full category names display. Controlled by `src/lib/languageStage.ts`.

**Empty State:**
- "No tasks for today" — displayed when `todaysTasks.length === 0`. This indicates a data issue (program_day misalignment, plan not generated, or all tasks already completed for the day). Shows "Contact support" link.

**Error State:**
- "Could not load today's tasks. Please try again." — displayed when Supabase query fails. Includes "Retry" button calling `refetch()`.

**Acceptance Criteria:**
- AC-1.1: Tasks load and display in correct order (incomplete first, then by duration).
- AC-1.2: `outcomeTitle` shown when available and day < 57.
- AC-1.3: Pillar badge displays correct pillar name and colour.
- AC-1.4: Duration and XP value display correctly formatted.
- AC-1.5: "Why it works" section expandable on tap.
- AC-1.6: Category dots shown days 15-28, category names shown day 29+.
- AC-1.7: Skeleton loading state shown during fetch.
- AC-1.8: Empty state shown when no tasks for today.
- AC-1.9: Error state shown with retry on fetch failure.
- AC-1.10: 3 skeleton cards shown during loading.

---

### 2.2 Task Completion

**Implementation:** `taskEngine.completeTask(userId, taskId)` → called by `useTasks.completeTask()` from screen tap.

**Idempotency:**
- Update query includes `.eq("is_completed", false)` guard. If task is already completed, Supabase returns `PGRST116` (no rows), and the function throws "Task already completed or not found." This prevents double-XP, double-streak, double-drift.

**Pipeline:**
1. Mark `is_completed = true`, set `completed_at` to now — only if currently false.
2. Fetch `current_streak` from `progress` table to determine streak bonus eligibility.
3. Award XP: base `xp_value` (default 10) + 20 streak bonus if `current_streak > 3`.
4. Update streak via `streakService.updateStreak(userId)`.
5. Advance matching challenges via `challengeEngine.onTaskComplete(userId, task)`.
6. Queue and apply pillar score drift (+0.5 on task's pillar):
   - Insert pending effect row into `pending_task_effects`.
   - Call `scoreCalculator.applyTaskEffect(userId, pillar)`.
   - On success: mark effect as applied (`applied_at = NOW()`).
   - On failure: effect stays pending, retried on next app launch via `retryPendingEffects`.
7. Check if all today's tasks are now complete: count remaining incomplete tasks for today's `day_number`. If count = 0, `allDoneToday = true`.
8. Return `{ xpAwarded, streakUpdate, allDoneToday }`.

**UI Feedback:**
- TaskCard animates: opacity fade to 0.5, checkmark icon appears with scale-in animation.
- XP popup: "+{xpAwarded} XP" floats up from task card and fades out (800ms animation).
- Streak indicator updates in real-time (in StatusStrip header).
- If `allDoneToday` is true, `CompletionCard` component slides up from bottom.
- If first task on day 1 AND first strike not completed, `FirstStrikeModal` appears.

**Acceptance Criteria:**
- AC-2.1: Completing a task marks it as done in database (verify `is_completed = true`).
- AC-2.2: Completing an already-completed task throws "Task already completed" error.
- AC-2.3: XP is awarded atomically with task completion.
- AC-2.4: Streak bonus (+20) applied when `current_streak > 3`.
- AC-2.5: Streak updated after completion (verify `last_active_date` = today).
- AC-2.6: Pillar score drift (+0.5) applied to progress table.
- AC-2.7: Failed drift is queued in `pending_task_effects`.
- AC-2.8: `allDoneToday` correctly detects when all tasks are done.
- AC-2.9: Challenge progress advances for matching active challenges.
- AC-2.10: TaskCard shows completion animation on tap.

---

### 2.3 XP Award

**Implementation:** `xpService.awardXP(userId, amount)` called during task completion.

**XP Values:**
| Event | XP |
|-------|-----|
| Task complete (base) | 10 |
| Streak bonus (streak > 3) | 20 |
| Challenge complete | 100 |
| Milestone reached | 250 |
| Cycle check-in | 25 |
| Weekly report (read) | 15 |

**Award Flow:**
1. Validate amount: must be integer, 0 < amount ≤ 500.
2. Fetch current `total_xp` from `progress` table.
3. Compute `newTotal = current + amount`.
4. Calculate new level via `calculateLevel(newTotal)`.
5. Detect level-up: compare `newLevel > oldLevel`.
6. Update `progress` table: `total_xp = newTotal`, `level = newLevel` — with optimistic concurrency guard `.eq("total_xp", current)`.
7. Retry up to 3 times with exponential backoff (100ms, 300ms, 900ms) if guard fails (concurrent update detected).
8. Return `{ newTotal, leveledUp, newLevel?, newLevelName? }`.

**UI Feedback:**
- XP bar (`XPBar` component) animates fill from old to new total.
- If `leveledUp` is true: level-up animation plays (full-screen pulse + new level name displays for 3 seconds then auto-dismisses).
- XP bar shows current level, current XP, and XP-to-next-level.
- XP bar lives in `StatusStrip` header on home screen.

**Acceptance Criteria:**
- AC-3.1: Base 10 XP awarded per task.
- AC-3.2: Streak bonus 20 XP awarded when streak > 3.
- AC-3.3: Invalid XP amounts (≤0 or >500) throw error.
- AC-3.4: Level correctly recalculated after XP award.
- AC-3.5: Level-up detected and returned when threshold crossed.
- AC-3.6: Concurrent update guard prevents race conditions.
- AC-3.7: Retry with backoff (up to 3 attempts) on guard failure.
- AC-3.8: XP bar updates in UI after award.

---

### 2.4 Streak Update

**Implementation:** `streakService.updateStreak(userId)` called during task completion.

**Logic:**
- Fetch `current_streak`, `longest_streak`, `last_active_date` from `progress`.
- Compute today's date string (`YYYY-MM-DD` in local timezone).
- **Already counted today:** if `last_active_date === today` → return current state (no change).
- **Consecutive day:** if `daysBetween(last_active_date, today) === 1` → increment streak.
- **Gap detected or first activity:** → reset streak to 1. `wasReset = true` if previous streak > 0.
- `newLongest = max(newStreak, longest_streak)`.
- Detect milestone: `newStreak` is in `[7, 14, 30, 60, 90]`.
- Persist: update `progress` with `current_streak`, `longest_streak`, `last_active_date`.
- Return `StreakUpdate { newStreak, longestStreak, isMilestone, milestoneValue?, wasReset }`.

**Milestone Detection:**
- Streak values 7, 14, 30, 60, 90 trigger `isMilestone = true`.
- `StreakMilestoneModal` component shown on milestone with:
  - Streak number (large display).
  - Encouraging but non-guilting message: "Day {streak} — a streak worth noting."
  - Continue button dismisses modal.
- Milestone XP (250) awarded inside the modal trigger.

**Milestone Component:**
- Uses `StreakMilestoneModal` — full-screen overlay with teal streak number animation.
- Message uses factual language, no guilt, no "great job".
- Badge unlock check: milestone badge awarded via `unlockBadge` if `streak_{value}` exists in BADGES constant.

**Acceptance Criteria:**
- AC-4.1: Consecutive day correctly increments streak.
- AC-4.2: Gap > 1 day resets streak to 1.
- AC-4.3: Same-day repeat does not change streak.
- AC-4.4: Longest streak updates correctly.
- AC-4.5: `wasReset` flag set when streak resets from > 0.
- AC-4.6: Milestones 7, 14, 30, 60, 90 correctly detected.
- AC-4.7: StreakMilestoneModal appears on milestone with correct day number.
- AC-4.8: Milestone message uses factual, non-guilt language.
- AC-4.9: Milestone badge unlocked on reaching the milestone.

---

### 2.5 All-Done Celebration

**Component:** `CompletionCard` in `src/components/ui/CompletionCard.tsx`

**Trigger:** When `allDoneToday === true` returned from `completeTask()` — i.e. the last incomplete task for today was just completed.

**Behaviour:**
- `CompletionCard` slides up from the bottom of the home screen with spring animation.
- Content:
  - Large checkmark icon (teal `#00C4A7`).
  - "All done for today" heading.
  - Subtitle: "Day {programDay} complete." (non-guilting, factual).
  - Total XP earned today (sum of all today's task XP + streak bonus).
  - Current streak displayed.
  - "View Progress" button → navigates to Progress tab.
  - "Dismiss" tap-anywhere-to-close behaviour.
- If daily insight is cached/available, displayed at bottom: "Coach tip: {insight}".
- Card auto-dismisses after 10 seconds if not interacted with.

**Acceptance Criteria:**
- AC-5.1: CompletionCard appears when all tasks for today are complete.
- AC-5.2: Card slides up with animation.
- AC-5.3: Day number and total XP displayed correctly.
- AC-5.4: "View Progress" button navigates to progress tab.
- AC-5.5: Card dismisses on tap-anywhere.
- AC-5.6: Auto-dismiss after 10 seconds.
- AC-5.7: Daily insight shown if available.

---

### 2.6 First Strike

**Implementation:** `src/services/firstStrike/firstStrikeService.ts`, `src/components/ui/FirstStrikeModal.tsx`

**Trigger:** Day 1, first task completion, AND `users.first_strike_completed === false`.

**Behaviour:**
- `evaluateFirstStrike(userId)` checks if `first_strike_completed` flag is false. If true, returns early (no action).
- `completeFirstStrike(userId)`:
  1. Sets `first_strike_completed = true` on users table.
  2. Reads current `optimisation_score` from progress.
  3. Computes `microScore = min(optimisation_score + 5, 100)`.
  4. Updates `optimisation_score` to new value.
  5. Generates AI insight via `callClaude` with `FIRST_STRIKE_SYSTEM_PROMPT`:
     - System prompt instructs Claude: "Write ONE sentence celebrating this. Keep it grounded and real, not hype. No exclamation marks. Never say 'great job', 'keep it up', 'you're doing amazing', 'consistency is key'. Example tone: 'You already changed something. Before day 1 ends.'"
  6. Returns `{ microScore, insight }`.
- `FirstStrikeModal` displays:
  - **Headline:** "First Strike — Day 1"
  - **Micro-score:** large animated number counting up to `microScore`.
  - **Insight:** AI-generated one-sentence insight.
  - **"Continue"** button dismisses modal.

**States:** Hidden (not day 1 or already completed), active (modal showing), complete (dismissed).

**Acceptance Criteria:**
- AC-6.1: First Strike triggers only on day 1, first task.
- AC-6.2: `first_strike_completed` flag prevents re-trigger.
- AC-6.3: Micro-score computed as min(base + 5, 100).
- AC-6.4: AI insight is one sentence, no exclamation marks, no guilt language.
- AC-6.5: Insight fallback: "You already changed something. Before day 1 ends." if AI fails.
- AC-6.6: Modal dismisses on Continue tap.
- AC-6.7: Progress `optimisation_score` updated after completion.

---

### 2.7 Task Detail

**Screen:** `app/(app)/task/[taskId].tsx`

Dedicated full-screen view for a single task with expanded information. Navigated to by tapping a TaskCard (non-complete action — the complete action is the checkbox).

**Display:**
- **Title:** `outcomeTitle` if available (and day < 57), else `title`. Display font size (32).
- **Pillar:** Pillar name from `PILLAR_DISPLAY` with coloured badge.
- **Tier:** "Beginner" / "Intermediate" / "Advanced" tag.
- **Category:** Category name badge.
- **Duration:** "Takes about {duration_mins} minutes".
- **XP Value:** "+{xp} XP" badge.
- **Why It Works (Full):** Full `whyItWorks` text, no truncation. Formatted with paragraph breaks.
- **Why It Works (Short):** One-line `whyShort` summary above the full text.
- **Completion Button:** `PrimaryButton` "Complete Task" (gold). Shows "Completed" with checkmark if already done.
  - On tap: calls `useTasks.completeTask(taskId)` → handles the full pipeline.
  - On success: shows completion animation, updates button state, navigates back after 1.5s delay.
  - On error: shows error toast with message.

**Related Tasks:**
- Shows 2-3 other tasks for the same day (fetched from `useTodaysTasks`), filtered to exclude current task. Allows quick navigation between today's tasks without going back to home.

**States:** Loading (task fetch), content (task display), error (task not found).

**Acceptance Criteria:**
- AC-7.1: Task detail renders all fields correctly.
- AC-7.2: `outcomeTitle` shown when available (day < 57).
- AC-7.3: Full "why it works" text displayed without truncation.
- AC-7.4: Complete button triggers full completion pipeline.
- AC-7.5: Completed state shown when task is already done.
- AC-7.6: Related tasks shown and tappable for navigation.
- AC-7.7: Back navigation with completion animation delay.

---

### 2.8 Empty / Error States

**Home Screen States:**

**Loading (Skeleton):**
- 3 `TaskCard` skeleton placeholders with pulsing gradient animation.
- Each skeleton: rounded rectangle for title, smaller rectangles for badges and duration.
- Skeleton uses `Colors.surface = #141414` as base, `Colors.elevated = #1C1C1C` as shimmer.
- No text visible during skeleton phase.

**Empty ("No tasks for today"):**
- `ForgeEmptyState` component:
  - Icon: calendar outline.
  - Title: "No tasks for today."
  - Subtitle: "Check back tomorrow for your next set of tasks."
  - Optional: "View Program" button → navigates to Program tab.
- Triggered when `todaysTasks.length === 0` after successful fetch.
- Typically indicates program_day misalignment or all tasks completed.

**Error:**
- `ForgeEmptyState` component:
  - Icon: alert circle.
  - Title: "Could not load today's tasks."
  - Subtitle: error message from service layer.
  - "Try Again" button → calls `refetch()`.
- Triggered when Supabase query fails (network, auth, RLS).

**Acceptance Criteria:**
- AC-8.1: Skeleton loading shows 3 pulsing card placeholders.
- AC-8.2: Empty state shows "No tasks for today" with correct messaging.
- AC-8.3: Error state shows user-readable error with retry button.
- AC-8.4: Retry button successfully refetches tasks.
- AC-8.5: No blank/white state ever rendered on home screen.
