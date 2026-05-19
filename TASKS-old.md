# FORGE — Development Tasks

> Status key: ✅ Done · 🔄 In progress · ⬜ Todo · 🚫 Deferred
> Last updated: May 2025

---

## Foundation

Infrastructure and scaffold — the bones everything sits on.

| Status | Task |
|---|---|
| ✅ | Expo project init with TypeScript (SDK ~55, RN 0.83) |
| ✅ | Supabase project setup (PostgreSQL, Auth, Storage, Edge Functions) |
| ✅ | expo-router file-based routing with `(auth)` and `(app)` groups |
| ✅ | Zustand store setup: `useUserStore`, `useProgramStore`, `useProgressStore` |
| ✅ | Path aliases `@/` configured in tsconfig |
| ✅ | ESLint + TypeScript strict mode |
| ✅ | Jest + ts-jest test setup (14 test files) |
| ✅ | Design token system: `Colors`, `Spacing`, `Typography`, `Radius`, `Animation` in `src/constants/design.ts` |
| ✅ | SwiftUI design tokens bridge: `src/constants/swiftui.ts` (SwiftUIColors, SwiftUIPadding, SwiftUIFontSize, SwiftUIWeight, SwiftUIRadius) |
| ✅ | EAS Build configuration (dev, preview, production profiles) |
| ✅ | RevenueCat SDK setup (`react-native-purchases`, `app.config.ts` plugin) |
| ✅ | PostHog analytics setup (7 core events instrumented) |
| ✅ | `app.config.ts` with iOS bundle identifier `com.forge.app`, camera/photo permissions |
| ✅ | Environment variables: `EXPO_PUBLIC_SUPABASE_URL`, `EXPO_PUBLIC_SUPABASE_ANON_KEY`, `EXPO_PUBLIC_ANTHROPIC_KEY`, `EXPO_PUBLIC_REVENUECAT_APPLE_KEY`, `EXPO_PUBLIC_APP_ENV` |

---

## Sprint 1 — Auth & Onboarding Structure

**Goal:** User can create account and navigate through onboarding skeleton.  
**Status:** ✅ Done

| Status | Task |
|---|---|
| ✅ | Splash screen with animated loading bar and FORGE wordmark |
| ✅ | Welcome carousel (3 slides: transformation promise, 90-day structure, AI coaching) |
| ✅ | Quiz with 7 questions (goals, routine level, daily time, timeline, main concern, age range, has photo) |
| ✅ | Quiz step-based routing with progress indicator |
| ✅ | Quiz answer caching: memory (`quizCache.ts`) + AsyncStorage draft persistence |
| ✅ | Signup screen (name, email, password with validation) |
| ✅ | Login screen (email, password, toggle from signup) |
| ✅ | Supabase auth integration: `signUp()`, `signIn()`, `signOut()`, `getCurrentUser()` |
| ✅ | Auth state listener in root `_layout.tsx` — redirects based on `onboarded` flag |
| ✅ | Onboarding routing guards: splash → welcome → quiz → signup → plan-loading → plan-reveal → paywall → `/(app)` |
| ✅ | Ghost user recovery: SignIn detects missing profile row + upserts; SignUp validates profile row after insert |
| ✅ | Progress row created at signup (all pillar scores = 50, streak = 0, total_xp = 0, level = 1) |
| ✅ | Device timezone captured at signup (`Intl.DateTimeFormat().resolvedOptions().timeZone`) stored in `users.timezone` |
| ✅ | `signOut()` cleans up: 3 Zustand stores reset, plan cache cleared, baseline cache cleared, notifications cancelled, Live Activity ended |
| ✅ | `deleteAccount()`: Deletes all user data from 12 tables, signs out locally |

---

## Sprint 2 — Plan Generation

**Goal:** Codex generates a personalised 90-day plan from quiz answers.  
**Status:** ✅ Done

| Status | Task |
|---|---|
| ✅ | Plan generation service (`planGenerator.ts`) — calls Claude with task library + quiz answers |
| ✅ | Master Task Library populated (~150 tasks across 9 pillars, 3 tiers: beginner/intermediate/advanced) |
| ✅ | Plan system prompt engineering (`planPrompt.ts`) — phased introduction schedule, 90-day structure |
| ✅ | Task library prompt injection — compact JSON of `{id, title, pillar, tier, whyItWorks}` sent as context |
| ✅ | Plan loading screen with animated progress messages, gradient background |
| ✅ | Plan reveal screen with program name, focus summary, honest expectation, score estimation |
| ✅ | Plan persistence to Supabase: `plans` table (program_name, focus_summary, raw_json) + `daily_tasks` table (all 90 days flattened) |
| ✅ | Task library selection tracking via `task_library_selections` table (unique library_task_ids per plan) |
| ✅ | AI simulation mode for dev (`config/aiSimulation.ts`) — mock plan, mock compliment, mock analysis |
| ✅ | Plan validation: structural (`validatePlan`) + semantic (`validatePlanStrict`) — weeks count, day count, pillar keys, weight sum = 1.0 |
| ✅ | Markov fence stripping: handles Claude accidentally returning JSON inside \`\`\` fences |
| ✅ | XP values attached to tasks (10 XP per task, injected during plan generation) |
| ✅ | Plan IDs tracked per season — fetched via `plans` table `season` column for rollover detection |
| ✅ | Plan cache handoff: `planCache.ts` stores generated plan + baseline analysis; plan-reveal reads from cache; cleared on signOut |
| ✅ | Onboarding compliment generation (`generateOnboardingCompliment()`) — 15-25 word specific strength callout |
| ✅ | Quiz score estimation (`quizScoreEstimator.ts`) — pre-baseline score prediction shown on plan-reveal |

---

## Sprint 3 — Daily Tasks & Home Screen

**Goal:** User can view and complete daily tasks on the home screen.  
**Status:** ✅ Done

| Status | Task |
|---|---|
| ✅ | Task engine (`taskEngine.ts`): `getTodaysTasks()`, `completeTask()`, `savePlanToDatabase()` |
| ✅ | `getTodaysTasks()` query with ordering: incomplete first, then duration_mins ASC (easiest first) |
| ✅ | `completeTask()` with idempotency guard: `eq("is_completed", false)` filter prevents double completion |
| ✅ | XP service (`xpService.ts`): `awardXP()`, calculate level from XP thresholds (6 levels) |
| ✅ | Streak service (`streakService.ts`): `updateStreak()`, milestone detection (7, 14, 30, 60, 90) |
| ✅ | Streak reset detection: gap > 1 day or null `last_active_date` → reset to 1 |
| ✅ | Streak bonus: +5 XP when `current_streak > 3` |
| ✅ | Home screen with task list, status strip, AI insight card |
| ✅ | TaskCard component with toggle, title, `outcomeTitle` (when present), `whyItWorks` expand, pillar badge, duration |
| ✅ | `outcomeTitle` preferred over clinical title for display (until day ≥ 57) |
| ✅ | XPBar component: progress bar with current XP, next level threshold, current level badge |
| ✅ | StreakBadge component: flame icon, current streak count, milestone indicator |
| ✅ | StatusStrip component: XP + Streak + Optimization Score compact strip at top |
| ✅ | AI insight card: 1-line daily coaching insight (≤25 words), stage-aware language |
| ✅ | Pillar badge on tasks: colored pill with pillar abbreviation |
| ✅ | Task ordering: incomplete first, by duration (shortest → longest) |
| ✅ | Pull-to-refresh on home screen tasks |
| ✅ | `CompletionCard`: shown when all tasks complete — streak, XP earned today, next cycle countdown |
| ✅ | `CategoryBadge`: task category indicator (routine, exercise, nutrition, grooming, etc.) |

---

## Sprint 4 — Scoring & Progress

**Goal:** 9-pillar scoring system with weighted composite Optimisation Score.  
**Status:** ✅ Done

| Status | Task |
|---|---|
| ✅ | 9-pillar schema migration (`003_nine_pillar_migration.sql`): per-pillar score columns + `optimisation_score` |
| ✅ | Score calculator (`scoreCalculator.ts`): `calculateOptimisationScore()` weighted composite, `deriveInitialWeights()` from quiz |
| ✅ | Face shape weight adjustments: 6 face shapes with per-pillar deltas (`faceShapeWeights.ts`) |
| ✅ | `applyTaskEffect()`: +0.5 drift per task completion, capped at 100, re-normalizes optimisation_score |
| ✅ | `retryPendingEffects()`: replays unapplied effects from `pending_task_effects` table on cold start |
| ✅ | `applySeasonalReweight()`: voice pillar unlocked in Season 2+ (increases from ~0.03 to 0.11) |
| ✅ | `diffPillars()`: delta calculation between two score sets (current − previous) |
| ✅ | `getHeatmapData()`: 90-element boolean array for heatmap grid (completed any task that day) |
| ✅ | Progress screen layout: hero ForgeScoreCard, pillar score grid, heatmap, sparklines |
| ✅ | ForgeScoreCard component: hero display with current score, delta indicator |
| ✅ | ScoreCard component: per-pillar card with score, delta, confidence, color |
| ✅ | HeatmapGrid component: 91-day grid (day 0–90), colored by completion |
| ✅ | SparklineChart component: per-pillar trend line across cycles |
| ✅ | Progress store hydration: fetches progress row, calculates deltas |
| ✅ | Pillar detail screen: single-pillar deep dive with score history, related tasks, focus tips |
| ✅ | PILLAR_DISPLAY and `pillarDisplayName()` — UI reads from constants, not raw strings |
| ✅ | `VISIBLE_PILLARS` constant — only 6 of 9 pillars surfaced by default (excludes sleep, nutrition, voice) |
| ✅ | `segmentBar` component: visual representation of pillar weight distribution |

---

## Sprint 5 — Paywall & Subscription

**Goal:** User purchases $11/mo subscription via RevenueCat.  
**Status:** ✅ Done

| Status | Task |
|---|---|
| ✅ | Paywall screen design: dark surface, feature list, CTA button, restore link, legal links |
| ✅ | RevenueCat purchase flow: `configure()`, `purchaseBasic()`, `restorePurchases()`, `getCustomerInfo()` |
| ✅ | RevenueCat webhook Edge Function: handles `INITIAL_PURCHASE`, `RENEWAL`, `EXPIRATION`, `CANCELLATION` events |
| ✅ | Subscription status sync to DB: `subscription_tier`, `subscription_provider`, `subscription_expires_at` on `users` table |
| ✅ | Dev bypass mode: `isDevBypass()` returns mock active subscription in `__DEV__` mode |
| ✅ | Post-purchase notification permission request (soft rationale, graceful fallback if denied) |
| ✅ | Subscription gating on app entry: `useSubscription` hook, full-screen paywall overlay if inactive |
| ✅ | 3-day free trial (configured in RevenueCat dashboard, referenced in paywall copy) |
| ✅ | Subscription expired mid-session handling: `getCustomerInfo()` on app foreground |
| ✅ | Restore purchases with "no subscription found" error state |
| ✅ | `useSubscription` hook: returns `isActive`, `expiresAt`, `purchase()`, `restore()` |

---

## Sprint 6 — Photo Capture & Analysis

**Goal:** User takes photos and gets Codex Vision analysis.  
**Status:** ✅ Done

| Status | Task |
|---|---|
| ✅ | Camera integration (`expo-camera`) — front-facing camera with capture button |
| ✅ | Gallery picker (`expo-image-picker`) — select from photo library |
| ✅ | Image crop & compress (`expo-image-manipulator`) — resize to max 1024px, JPEG 80% quality |
| ✅ | Private photo bucket setup: `user-photos-private` with RLS policies (user reads own, service_role inserts) |
| ✅ | Signed URL generation (`signedUrl.ts`): `getSignedPhotoUrl()` with 300s default TTL, retry on failure |
| ✅ | Batch signed URL generation: `getSignedPhotoUrls()` for multiple paths |
| ✅ | Photo upload service (`imageService.ts`): upload to private bucket, return path + signed URL |
| ✅ | Codex Vision integration (`callClaudeVision()`): URL-based images via server-side proxy |
| ✅ | Photo analysis system prompt (`photoPrompt.ts`): structured 9-pillar analysis, face shape, quality flag |
| ✅ | Cycle record persistence: `cycles` table with photo_url, photo_path, all 9 pillar scores, AI insight, face_shape |
| ✅ | Photo timeline screen: chronological list of check-in photos with scores |
| ✅ | Before/after comparison screen: side-by-side cycle photos with score deltas |
| ✅ | Face guide overlay on camera (`FaceGuideOverlay.tsx`): silhouette guide for consistent framing |
| ✅ | Lighting indicator on camera (`LightingIndicator.tsx`): real-time brightness feedback |
| ✅ | AI simulation mode for vision: returns `MOCK_CYCLE_ANALYSIS` with cycle_number injected |
| ✅ | Scan mode support: "face" (close-up) and "full" (full body) — applies data gap filters for non-visual pillars |
| ✅ | Photo analysis validation: `isValidCycleAnalysis()` checks all 9 pillars, forge_score, cycle_number, date |
| ✅ | Photo analysis clamping: `clampAnalysis()` caps scores 0–100, deltas -100 to 100, monotonic cycle_high |

---

## Sprint 7 — Cycle Check-Ins

**Goal:** User checks in every 3 days with photos.  
**Status:** ✅ Done

| Status | Task |
|---|---|
| ✅ | Cycle check-in eligibility: every 3 days from plan start date |
| ✅ | `useCycles` hook: `canCheckInNow`, `daysUntilNextCycle`, `history[]`, `latest` |
| ✅ | Cycle screen: camera capture + gallery picker, scan mode toggle, submit button |
| ✅ | `useCycleCheckIn` hook: orchestrates capture → upload → analyse → persist → display |
| ✅ | Cycle analysis validation: all 9 pillars present, forge_score numeric |
| ✅ | Cycle result card component: scores, insight, next focus, quality flag, share button |
| ✅ | Cycle history query: `getCycleHistory()` ordered by cycle_number DESC |
| ✅ | Cycle comparison modal: side-by-side of any two cycles with score deltas |
| ✅ | Cycle notification scheduling: every 3 days at 10am, 12 cycles ahead, guilt-free copy |
| ✅ | Cycle number auto-assignment trigger: `015_cycle_number_auto_assign.sql` — DB trigger assigns next cycle number per user |
| ✅ | Baseline photo deferred to day 3: `useBaselineStatus` hook checks `baseline_photo_url`; redirects to `/(app)/baseline-photo` if missing |
| ✅ | `/(auth)/baseline-photo.tsx` retained for edge-case recovery during onboarding |
| ✅ | Baseline analysis stores `cycle_type: "baseline"` — used for before/after comparisons |
| ✅ | Photo upload with loading state, error state, retry |
| ✅ | `useBaselineUpload` hook: baseline-specific capture/upload/analyze flow |
| ✅ | `usePhotoCapture` hook: reusable camera/gallery capture logic |

---

## Sprint 8 — Coaching Engine

**Goal:** AI generates daily insights and weekly reports with stage-aware language.  
**Status:** ✅ Done

| Status | Task |
|---|---|
| ✅ | Daily insight generation: 1 sentence (≤25 words), stage-aware, cached 1 hour TTL |
| ✅ | Language stage system (`languageStage.ts`): outcome (days 1–14) → habit (15–30) → mechanism (31–90) |
| ✅ | `stageForDay()` resolves stage from program day |
| ✅ | `showCategoryDots()`: day ≥ 15 && ≤ 28 |
| ✅ | `showCategoryNames()`: day ≥ 29 |
| ✅ | `showWhyByDefault()`: day ≥ 29 |
| ✅ | Weekly report generation: 180–250 words with opening, pillar breakdown, coaching note, next week focus |
| ✅ | Season report generation: narrative format, before/after scores, biggest mover, habits stuck, what changed/didn't |
| ✅ | Onboarding compliment generation: 15–25 word strength callout from baseline analysis |
| ✅ | Weekly report Edge Function: scheduled via `pg_cron` Sunday 06:00 UTC, generates + saves to `weekly_reports` table |
| ✅ | Coaching prompt system (`coachingPrompt.ts`): `buildCoachingSystemPrompt(stage)` returns stage-appropriate system prompt |
| ✅ | Insight caching: in-memory Map, 1-hour TTL, keyed by `date:stage:mode` |
| ✅ | Weekly report screen: markdown-rendered report with pillar movement table, coaching note, next focus |
| ✅ | Coaching notifications: "Weekly report ready." Sunday 9am push |
| ✅ | Coaching tone: grounded, specific, scientific; no cheerleading ("great job", "keep it up") |
| ✅ | `useInsights` hook: fetches + caches daily insight |
| ✅ | `useWeeklyReport` hook: fetches latest weekly report |

---

## Sprint 9 — Notifications

**Goal:** User receives timely, guilt-free push notifications.  
**Status:** ✅ Done

| Status | Task |
|---|---|
| ✅ | expo-notifications setup: handler configured (show alert, sound, badge, banner, list) |
| ✅ | Permission request flow: soft rationale after purchase, graceful fallback if denied |
| ✅ | Cycle prompt scheduling: every 3 days at 10am, 4 cycles ahead (12 days), guilt-free copy |
| ✅ | Weekly report notification: Monday 9am, repeats weekly |
| ✅ | Day-1 push: 7am on signup day — "Welcome to Day 1. Your transformation starts now." |
| ✅ | Streak risk notifier decommissioned: Edge function still deployed but unscheduled |
| ✅ | Guilt-free language enforced: no "at risk", "miss you", "come back", "keep going", "don't lose progress" |
| ✅ | Notification cancellation on sign out: `cancelAll()` clears all scheduled notifications |
| ✅ | Device timezone capture at signup: `getDeviceTimezone()` → `users.timezone` |
| ✅ | Cycle prompts cease at day 90: no prompts scheduled beyond program day 90 |
| ✅ | Notification channel (Android): default channel with sound |
| ✅ | `useNotifications` hook: permission status, schedule/cancel helpers |

---

## Sprint 10 — Gamification

**Goal:** XP, levels, streaks, challenges, and badges drive engagement.  
**Status:** ✅ Done

| Status | Task |
|---|---|
| ✅ | XP award on task completion: 10 XP per task, +5 streak bonus when streak > 3 |
| ✅ | Level calculation: 6 levels with XP thresholds (50, 150, 350, 700, 1200, 2000) |
| ✅ | Level display: level number + level name from `LEVELS` constant |
| ✅ | Streak tracking: `updateStreak()` increments consecutive days, resets on gap |
| ✅ | Streak milestones: 7, 14, 30, 60, 90 days with milestone modal celebration |
| ✅ | Badge catalog defined: `BADGES` constant with id, name, description, icon |
| ✅ | Challenge templates: `CHALLENGES` constant (streak, task_count, season types) |
| ✅ | Challenge engine (`challengeEngine.ts`): `startChallenge()`, `onTaskComplete()`, `onCycleCheckIn()`, `getActiveChallenges()`, `checkChallengeComplete()` |
| ✅ | Achievement unlocking: `unlockBadge()` inserts into `achievements` table, idempotent |
| ✅ | Challenge completion: marks `completed`, awards XP, unlocks badge |
| ✅ | First Strike celebration: Day 1 3-task completion triggers `completeFirstStrike()`, +5 micro-score, AI insight |
| ✅ | `FirstStrikeModal`: celebrating first-day completion with insight quote |
| ✅ | Streak milestone modal (`StreakMilestoneModal`): milestone value, encouragement quote |
| ✅ | `CompletionCard`: shown when all tasks done, with XP earned, streak, next cycle |
| ✅ | Season 2 teaser card: shown at day 66+ — "Season 2 coming. Voice training unlocks." |
| ✅ | `useChallenges` hook: active challenges + progress |
| ✅ | `useAchievements` hook: unlocked badges |
| ✅ | `useStreak` hook: current streak, longest streak, milestone, at risk (informational only, no guilt notification) |
| ✅ | `useXP` hook: total XP, level, level name, xp to next level, leveled up |
| ✅ | `useFirstStrike` hook: evaluation + completion flow |

---

## Sprint 11 — Season Lifecycle

**Goal:** Program day advancement, season rollover, season complete.  
**Status:** ✅ Done

| Status | Task |
|---|---|
| ✅ | Program day advancement logic (`programAdvancement.ts`): `getProgramDay()`, `advanceProgramDay()` |
| ✅ | `advanceProgramDay()`: checks `last_active_date`, skips if already today, advances by 1, concurrency guard |
| ✅ | Season rollover: `handleSeasonRollover()` gates on `programDay >= 90 && season === 1` |
| ✅ | Season rollover applies: update season → 2, reset program_day → 1, reweight pillars, generate S2 plan |
| ✅ | Season rollover cron job: `pg_cron` daily 00:00 UTC triggers Edge Function for eligible users |
| ✅ | `applySeasonalReweight()`: voice pillar unlocked (0.11 weight), other 8 pillars re-scaled proportionally |
| ✅ | Season complete screen: end-of-season report with before/after, biggest mover, habits stuck, Season 2 preview |
| ✅ | Season event audit log: `season_events` table tracks plan_generated, season_complete, rollover_started, etc. |
| ✅ | Season 2 plan regeneration: uses S1 quiz answers + face shape + S2 reweighted pillars |
| ✅ | Voice unlock in Season 2: voice pillar weight increased from ~3% to 11% |
| ✅ | Aging velocity metric: Codex Vision compares baseline vs. latest photo, estimates years younger/older (-3 to +3) |
| ✅ | Season transition modal: shown at day 66 — teaser for Season 2 |
| ✅ | Phase progress bar (`PhaseProgressBar`): visual 3-phase indicator with current phase highlighted |
| ✅ | Milestone timeline component (`MilestoneTimeline`): day markers at 7, 14, 30, 60, 90 |
| ✅ | Phase names from `PHASE_DISPLAY` constant — no hardcoded phase strings in JSX |
| ✅ | `useProgramAdvancement` hook: triggers day advance on app foreground |
| ✅ | `useSeasonComplete` hook: checks season completion + triggers rollover |
| ✅ | `useAgingVelocity` hook: calculates and caches aging velocity |

---

## Sprint 12 — Share & Profile

**Goal:** User can share progress and manage account.  
**Status:** ✅ Done

| Status | Task |
|---|---|
| ✅ | Share card generation: `ShareScoreCard` component with Forge Score, streak, cycle count |
| ✅ | Share score card screen: renders share card, captures via `react-native-view-shot` |
| ✅ | Share service (`shareService.ts`): native share sheet with image + text |
| ✅ | Challenge share card: share challenge completion badge |
| ✅ | Profile screen: name, email, subscription status, program day, XP/level, account actions |
| ✅ | Account deletion: deletes all user data from 12 tables in dependency order |
| ✅ | Sign out flow: cancel notifications, end Live Activity, clear 3 stores, clear caches, sign out Supabase |
| ✅ | Referral code generation + sharing: 8-char alphanumeric code auto-generated, shared via native share sheet |
| ✅ | PostHog analytics instrumented: 7 core events (signup_completed, plan_generated, first_task_completed, first_cycle_checkin, subscription_started, score_shared, season_completed) |
| ✅ | iOS NativeTabs with SF Symbols: `LiquidGlassTabBar` on iOS 26+, RN tab fallback on older |
| ✅ | `useShareCard` hook: generates share card image, opens native share sheet |
| ✅ | `useAccount` hook: account deletion, sign out |
| ✅ | `useAnalytics` hook: wraps PostHog identify + track |

---

## Sprint 13 — Polish & Hardening

**Goal:** Bug fixes, edge cases, security hardening, enforcement tests.  
**Status:** ✅ Done

| Status | Task |
|---|---|
| ✅ | Input validation CHECK constraints on `users` table (email format, name length) |
| ✅ | RLS policy hardening: service_role bypass, user-isolation on all tables |
| ✅ | Security hardening migration (`008_security_hardening.sql`): row-level security audit |
| ✅ | Rate limit tracking: `claude_api_calls` table logs all proxy requests, rate limit 20/hr/user |
| ✅ | Pending task effects queue: `pending_task_effects` table captures drift that failed to apply, retried on cold start |
| ✅ | Photo bucket privatisation: `010_private_photo_bucket.sql` migration, RLS policies, signed URL generation |
| ✅ | Session recovery fallback: `signIn()` upserts profile row for ghost users |
| ✅ | Progress store retry on cold start: `retryPendingEffects()` replays unapplied drift |
| ✅ | Plan cache handoff hardening: memory cache cleared on signOut, plan-reveal reads from cache only |
| ✅ | Program day advancement hardening: optimistic concurrency guard (`eq("program_day", user.program_day)`), `last_active_date` dedup |
| ✅ | Enforcement tests (no hardcoded phases, outcome language, guilt-free notifications) |
| ✅ | AGENTS.md + CLAUDE.md documentation: full project context, non-negotiable rules, architecture |
| ✅ | Architecture.md: tech stack, running locally, project structure, data flow, deployment |
| ✅ | ErrorBoundary component: catches render errors, shows recovery UI |
| ✅ | ForgeEmptyState component: standardized empty state with illustration and CTA |

---

## Phase 2 — 🚫 Deferred

**Goal:** Social features, creator partnerships, advanced coaching, growth mechanics.

| Status | Task |
|---|---|
| 🚫 | Social feed for progress sharing (upvotes, comments, anonymous mode) |
| 🚫 | Creator/influencer dashboard (analytics, audience insights, plan templates) |
| 🚫 | Plan regeneration UI (user requests a new plan mid-season) |
| 🚫 | Advanced analytics dashboard (cohort retention, pillar progression, churn prediction) |
| 🚫 | Cohort/challenge groups (join a group of users on same program day, shared challenge) |
| 🚫 | Plan template CMS (admin interface for managing task library and plan templates) |
| 🚫 | A/B testing framework for plan variants (different task selections, different coaching tones) |
| 🚫 | Multi-language support (i18n for UI strings, bilingual Claude prompts for non-English insights) |
| 🚫 | Push notification customization (user picks notification types and times) |
| 🚫 | Widget (iOS home screen): ForgeScoreWidget, TodaysTasksWidget |
| 🚫 | Apple Watch companion: StreakActivityView via Live Activity bridge |
| 🚫 | Creator-specific plan variants (co-branded plans with creator's identity) |
| 🚫 | Batch plan generation improvements (pre-generate plans for new users during low-traffic hours) |
| 🚫 | Image quality auto-enhancement (auto-brightness, sharpening before Claude analysis) |
| 🚫 | Improved share card animations (react-native-reanimated entrance/exit animations) |
| 🚫 | Deep link support for share cards (app store redirect for non-installed users) |
| 🚫 | Referral attribution tracking (PostHog event on referral signup) |
| 🚫 | In-app feedback collection (NPS survey at day 30 and day 90) |
| 🚫 | Crash recovery UX (auto-restore to last screen after crash) |

---

## Phase 3 — 🚫 Deferred

**Goal:** Proactive AI coach, hardware integrations, enterprise/teams.

| Status | Task |
|---|---|
| 🚫 | AI-initiated micro-sprints (Claude suggests 3-day focus sprints based on pillar drift) |
| 🚫 | Voice-guided morning routines (audio coaching for grooming/skincare routines) |
| 🚫 | Smart mirror integration (camera-equipped mirror captures daily progress photos automatically) |
| 🚫 | Wearable sleep/fitness data import (Apple Health, Oura, Whoop → sleep + nutrition pillar verification) |
| 🚫 | Predictive score modeling (Claude forecasts 14-day score trajectory based on completion patterns) |
| 🚫 | Enterprise/team plans (corporate wellness, team challenges, admin dashboard) |
| 🚫 | Habit stacking engine (AI chains new habits onto established ones based on completion data) |
| 🚫 | Real-time pillar drift alerts (push notification when a pillar drops >2 points in one cycle) |
| 🚫 | Custom plan builder (user-editable task selection, reordering, day assignment) |
| 🚫 | Program export (PDF/print — end-of-season report as downloadable PDF) |
| 🚫 | Cross-platform sync (iPad companion app, web dashboard) |
| 🚫 | Automated video check-ins (30-second video analysis instead of photos) |
| 🚫 | Partner/accountability buddy system (connect with another user, see each other's streak) |
| 🚫 | Body composition tracking (photo-based body fat % estimation via Claude Vision) |

---

## Infrastructure / DevEx

Developer tooling, CI/CD, observability, testing.

| Status | Task |
|---|---|
| ✅ | Jest test suite (14 test files: streakService, xpService, taskEngine, scoreCalculator, planGenerator, auth, planCache) |
| ✅ | TypeScript strict mode (no `any` types, strict null checks) |
| ✅ | ESLint configuration (consistent code style, import ordering) |
| ✅ | Path aliases (`@/`) configured in tsconfig |
| ✅ | EAS dev builds (iOS + Android, development profile) |
| ✅ | Supabase migrations (17 migrations, sequentially numbered) |
| ✅ | Prettier configuration |
| ⬜ | CI/CD pipeline (GitHub Actions: lint, typecheck, test, EAS build on PR) |
| ⬜ | E2E testing (Detox or Maestro — test full onboarding flow, task completion, cycle check-in) |
| ⬜ | Automated migration testing (apply all migrations to fresh DB, verify schema) |
| ⬜ | Crash reporting (Sentry: capture JS exceptions, native crashes) |
| ⬜ | Performance monitoring (Sentry: track cold start time, screen render time, API latency) |
| ⬜ | Code coverage reporting (Jest coverage thresholds: 80% lines, 70% branches) |
| ⬜ | Preview builds on PR (EAS Update: deploy preview channel for PR review) |
| ⬜ | Automated changelog generation (conventional commits → CHANGELOG.md) |
| ⬜ | Stale branch cleanup (GitHub Action: delete merged branches after 7 days) |
| ⬜ | Dependency auditing (weekly `npm audit`, automated PR for security patches) |
| ⬜ | Environment variable validation (startup check: all required env vars present) |
| ⬜ | Bundle size monitoring (track JS bundle size per build, alert on >5% increase) |
