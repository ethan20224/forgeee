# Flow: Season Complete

> Day 90 detection, season report generation, celebration, and season rollover.

Flow: Season Complete. Actor: User → System. Trigger: Day 90 detected via program advancement. End state: Season 2 started with new plan.

---

## Happy Path

```
1. User opens app → program advancement check runs
   └─> advanceProgramDay(userId) detects: program_day was 89, new program_day = 90
       └─> Returns { seasonComplete: true, programDay: 90, season: 1, ... }
           └─> useProgramAdvancement hook sets isSeasonComplete = true
               └─> App layout detects isSeasonComplete → navigates to season-complete screen
                   └─> Season Complete Screen loads
                       ├─ Celebration animation plays (full-screen)
                       │   ├─ Confetti/particle effect (react-native-reanimated)
                       │   ├─ "Season 1 Complete" text animates in
                       │   └─ FORGE Score transition: starting score → final score (animated counter)
                       ├─ Season report generation triggered
                       │   ├─ generateSeasonReport(userId) via Claude AI
                       │   │   ├─ Gathers: all cycle records, completion stats, streak history
                       │   │   ├─ Sends to Codex with narrative story prompt
                       │   │   └─ Returns: story-formatted report (200–350 words)
                       │   └─> Report displayed below celebration
                       │       ├─ Narrative story format
                       │       ├─ "Your Journey" section
                       │       ├─ Before/After comparison
                       │       │   ├─ Score: {baseline_score} → {final_score} (+{delta})
                       │       │   └─ Per-pillar before/after with deltas
                       │       ├─ "Habits That Stuck" — most consistent tasks
                       │       ├─ "Biggest Breakthrough" — pillar with largest improvement
                       │       └─ "What's Next" — focus recommendation for Season 2
                       └─> User reviews report → scrolls to bottom
                           └─> "Start Season 2" button
                               └─> User taps "Start Season 2"
                                   ├─ startNewSeason(userId) called
                                   │   ├─ users.season incremented to 2
                                   │   ├─ program_day reset to 1
                                   │   ├─ plan_start_date set to today
                                   │   └─ Returns { newSeason: 2, planGenerated: false }
                                   ├─ Zustand stores updated (useProgramStore.setSeason(2), setProgramDay(1))
                                   ├─ isSeasonComplete flag cleared
                                   ├─ New plan generation triggered (Codex AI)
                                   │   ├─ Season 1 data feeds into new plan (pillar scores, face shape, preferences)
                                   │   ├─ Voice pillar weight boosted by face shape factor
                                   │   └─ New 90-day plan saved to database
                                   └─> Navigate to home screen (/(app)/(tabs))
                                       └─ Season 2, Day 1 — fresh start
```

---

## Alternate Paths

### Cron-Triggered Rollover (System)
```
pg_cron triggers season-rollover-handler edge function daily at 00:00 UTC
├─ Edge function fetches all onboarded users with plan_start_date
├─ For each user, calculates program_day from start date
├─ If program_day >= 90 AND current season = 1:
│   ├─ Updates users.season = 2
│   ├─ Updates progress.program_day = 1
│   ├─ Inserts season_events row (event_type: "season_rollover")
│   ├─ Resets daily_tasks.is_completed for new season
│   └─ Returns { userId, status: "rolled_over" }
├─ If user on season >= 2: marks as "skipped"
├─ If program_day < 90: marks as "not_ready"
└─> Next time user opens app
    ├─ Program advancement check: program_day = 1, season = 2
    ├─ Season completion screen NOT shown (system already rolled over)
    ├─ Season 1 report available in "Past Seasons" section of profile
    └─ User sees Season 2 home screen directly
```

### View Past Season Reports
```
User on profile screen → taps "Past Seasons"
├─ Lists all completed seasons (1, 2, ...)
├─ Each season shows: FORGE Score range, completion rate, total tasks
├─ Tapping a season opens that season's report
│   ├─ Before/after scores
│   ├─ Per-pillar deltas
│   └─ Full AI-generated narrative (if available)
└─ Reports stored in weekly_reports table (week_number = -1 per season)
```

---

## Error States

| Error | Detection | User Experience |
|-------|-----------|-----------------|
| **Season report generation fails** | `generateSeasonReport()` throws or returns invalid response | Fallback display shown: raw before/after scores with per-pillar deltas, but no AI narrative. User sees: "Your Season 1 scores" with data table. "Start Season 2" button still available. Report generation retried server-side in background. |
| **Rollover DB failure** | `startNewSeason()` update fails (Supabase error) | Error alert: "Could not start your new season. Your Season 1 data is safe." with "Retry" button. User stays on season-complete screen until rollover succeeds. |
| **New plan generation fails** | Codex plan generation fails after season rollover | User is in Season 2 at Day 1 but no plan exists yet. Home screen shows: "We're building your Season 2 plan. Check back shortly." Plan generation retries automatically every 5 minutes (up to 6 retries). On final failure: "We hit a snag generating your plan. Don't worry — we're on it. A notification will let you know when it's ready." Edge function retries plan generation independently. |
| **Season complete detection race condition** | User opens app on 2 devices at day 90 simultaneously | Optimistic-concurrency guard on program_day update: only one device's update succeeds (WHERE program_day = oldValue). Second device gets update count = 0 → re-reads program_day → sees 90 → navigates to season-complete screen (read-only at this point). Only first device triggers rollover. Second device sees "Season already complete" with "View Report" option instead of "Start Season 2". |
