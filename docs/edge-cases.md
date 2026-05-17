# FORGE — Edge Cases & Open Questions

> Living document. Updated as decisions solidify and new edge cases surface.
> Last updated: May 2025

---

## Resolved Decisions

| # | Decision | Context | Rationale | Date |
|---|---|---|---|---|
| 1 | Baseline photo deferred to day 3 | Originally required during onboarding after plan reveal. Caused ~40% drop-off between signup and app entry. | Moved to in-app prompt on day 3 via `/(app)/baseline-photo.tsx`. By day 3 the user has completed tasks, seen the home screen, and is invested enough to take a photo. `/(auth)/baseline-photo.tsx` retained for edge-case recovery. | Mar 2025 |
| 2 | Private photo bucket with signed URLs | Originally public bucket (`user-photos`) for simplicity — anyone with the URL could access photos. Privacy risk. | Switched to private bucket (`user-photos-private`) with time-limited signed URLs. Default TTL: 300s. Added `signedUrl.ts` service with retry logic. | Mar 2025 |
| 3 | Notifications use guilt-free language | Originally included "your streak is at risk" and "don't lose progress" notifications. Felt manipulative and caused notification fatigue. | Replaced with factual cycle prompts: "Cycle photo today. Same angle, same lighting." No "miss you", "come back", "at risk", or "keep going" anywhere. | Mar 2025 |
| 4 | AI proxy via Edge Function | Originally client called Anthropic directly with `EXPO_PUBLIC_ANTHROPIC_KEY` embedded in the app bundle. Key exposure and abuse risk. | Moved to server-side proxy (`claude-proxy` Edge Function). Client sends JWT auth header. Rate limiting: 20 calls/hr/user. Anthropic key lives only in server env (`ANTHROPIC_API_KEY`). | Mar 2025 |
| 5 | Single Basic tier at $11/mo | Originally planned two tiers: Premium ($11/mo) and Max ($29/mo) with feature gating. | Simplified to single `basic` tier to reduce onboarding decision friction. No feature gating — all users get everything. RevenueCat entitlement: `basic`. Package: `basic_monthly`. | Feb 2025 |
| 6 | Streak-risk notifier decommissioned | Edge function `streak-risk-notifier` still deployed, originally triggered at 9pm for users who hadn't completed tasks. | Decommissioned as part of guilt-free notification policy. Function still exists in Supabase but no longer scheduled via `pg_cron`. Cycle prompts only. | Mar 2025 |
| 7 | Task idempotency guard on complete | Early implementation allowed double-tapping a task to trigger double XP and double streak updates. | Added `eq("is_completed", false)` filter on the UPDATE in `taskEngine.completeTask()`. PGRST116 error now returns "Task already completed or not found." | Feb 2025 |
| 8 | Ghost user recovery (auth exists, no profile row) | Broken signups during early development left auth rows with no matching `users` table row. Caused FK violations on plan save, streak, and task operations. | `signIn()` now detects missing profile row and upserts one. `signUp()` validates the profile row exists after insert — if RLS blocked it, returns error. Error states in `_layout.tsx` and signup screen handle the case. | Mar 2025 |
| 9 | Quiz answers cached in memory + AsyncStorage | Network drops or app kills during onboarding could lose quiz state, requiring full restart. | Dual persistence: in-memory cache (`quizCache.ts`) for fast access during onboarding flow, AsyncStorage draft keyed by `quiz_draft_{suffix}` for cold-start recovery. Quiz screens check for draft on mount. | Feb 2025 |
| 10 | Plan cache handoff between plan-loading → plan-reveal | Plan generation is async (~10-30s). If the user navigates away or the app restarts mid-generation, the plan could be lost. | In-memory `planCache.ts` stores the generated plan and baseline analysis. Plan reveal screen reads from cache. `savePlanToDatabase()` called in plan-reveal, not plan-loading. Cache cleared on signOut. | Feb 2025 |
| 11 | Dev bypass mode for RevenueCat | RevenueCat SDK requires EAS dev build — unavailable in Expo Go. Blocked local development and testing. | `isDevBypass()` in `revenuecat.ts` checks `__DEV__ && env !== "production"`. Returns mock active subscription. Allows all development flows without EAS builds. | Feb 2025 |
| 12 | AI simulation mode for dev testing | Real Claude calls cost tokens and require internet — impractical for rapid iteration. | `isAiSimulationEnabled()` in `config/aiSimulation.ts` returns mock plan, mock analysis, mock compliment, mock insights. Controlled per-service for targeted testing. | Feb 2025 |
| 13 | Exo modules (LiquidGlassTabBar, forge-activity, forge-haptics, forge-symbol-effects) | iOS 26+ SwiftUI native components via `@expo/ui/swift-ui` for premium feel. | Modular architecture: `modules/forge-shared` (App Group writer), `modules/forge-activity` (Live Activity bridge for streak), `modules/forge-haptics` (haptic feedback), `modules/forge-symbol-effects` (SF Symbol effects). Each module has fallback for pre-iOS 26. | Apr 2025 |
| 14 | 9-pillar schema migration (003) | Original schema had monolithic `score` columns. No way to track per-pillar progress or apply face shape weight adjustments. | Migration `003_nine_pillar_migration.sql` split into 9 per-pillar columns with `optimisation_score` computed. Weighted composite calculation in `scoreCalculator.ts`. Face shape weight overrides in `faceShapeWeights.ts`. | Feb 2025 |
| 15 | Push notification permission flow | Originally requested notification permissions on app launch (before user had invested). High rejection rate. | Moved to post-purchase: after successful RevenueCat purchase, `requestPermissions()` is called with a soft rationale. Falls back gracefully — notifications silently skip scheduling if denied. | Mar 2025 |
| 16 | Voice pillar unlocked in Season 2 only | Voice is a differentiating pillar but impossible to assess from photos. Premature emphasis in Season 1 would confuse users. | Voice pillar weighted near-zero in Season 1 (`voiceScore = 50` baseline, no drift). On Season rollover, `applySeasonalReweight()` increases voice to 0.11 (11%) proportionally. | Mar 2025 |
| 17 | No face guide overlay on scene photos | Camera needs to capture consistent angles but users have no reference. Early builds had no guidance. | `FaceGuideOverlay.tsx` provides silhouette guide on camera. `LightingIndicator.tsx` shows real-time brightness feedback. Photo analysis system prompt references guide alignment. | Mar 2025 |
| 18 | Program day advancement with last_active_date | Multiple app opens in one day could advance the program day multiple times. | `advanceProgramDay()` checks `last_active_date` from progress table — if already today, returns early with `daysAdvanced: 0`. Optimistic concurrency guard: `eq("program_day", user.program_day)` to prevent double-advance from race conditions. | Mar 2025 |
| 19 | Single season rollover (Season 1 → 2) with S2+ stub | Rollover from S1→S2 is critical — voice unlocks, weights rebalance, new plan generated. S3+ was undefined. | `handleSeasonRollover()` gates on `programDay >= 90 && season === 1`. S2+ rollover stub exists via `startNewSeason()`. Future: generalize rollover to any season transition. | Apr 2025 |
| 20 | Referral code generation at signup | Needed growth mechanics. Manual codes are error-prone and not user-friendly. | Migration `011_referral_codes.sql` adds `referral_code` to users table. Code auto-generated at signup (8-char alphanumeric). `referred_by` column tracks attribution. Shared via native share sheet. | Apr 2025 |

---

## Open Questions

### Content & Plan Generation

| ID | Question | Recommended Answer | Impact |
|---|---|---|---|
| OQ-01 | How do we handle plan variation when a user restarts a season? Currently regenerates from scratch. Should we reuse library tasks that weren't selected in previous seasons? | Increase "novelty" weight in the plan system prompt for S2+ — prefer unused tasks from the user's library selection history. Track `task_library_selections` per season to avoid repeats. | Without this, a user in Season 3 may recognize 70% of tasks from Season 1. Engagement drops when content feels recycled. |
| OQ-02 | Should the Master Task Library be expanded beyond ~150 tasks? | Add ~30-50 advanced tasks locked to Season 2+ (tier: "advanced"). These represent higher-commitment habits that build on S1 foundations. | 150 tasks across 90 days with selection variety means ~60-70 unique tasks per season. Three-season users will see repeats. Advanced tier tasks extend freshness for retained users. |
| OQ-03 | What happens when a user restarts mid-season (e.g., deletes and recreates account)? Should the plan be different? | Re-randomize task selection — flag previous plan's `libraryTaskIds` in the prompt as "previously used, prefer alternatives." | Users who restart for a "fresh slate" should feel like they got a new plan, not the same one. |
| OQ-04 | How do we handle users on dramatically different time commitments (5min vs 1hr daily)? | The plan prompt already injects `daily_time` from quiz. Mitigations: shorter-duration task variants in the library. Consider a `duration_tier` system: tasks that have 5-min and 15-min versions of the same habit. | A 1hr/day user getting 5-minute tasks feels underwhelming. A 5min/day user getting 30-minute tasks will bail. Task duration variance needs library-level support. |

### Scoring & Progress

| ID | Question | Recommended Answer | Impact |
|---|---|---|---|
| OQ-05 | Should optimisation score floor at something above 0? | Keep the mathematical floor as-is (0-100 range). But set the UX display floor at 20 — users should never see a score below 20 even if the raw math produces it. Scores below 20 are demoralizing and drive churn. | A score of 3 feels broken. A score of 22/100 still communicates "room to grow" without feeling punitive. |
| OQ-06 | How should we handle plateaus? User at day 50+ seeing flat pillar scores. | Generate a "plateau coaching insight" when no pillar moves >1 point across 3 consecutive cycles. Insight should acknowledge the plateau, reinforce that this is normal, and suggest one new leverage point. | Stagnant scores kill motivation. Without plateau-aware coaching, users assume the program stopped working and churn. |
| OQ-07 | Should sleep and nutrition scores drift from task completion given we can't visually assess them? | Sleep and nutrition are tagged as `data_gap` in photo analysis. They currently drift +0.5 per task like any pillar. Consider: should they drift slower (0.25) since they're never verified? | Over-weighting invisible pillars inflates scores artificially. A user could have terrible sleep but a 78 sleep score just from completing morning routine tasks. |
| OQ-08 | Should ageing velocity display be optional or always shown? | Gate on minimum cycles: only show ageing velocity after at least 3 check-in cycles (day 9+). Before that, the photo sample is too small for meaningful comparison. | Showing "0 years" on day 3 looks like a bug. Showing "-0.7 years" on day 30 is a powerful moment. |

### AI & Coaching

| ID | Question | Recommended Answer | Impact |
|---|---|---|---|
| OQ-09 | How do we improve weekly report generation reliability? Current reports occasionally have inconsistent structure. | Add structured output enforcement: validate the report string contains all required sections (opening, pillar breakdown, coaching note, next focus) via regex before saving. On validation failure, retry once. If still fails, save a template-based fallback. | A mangled weekly report is worse than no report — it erodes trust in the AI coaching. |
| OQ-10 | Should we add a "coach tone" personalization setting? (direct vs. supportive) | Add if user research supports it. Low priority — the current tone ("grounded, specific, scientific") works well as a default. Premature personalization adds complexity with unclear ROI. | User acquisition cost of personalization is high (quiz question + prompt engineering + testing). Wait for retention data to justify. |
| OQ-11 | How do we handle Claude API outages that last >1 hour? | Build a local fallback insight bank: 30 pre-written, stage-appropriate insights that can be served when Claude is unavailable. Rotate by day to avoid repeats. Show a subtle "cached insight" indicator. | An outage during a user's first weekly report kills trust. Local fallback keeps the experience alive. |

### Gamification

| ID | Question | Recommended Answer | Impact |
|---|---|---|---|
| OQ-12 | Should streaks reset after a single missed day, or should we allow 1 "grace day" per week? | No grace days. The streak mechanic is binary by design — it communicates "you either showed up or you didn't." Softening it dilutes the behaviour change signal. But: when a streak breaks, show a "starting fresh" screen that celebrates the new streak, not the loss. | Grace days turn streaks into "most days" metrics, which don't drive the same behavioural urgency. The key is making the reset feel like a new beginning, not a failure. |
| OQ-13 | Should XP have a daily cap? | Yes — cap at 50 XP/day (5 tasks × 10 XP). No cap on bonus XP (streak bonus, challenge rewards). This prevents XP inflation from a few power users while keeping bonus XP special. | Without a cap, a user who does 15 light tasks daily outpaces everyone. With a cap, milestones remain meaningful baselines. |
| OQ-14 | Are challenge templates (CHALLENGES constant) sufficient, or do we need generated challenges? | The current template set (streak, task count, season) covers core loops. Add dynamic challenges for Season 2+ that are pillar-specific: "Improve skin score by 5 points in 2 weeks." Requires pillar delta tracking and challenge eligibility gating. | Template challenges become predictable by Season 2. Pillar-specific challenges keep the system fresh and aligned with user goals. |

### Subscription & Business

| ID | Question | Recommended Answer | Impact |
|---|---|---|---|
| OQ-15 | Should we offer a lifetime purchase option? | No. Subscription aligns incentives: the app needs to keep delivering value every month. A one-time purchase removes the retention imperative. Revisit when the product has 12+ months of cohort data. | Lifetime purchases front-load revenue but destroy the long-term product quality feedback loop. |
| OQ-16 | How should we handle the transition from 3-day free trial to paid? | Current flow: trial auto-converts to paid after 3 days via App Store. Add: a "trial ending" push notification at 48 hours with a summary of what the user accomplished in 3 days. No guilt — just "here's what you did." | The most churn-prone moment is trial end. A well-timed, factual summary re-grounds the value proposition at the exact moment the purchase decision happens. |
| OQ-17 | Should we add a "pause subscription" feature? (e.g., user going on vacation) | No. Pausing complicates the RevenueCat integration and the coaching engine (what happens to program day advancement?). Instead: make the program forgiving — user opens app after 2 weeks, program day picks up where they left off, no guilt. | "Pause" is a product band-aid for a program that feels punishing. A resilient program design (no streak shaming, day advancement guard) is better. |

---

## Edge Cases

### Onboarding

| ID | Scenario | Defined Handling | Phase |
|---|---|---|---|
| OE-01 | Network drops during plan generation (Claude call) | `planGenerator.ts` throws user-readable error: "Failed to generate your plan. [message]". Plan-loading screen shows error state with retry button. Quiz answers preserved in memory cache — retry rebuilds from cache. | Implemented |
| OE-02 | Quiz crash recovery — app killed mid-quiz | Each quiz step calls `persistQuizDraft()` to AsyncStorage. On mount, quiz screens check `loadQuizDraft()` and restore to last answered question. If no draft found, restart from question 1. | Implemented |
| OE-03 | Signup with existing email | Supabase Auth returns `authError`. Already-translated error passed to signup screen. Signup screen shows the error inline below the email field and offers "Already have an account?" toggle to switch to login screen. | Implemented |
| OE-04 | Plan generation timeout (Claude takes >30s) | No explicit client-side timeout — fetch times out at the network layer (~60s default). UI shows animated loading state with progress messages rotating every 5 seconds. Future: add AbortController with 45s timeout and fallback message. | Implemented |
| OE-05 | Paywall dismissed without purchase | RevenueCat `purchaseBasic()` called from paywall screen. If user dismisses (back button or swipe), they enter `/(app)` without an active subscription. `useSubscription` hook checks `getCustomerInfo()` on app entry. Without subscription, full-screen paywall overlay blocks app interaction. Dev bypass available in `__DEV__` mode. | Implemented |
| OE-06 | Baseline photo missing at day 90 (user never took one) | Cycle check-in screen gates on baseline photo: redirects to `/(app)/baseline-photo` if `baseline_photo_url` is null. At day 90 without baseline, the season rollover still triggers but voice pillar weights remain flat (no face shape adjustment possible). Season report generated without before/after comparison. | Implemented |
| OE-07 | Ghost user — auth row exists, no `users` profile row | Detected in `signIn()`: attempts profile fetch, gets null. Upserts a new profile row with `onboarded=false`. Redirects to appropriate auth screen. Detected in `signUp()`: validates profile row exists after insert. If missing (RLS blocked it), returns hard error — user sees "Account created but profile setup failed. Please try again." | Implemented |
| OE-08 | Returning user mid-onboarding (e.g., closed app after quiz but before plan generation) | `_layout.tsx` checks `user.onboarded` flag. If false, checks which onboarding step to resume: quiz draft exists → resume quiz. No draft but auth exists → restart quiz. Plan cache exists → resume plan-reveal. Redirect chain: splash → correct resume point. | Implemented |

### Daily Tasks

| ID | Scenario | Defined Handling | Phase |
|---|---|---|---|
| TE-01 | All tasks already completed on app open | `getTodaysTasks()` returns all tasks with `is_completed: true`. Home screen renders `CompletionCard` ("All done today") with streak badge, XP summary, and next cycle countdown. No empty state anomaly. | Implemented |
| TE-02 | Task completion double-tap | `completeTask()` includes idempotency guard: UPDATE filters `eq("is_completed", false)`. Second tap returns PGRST116 → throws "Task already completed or not found." UI debounces the toggle with 500ms cooldown after first tap. | Implemented |
| TE-03 | Streak bonus calculation wrong — streak is 3, no bonus, but should be at 4? | Streak bonus triggers at `currentStreak > 3` (i.e., streak of 4+). This is by design: day 1-3 are ramp-up, day 4 starts rewarding consistency. `streakService.ts` computes accurate streak from `last_active_date` before passing to `completeTask()`. | Implemented |
| TE-04 | XP not awarded but task marked done | If `awardXP()` fails after task is marked complete, `completeTask()` throws. Task stays marked complete (`is_completed: true`) but XP row not updated. On next app launch, `retryPendingEffects()` in `progressStore` replays unapplied effects from `pending_task_effects` table. XP is eventually consistent. | Implemented |
| TE-05 | User skips multiple days (e.g., 5 days inactive) | `programAdvancement.ts` advances only 1 day per `advanceProgramDay()` call. User returns with `program_day` advanced by 1, not 5. Rationale: program content is sequential and cumulative. Tasks for missed days become permanently incomplete (they don't force-completion). Streak resets to 1. | Implemented |
| TE-06 | User opens app at 11:59 PM, completes task, date rolls over during interaction | `completeTask()` uses `new Date()` for timestamps. If date rollover occurs between marking complete and checking `allDoneToday`, the day_number is anchored to the task's assigned day — doesn't affect results. Streak update uses local date string comparison for consistency. | Implemented |

### Cycle Check-Ins

| ID | Scenario | Defined Handling | Phase |
|---|---|---|---|
| CE-01 | No baseline photo when 3-day check-in is due | `useBaselineStatus` hook checks `baseline_photo_url` before allowing check-in. If missing, cycle screen redirects to `/(app)/baseline-photo.tsx` with a banner: "Add baseline photo to unlock Forge Scores." Photo is captured, uploaded, analyzed — baseline analysis stored in `cycles` table with `cycle_type: "baseline"`. | Implemented |
| CE-02 | Photo too dark/blurry for Codex Vision analysis | Claude returns `photo_quality_flag: "poor"` in the analysis. `photoAnalyser.ts` clamps analysis and returns it with reduced confidence. `CycleResultCard` shows quality warning and "retry" button. `LightingIndicator.tsx` on camera screen provides real-time feedback before capture to prevent most cases. | Implemented |
| CE-03 | Codex Vision timeout during photo analysis | `photoAnalyser.ts` calls `callClaudeVision()` which routes through `claude-proxy` Edge Function. Timeout handled at fetch layer. Error thrown: "AI Vision error. Please try again." Cycle screen shows error state with retry. Photo already uploaded to bucket — analysis only needs to be retried, not re-uploaded. | Implemented |
| CE-04 | User skips multiple check-in cycles (e.g., cycles 3, 4, 5 missed, now at cycle 6) | `scheduleCyclePrompt()` schedules every 3 days. If missed, the next eligible day is the nearest future multiple of 3 from plan start. User can check in on any day ≥ 3. Cycle numbers auto-assign via `cycle_number_auto_assign` migration (015). Missed cycle slots are simply not created — there's no backfill requirement. | Implemented |
| CE-05 | No internet during photo upload | `imageService.ts` uploads to Supabase storage. Network error surfaces to the cycle screen as "Could not upload photo. Check your connection and try again." Photo preserved in local temp file until upload succeeds. | Implemented |
| CE-06 | Photo already exists for this cycle number | Cycle number assignment uses auto-increment trigger (`015_cycle_number_auto_assign.sql`). INSERT with a duplicate `cycle_number` would fail on the DB unique constraint. Application code never passes explicit cycle numbers — delegates to the trigger. | Implemented |

### Scoring

| ID | Scenario | Defined Handling | Phase |
|---|---|---|---|
| SE-01 | Optimisation score goes above 100 | `applyTaskEffect()` in `scoreCalculator.ts` caps individual pillar scores at `MAX_SCORE = 100` via `Math.min(currentScore + DRIFT_AMOUNT, MAX_SCORE)`. `clampAnalysis()` in `photoAnalyser.ts` clamps `pillar.score` to `[0, 100]` and `forge_score.cycle_high` to max of current vs. previous. Score above 100 is mathematically impossible. | Implemented |
| SE-02 | Negative pillar delta (score went down since last cycle) | `clampAnalysis()` clamps delta to `[-100, 100]`. Negative delta displayed as red text with down indicator on `ScoreCard`. Coaching insight acknowledges regression without alarm: "Hair score dipped this cycle — normal fluctuation. Next focus: consistency." | Implemented |
| SE-03 | Missing pillar in analysis — Claude didn't return a score for one pillar | `isValidCycleAnalysis()` validates all 9 required pillars exist in the JSON response. If any missing, `photoAnalyser.ts` throws "AI analysis was incomplete. Please try again." Retry regenerates the full analysis. | Implemented |
| SE-04 | Face shape not detected in baseline analysis | `clampAnalysis()` preserves whatever face shape Claude returned (or null). Face shape weight adjustments in `deriveInitialWeights()` are skipped if `faceShape` is null or not in `FACE_SHAPE_WEIGHTS` map. Falls through to equal weights. User sees "Face shape: calibrating" on first cycle result. | Implemented |

### Subscription

| ID | Scenario | Defined Handling | Phase |
|---|---|---|---|
| UE-01 | Purchase succeeds (App Store charges) but DB sync fails | `purchaseBasic()` calls `syncSubscriptionToDb()` as fire-and-forget (void). Purchase is still active — RevenueCat is source of truth. `syncSubscriptionToDb()` catches errors silently and logs. On next `getCustomerInfo()` call, RevenueCat returns active entitlement, and app continues normally. DB eventually consistent. | Implemented |
| UE-02 | Subscription expired mid-day, user returns to app | `getCustomerInfo()` called on app foreground via `useSubscription` hook. If entitlement inactive, full-screen paywall overlay blocks interaction. Program day and streak unaffected — subscription is orthogonal to progress. If user re-subscribes, continues from where they left off. | Implemented |
| UE-03 | Restore finds no purchases (user thinks they subscribed but didn't, or used different Apple ID) | `restorePurchases()` returns `active: false`. Paywall screen shows error: "No active subscription found. If you believe this is an error, try again or contact support." Restore button remains available for retry. | Implemented |
| UE-04 | RevenueCat SDK unavailable (Expo Go, network error, or SDK init failure) | `isDevBypass()` returns true in `__DEV__` dev mode → returns mock active subscription. In production, `configure()` throws with user-readable error. `useSubscription` hook catches and shows error state: "Could not verify subscription. Please try again." | Implemented |

### Season Rollover

| ID | Scenario | Defined Handling | Phase |
|---|---|---|---|
| RE-01 | User reaches day 90 but hasn't completed most tasks | Season rollover triggers regardless of completion rate — `handleSeasonRollover()` only gates on `programDay >= 90 && season === 1`. Task completion doesn't affect eligibility. Season report is generated with actual data (low completion → honest assessment). Season 2 plan generated fresh. | Implemented |
| RE-02 | Season rollover cron fails (Supabase `pg_cron` down or function error) | Two-tier recovery: (1) Edge function has retry logic built in. (2) `advanceProgramDay()` has client-side season complete detection — if `seasonComplete === true` is returned, home screen can trigger client-side rollover as fallback. Rollover is idempotent — safe to retry. | Partially implemented (client-side detection exists; full retry via Edge Function is WIP) |
| RE-03 | New plan generation fails during rollover (Claude unavailable) | `handleSeasonRollover()` does not catch the plan generation failure — the error propagates. User sees the error on next app open. The season number has already been updated to 2, but no plan exists. Recovery: `_layout.tsx` detects `season >= 2 && no plan for current season` → triggers `generatePlan()` on app entry with retry. | Implemented (layout.tsx guard exists) |

---

## Future Edge Cases (Phase 2+)

### Social & Sharing (Phase 2)

| ID | Scenario | Target Phase |
|---|---|---|
| SF-01 | Share link opened by non-app user (deep link into app store if app not installed) | Phase 2 |
| SF-02 | User screenshots share card instead of using share button (image quality degradation) | Phase 2 |
| SF-03 | Shared progress reveals identifiable data (privacy for public share links) | Phase 2 |

### Multi-Language (Phase 2)

| ID | Scenario | Target Phase |
|---|---|---|
| ML-01 | AI-generated content (insights, reports) in user's non-English language | Phase 2 |
| ML-02 | Master Task Library translations for ~150 tasks | Phase 2 |
| ML-03 | Quiz questions and onboarding screens in locale | Phase 2 |

### Widget & Watch (Phase 2)

| ID | Scenario | Target Phase |
|---|---|---|
| WW-01 | Widget doesn't update when app is in background (iOS widget refresh constraints) | Phase 2 |
| WW-02 | Apple Watch companion out of sync with phone data | Phase 2 |

### AI Coach Proactivity (Phase 3)

| ID | Scenario | Target Phase |
|---|---|---|
| AI-01 | AI-initiated micro-sprint conflicts with user's current task schedule | Phase 3 |
| AI-02 | Voice-guided routine interrupts while user is in a meeting (time-of-day detection) | Phase 3 |
| AI-03 | Smart mirror integration — user's face partially obscured during analysis | Phase 3 |
