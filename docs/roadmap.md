# Roadmap

> Phased delivery plan for FORGE. MVP shipped. Phase 2 targets Q3 2026. Phase 3 targets Q4 2026+.

---

## MVP (Shipped)

**Goal:** Complete end-to-end user journey — onboarding, 90-day plan, daily tasks, 3-day cycle check-ins, scoring, coaching, subscription.

**Prerequisite:** None

### Delivery by Sprint

| Sprint | Goal | Key Deliverables | Status |
|--------|------|------------------|--------|
| **S1** | Project foundations | Expo + React Native scaffold, Supabase client init, TypeScript strict mode, design tokens (Colors, Spacing, Typography), file-based routing with Expo Router, auth group and app group layout shells | ✅ Done |
| **S2** | Database & migrations | All 17 migrations applied: users, progress, plans, daily_tasks, cycles, weekly_reports, achievements, challenge_progress, task_library_selections, micro_sprints, pending_task_effects, rate_limits, claude_api_calls, season_events, referrals, private photo bucket, RLS policies | ✅ Done |
| **S3** | Auth & onboarding flow | Welcome carousel, 7-question quiz with quiz cache (in-memory + AsyncStorage draft persistence), email signup via Supabase Auth, session recovery on cold start, auth-checked guard in root layout, onboarding redirect enforcement (`onboarded` flag) | ✅ Done |
| **S4** | Plan generation | Codex AI proxy (`src/lib/anthropic.ts`), plan generator service, quiz-to-prompt mapping, Master Task Library (~150 curated tasks), `plan-loading` and `plan-reveal` screens, plan cache handoff, score estimator on reveal, plan saved to DB on confirm | ✅ Done |
| **S5** | Paywall & subscription | RevenueCat SDK integration, Basic tier ($11/mo), purchase/restore flows, `revenuecat-webhook` edge function for server-side validation, `isDevBypass()` for dev mode, post-purchase notification permissions + push scheduling, auth gate redirects to paywall | ✅ Done |
| **S6** | Daily tasks & home screen | `useTodaysTasks` hook, `useTasks` hook, `TaskCard` component, `XPBar` component, `StreakBadge` component, `HeatmapGrid` component, `AITipCard` component, home screen with 3-state handling (loading/content/empty), task completion with XP award + streak update + pending effect queue, `applyTaskEffect()` pillar drift (+0.5) | ✅ Done |
| **S7** | Cycle check-ins & photo analysis | 3-day photo capture (front/left/right), `imageService` (capture → compress → upload → signed URL), `photoAnalyser.ts` with Codex Vision (scan modes: face/full), `CycleAnalysis` type, `useCycles` hook, cycle history screen, before/after comparison, baseline photo deferred to day 3 with in-app prompt | ✅ Done |
| **S8** | Scoring system | 9-pillar scoring engine (`scoreCalculator.ts`), `PILLAR_DISPLAY` constants, pillar weights derived from quiz + face shape deltas (`faceShapeWeights.ts`), FORGE Optimisation Score (weighted composite 0–100), `useProgress` hook, `ScoreCard` component, progress screen with per-pillar breakdown | ✅ Done |
| **S9** | Coaching & AI insights | `coachingEngine.ts`: `generateDailyInsight()`, `generateWeeklyReport()`, `generateSeasonReport()`, `generateOnboardingCompliment()`, language stage routing (`stageForDay`), `weekly-report-generator` edge function (cron: Sunday 06:00 UTC), `weekly-reports` table, weekly report viewer screen, daily insight display on home screen | ✅ Done |
| **S10** | Gamification | XP system (`xpService.ts`) with 6 levels (Initiate → Grandmaster), streak service (`streakService.ts`) with milestone detection (7/30/60/90 days), challenge engine (`challengeEngine.ts`) with badge catalog (`badges.ts`), micro-sprint templates (`microSprints.ts`), First Strike celebration (`firstStrikeService.ts`, celebration modal), heatmap component | ✅ Done |
| **S11** | Season lifecycle & notifications | Program day advancement logic, season rollover at day 90, season-complete screen with story-format report, `pg_cron`-scheduled edge functions, push notification service (cycle prompts, weekly report ready, day-1 welcome push), guilt-free notification policy (factual reassurance, no urgency/shaming), `season_events` audit table | ✅ Done |
| **S12** | Profile, settings & share | Profile screen (avatar, plan info, subscription status), settings screen, account deletion flow (full data purge), sign-out with store reset, share card generation (`ShareScoreCard` component via `react-native-view-shot`), social share with pillar scores + before/after overlay, share service (`shareService.ts`), `useShareCard` hook | ✅ Done |
| **S13** | Polish, analytics & hardening | PostHog analytics (7 events: onboarding_complete, task_completed, cycle_checkin, weekly_report_viewed, share_card_generated, subscription_started, season_complete), referral code auto-generation on signup, signed URL system for private photo bucket, Claude API proxy with rate limiting (20 req/hr/user), `claude_api_calls` audit table, broken share tracking fix, notification guilt-language removal, program day advancement hardening | ✅ Done |

### What's In (grouped by actor)

**User**
- Welcome carousel with brand introduction
- 7-question quiz (goals, current routine, face shape self-assessment, time budget, priorities)
- Email signup via Supabase Auth
- AI-generated personalised 90-day plan (Codex selects from Master Task Library)
- Plan reveal screen with estimated FORGE Optimisation Score
- $11/mo Basic tier paywall (RevenueCat)
- Daily tasks (2–5 per day) with XP and streak tracking
- 3-day photo check-ins with Claude Vision analysis (face and full scan modes)
- FORGE Optimisation Score (0–100 weighted composite across 9 pillars)
- 9 per-pillar scores with delta tracking
- Daily AI coaching insight (≤25 words, language stage-aware)
- Weekly coaching reports (180–250 words, generated Sundays)
- 91-day heatmap (done/partial/missed/future)
- Challenge tracking with badge collection
- Micro-sprint templates
- Baseline photo capture (prompted on day 3)
- Cycle photo history with before/after comparison
- Season-complete celebration with story-format season report
- Season rollover (program day resets, weights recalibrated)
- First Strike celebration modal (first-ever task completion)
- Social share card generation (pillar scores, before/after, milestone callouts)
- Profile and settings screens
- Account deletion with full data purge

**System**
- Supabase Auth with Row-Level Security (RLS) on all tables
- 17 database migrations (users, progress, plans, daily_tasks, cycles, weekly_reports, achievements, challenge_progress, task_library_selections, micro_sprints, pending_task_effects, rate_limits, claude_api_calls, season_events, referrals, private photo bucket, RLS policies)
- Private photo storage (`user-photos-private` bucket) with signed URL generation (3600s expiry)
- `pg_cron`-scheduled edge functions: weekly report generation, streak risk detection, season rollover
- Claude AI proxy with per-user rate limiting (20 requests/hour)
- `revenuecat-webhook` edge function: server-side validation of INITIAL_PURCHASE, RENEWAL, CANCELLATION events
- PostHog analytics instrumentation (7 event types)
- Referral code auto-generation on signup
- Program day advancement engine with lapsed-user recovery
- Pending task effect queue with retry on app launch
- In-memory plan cache and quiz cache for onboarding handoff
- AI simulation mode for development (`EXPO_PUBLIC_AI_SIMULATION`)

### What's Not In
- Social features (friend comparison, leaderboards, community)
- Creator/influencer dashboard or custom plan marketplace
- Advanced plan customisation or mid-season plan regeneration
- Hardware integrations (smart mirror, wearable sync)
- AI-initiated micro-sprint engine
- Multi-language support
- Data export
- Admin UI (operator management via Supabase dashboard only)

---

## Phase 2 (Planned — Q3 2026)

**Goal:** Expand reach through social sharing and creator partnerships while deepening the coaching experience.

**Prerequisite:** MVP stable in production with crash rate below 0.3% and user retention metrics established.

### Feature Breakdown

#### Social & Sharing

| Feature | Description | Actor |
|---------|-------------|-------|
| Improved share cards | Animated progress cards with video export capability. Timeline of pillar scores over the season rendered as shareable motion graphic. | User |
| Push-to-share celebrations | When a user hits a major milestone (30-day streak, pillar +10 breakthrough, season complete), system prompts a one-tap share to Instagram Stories / TikTok. | User |
| Compare with friends | Opt-in friend comparison. Shows relative pillar scores and weekly completion rates. No leaderboard — comparison is framed as mutual encouragement, not competition. | User |
| Referral program v2 | Tracked referral codes with recipient attribution. "A friend who uses FORGE sent you" messaging on welcome screen. Referral dashboard for users showing how many friends joined. | User |

#### Creator Partnerships

| Feature | Description | Actor |
|---------|-------------|-------|
| Creator custom plans | Approved creators can design plan templates (task selections, pillar emphasis, micro-sprint triggers) published to a discoverable plan marketplace within the app. Plans carry the creator's name and photo. | User, Admin |
| Creator outreach dashboard | Internal dashboard for managing creator applications, reviewing plan templates, tracking creator-driven signups, and managing revenue share agreements. | Admin |
| Plan template CMS | Content management system for creating, versioning, and publishing plan templates without code changes. Supports task library curation per template. | Admin |
| Batch plan generation | Generate personalised plans for multiple users from the same creator template, optimising Claude API calls via prompt caching. | System |

#### Coaching Depth

| Feature | Description | Actor |
|---------|-------------|-------|
| Advanced analytics dashboard | Per-pillar trend graphs over time, completion rate by day-of-week, habit adherence score, milestone projections. "You're on track to hit 80 by day 60." | User |
| Plan regeneration mid-season | Users who feel their plan isn't working can request a regeneration — quiz answers and cycle data are fed into a new plan generation without losing existing progress. Day count preserved, tasks replaced from current day forward. | User |
| AI context depth improvement | Claude prompts enhanced with full task completion history and cycle delta trends for richer weekly reports and daily insights. | System |

### What's Not In (deferred to Phase 3)
- Voice-guided morning routines
- Hardware integrations
- Enterprise/team plans
- Real-time pillar drift detection
- Predictive score modeling
- Multi-language support

---

## Phase 3 (Planned — Q4 2026+)

**Goal:** Transform FORGE into an intelligent, proactive coach that anticipates needs and adapts in real-time.

**Prerequisite:** Phase 2 features stable, sufficient anonymised user data for AI model training (minimum 10,000 active users with 60+ days of data), and either Series A funding or revenue sufficient to support additional infrastructure costs.

### Intelligent Coaching

| Feature | Description | Actor |
|---------|-------------|-------|
| AI-initiated micro-sprints | System detects a stalled pillar (≤0.5 movement over 10+ days), analyses completion patterns, and suggests a targeted 7-day micro-sprint. User accepts or declines with one tap. Sprint tasks are hyper-focused on the stalled pillar. Post-sprint cycle check-in measures impact. | User, System |
| Predictive score modeling | ML model trained on anonymised user data predicts future pillar scores based on current trajectory and task completion patterns. Displayed as "projected score in 14 days" on progress screen. Increases plan adherence by making the outcome tangible. | System |
| Real-time pillar drift detection | Continuous monitoring of pillar score velocity. Detects early stagnation before it becomes a plateau. Triggers micro-sprint suggestions or coaching intervention before the user notices the stall. | System |
| Habit stacking suggestions | System analyses completion patterns (time of day, task order, skip patterns) and suggests optimised task ordering. "You're more consistent when you do posture before style — want to reorder your tasks?" | User, System |
| A/B testing framework | Infrastructure for testing plan variants, notification timing, coaching tone, and UI patterns. Enables data-driven product iteration without manual release cycles. Integrated with PostHog feature flags. | System |

### New Modalities

| Feature | Description | Actor |
|---------|-------------|-------|
| Voice-guided morning routines | Audio coaching track that walks the user through their morning tasks in sequence. "Five minutes remaining — start your cleanser now." Hands-free mode for bathroom use. Generated by text-to-speech from the day's task list. | User |
| Smart mirror integration | Camera capture and posture analysis via compatible smart mirrors (e.g., Withings, simple mirror + phone mount). Higher-quality photos with consistent angles and lighting. Cycle check-in triggered from the mirror. | User, System |
| Wearable data sync | Ingest sleep, heart rate variability, and activity data from Apple Health / Whoop / Oura. Sleep and nutrition pillar scores incorporate real biometric data alongside photo analysis. Users opt in per data source. | User, System |

### Scale & Reach

| Feature | Description | Actor |
|---------|-------------|-------|
| Enterprise/team plans | Group subscriptions for companies, gyms, or teams. Admin dashboard for group progress, shared challenges, and team-level insights. Per-seat pricing with volume discount. | User, Admin |
| Multi-language support | Full i18n of app UI, plan content, task library, and coaching output. Initial languages: Spanish, Portuguese, French, German, Japanese. Claude prompts translated with locale-specific cultural adaptation. | System |
| Referral network effects | When a referred user completes 30 days, both parties receive a bonus (extra micro-sprint, exclusive badge, or month discount). Creates a retention loop through social accountability. | User, System |

### What's Not In (beyond Phase 3)

| Out-of-scope | Reason |
|-------------|--------|
| Live 1:1 coaching (human) | Misaligned with AI-first product positioning. Service-heavy, unscalable. |
| Physical product line | Brand extension risk. Focus on software before considering CPG. |
| Marketplace for services (barbers, stylists, nutritionists) | Platform complexity. Two-sided marketplace dynamics require separate product strategy. |
| Prescription or medical claims | Regulatory exposure (FDA, HIPAA). FORGE is coaching, not medicine. |

---

## Timeline Summary

```
MVP (Shipped)
├── S1–S3: Foundation, database, auth, onboarding
├── S4–S5: Plan generation, paywall
├── S6–S8: Daily tasks, cycle check-ins, scoring
├── S9–S11: Coaching, gamification, season lifecycle
└── S12–S13: Profile, share, analytics, hardening

Phase 2 (Q3 2026)
├── Social sharing improvements
├── Creator partnerships & plan marketplace
├── Advanced analytics dashboard
└── Plan regeneration + AI context depth

Phase 3 (Q4 2026+)
├── AI-initiated micro-sprints & predictive scoring
├── Voice-guided routines & hardware integration
├── Enterprise/team plans & multi-language
└── A/B testing framework
```
