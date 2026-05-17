# Flow: Daily Routine

> Daily task completion, XP, streak, and AI insights — the core engagement loop.

Flow: Daily Routine. Actor: User. Trigger: User opens app on a new day. End state: All tasks complete with XP + streak updated.

---

## Happy Path

```
1. User opens app on a new day
   └─> Home screen loads (3-state handling: loading → content → empty/error)
       ├─ Progress hydrates from Supabase (useProgress, useStreak, useXP hooks)
       ├─ Program day advancement check runs (useProgramAdvancement.checkAdvancement())
       │   ├─ If day already advanced today → skip
       │   └─ If new day → advance program day, update last_active_date, return result
       └─> Home screen renders
           ├─ Hero section: FORGE Score (large animated number), current streak badge, XP bar with level
           ├─ AI insight card (daily coaching tip, ≤25 words, language stage-aware)
           ├─ Task list (2–5 tasks, ordered: incomplete first, shortest duration first)
           │   └─ Each task shows: outcomeTitle (if day < 57), pillar badge, duration, XP value
           └─ Heatmap row (last 7 days — done/partial/missed)
               └─> User taps a task
                   └─> Task detail screen
                       ├─ Task title (outcomeTitle preferred, clinical title if day >= 57)
                       ├─ Pillar badge + tier indicator
                       ├─ Duration and XP value
                       ├─ "Why it works" explanation
                       └─ "Mark Complete" button
                           └─> User taps "Mark Complete"
                               ├─ Double-tap guard: if already completed → show "Task already done" (no-op)
                               ├─ Task marked completed in daily_tasks table
                               ├─ XP awarded (10 base + 20 streak bonus if streak > 3)
                               ├─ Streak updated (increment or reset based on last_active_date)
                               ├─ applyTaskEffect() queues +0.5 pillar drift
                               ├─ Haptic feedback (success tap)
                               ├─ Animated checkmark on task card
                               ├─ Task moves to bottom of list (completed section, dimmed)
                               └─> If first task ever completed by user
                                   └─> First Strike modal appears
                                       ├─ Celebration animation
                                       ├─ Micro-score display
                                       ├─ AI-generated compliment
                                       └─ "Let's Go" button → dismiss
                                           └─> Return to task list
                                               └─> User completes remaining tasks
                                                   └─> All tasks complete
                                                       └─> Celebration card shows
                                                           ├─ "All Done" with animated checkmark
                                                           ├─ XP summary (total earned today)
                                                           ├─ Streak count updated
                                                           ├─ FORGE Score updated with any pillar drift
                                                           └─ "See your progress" link → progress tab
```

---

## Alternate Paths

### Partial Completion
```
User completes some tasks, closes app, returns later same day
├─ Home loads → shows remaining incomplete tasks at top
├─ Completed tasks shown dimmed at bottom
├─ Streak and XP already updated for previously completed tasks
└─ User completes remaining tasks → celebration card shown when all done
```

### Already All Done Today
```
User opens app, all tasks already completed for today
├─ Home shows CompletionCard at top: "All done for today"
├─ Task list shows all tasks dimmed with checkmarks
├─ FORGE Score, streak, XP displayed as current
└─ User can still browse progress, cycle check-in, coaching
```

### Skipped Days (Recovery)
```
User misses 1+ days, opens app on a later day
├─ programAdvancement detects gap: daysBetween(lastActive, today) > 1 → wasInactive = true
├─ Program day advances by 1 (not the full gap) — user continues from last position
├─ No penalty to day count, no "make-up" tasks assigned
├─ Streak resets to 0 if gap > 1 day (server-side via last_active_date check)
├─ Home shows current day's tasks (not accumulated backlog)
└─ AI insight may acknowledge the gap with neutral language:
    "Day {N}. Resuming where you left off." (no guilt/shaming)
```

---

## Error States

| Error | Detection | User Experience |
|-------|-----------|-----------------|
| **Task already completed (double-tap guard)** | Task row `is_completed = true` at time of tap | Toast: "Already done" — no XP re-awarded, no duplicate DB write. Button shows completed state immediately. |
| **XP not awarded but task marked done** | `awardXP()` fails after task completion update succeeds | Task shows as completed (checkmark visible). On next app open or task interaction, `pending_task_effects` table entries are processed by retry logic. XP appears after retry succeeds. Idempotent: retry checks if XP already awarded for that task. |
| **Network down during task fetch** | `useTasks` fetch fails (Supabase unreachable) | Home screen shows error state: "Could not load your tasks. Check your connection." with "Retry" button. Previously cached task data from store is preserved and displayed if available. |
| **Streak miscalculation** | `streakService` returns unexpected value (e.g., streak > last_active_date gap) | Streak recalculated from `daily_tasks` completion history on each home screen load. Server-side consistency: streak = count of consecutive days with at least one completed task, working backward from today. |
| **Progress hydration timeout** | `useProgress` fetch exceeds 5s | Loading skeleton persists. After 5s: "Loading your progress..." with subtle spinner. After 10s: "Taking longer than expected. Pull to refresh." No hard error — continues trying in background. |
