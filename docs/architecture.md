# FORGE — Architecture

> Premium male appearance transformation app. 90-day Season program.
> Stack: Expo 55 + React Native 0.83 + TypeScript 5.9 + Supabase + Claude AI + RevenueCat + PostHog
> Build: EAS (Expo Application Services)

---

## Tech Stack

| Layer | Technology | Notes |
|---|---|---|
| Mobile App | Expo ~55 with React Native 0.83, TypeScript 5.9 | Single codebase iOS + Android + Web |
| Routing | expo-router (file-based) | Stack navigator (auth) + NativeTabs (app on iOS 18+) + Tabs (fallback) |
| State | Zustand 5.0.12 | 3 stores: `useUserStore`, `useProgramStore`, `useProgressStore` |
| Backend | Supabase | PostgreSQL, Auth, Storage, Edge Functions |
| AI | Claude Sonnet 4.6 | Via server-side proxy Edge Function (`claude-proxy`) |
| Payments | RevenueCat | `react-native-purchases` 8.6.2 |
| Analytics | PostHog | `posthog-react-native` 4.44.0 |
| Animations | react-native-reanimated 4.2.1 | Transforms and opacity only |
| Native UI | @expo/ui, Liquid Glass module | SwiftUI on iOS 26+; `LiquidGlassTabBar`, `ForgeScoreCard` |
| Storage (tokens) | expo-secure-store | Auth tokens (iOS Keychain / Android Keystore) |
| Storage (fallback) | @react-native-async-storage 2.2.0 | Web fallback where SecureStore unavailable |
| Camera | expo-camera, expo-image-picker, expo-image-manipulator | Photo capture, library pick, compress/crop |
| Notifications | expo-notifications | Local + scheduled push |
| Testing | Jest 29.7.0 with ts-jest | Unit tests for services (streak, XP, scores, tasks) |
| Build / CI | EAS (Expo) | `eas build`, `eas submit`, `eas update` |

---

## Running Locally

### Prerequisites

- Node 22+
- Xcode 16+ (iOS simulator)
- Expo CLI (`npx expo`)
- Supabase project (free tier or self-hosted)

### Setup

```bash
# 1. Clone and install
git clone <repo-url>
cd forge-ai
npm install

# 2. Create environment file
cp .env.example .env.local

# 3. Fill in credentials in .env.local:
#    EXPO_PUBLIC_SUPABASE_URL=https://[your-project].supabase.co
#    EXPO_PUBLIC_SUPABASE_ANON_KEY=eyJhbGci...
#    EXPO_PUBLIC_ANTHROPIC_KEY=sk-ant-api03-...
#    EXPO_PUBLIC_REVENUECAT_APPLE_KEY=appl_...
#    EXPO_PUBLIC_POSTHOG_KEY=phc_...
#    EXPO_PUBLIC_POSTHOG_HOST=https://us.i.posthog.com
#
#    For dev without real API calls:
#    EXPO_PUBLIC_AI_SIMULATION=true

# 4. Run Supabase migrations (in Supabase SQL Editor)
#    Execute supabase/migrations/001–017 in order

# 5. Start the dev server
npx expo start

# Press i for iOS simulator
# Press a for Android emulator
# Press w for web
```

### RevenueCat Testing

RevenueCat requires an EAS development build — it does not work in Expo Go:
```bash
npx expo run:ios   # or npx expo run:android
```

---

## Environment Files

| File | Purpose | Committed |
|---|---|---|
| `.env.example` | Template with all required keys, placeholder values | Yes |
| `.env.local` | Developer-specific credentials | No (gitignored) |
| `.secrets.local` | Build-time secrets (loaded by dotenv in `app.config.ts`) | No (gitignored) |
| `.env.production` | Production credentials | No (set via `eas secret:create`) |

### Required Variables

| Variable | Used By | Notes |
|---|---|---|
| `EXPO_PUBLIC_SUPABASE_URL` | `src/lib/supabase.ts` | Supabase project URL |
| `EXPO_PUBLIC_SUPABASE_ANON_KEY` | `src/lib/supabase.ts` | Supabase anonymous key |
| `EXPO_PUBLIC_ANTHROPIC_KEY` | `supabase/functions/claude-proxy/` | Server-side only via edge function proxy |
| `EXPO_PUBLIC_REVENUECAT_APPLE_KEY` | `src/lib/revenuecat.ts` | RevenueCat iOS API key |
| `EXPO_PUBLIC_POSTHOG_KEY` | `src/services/analytics/postHogService.ts` | PostHog project API key |
| `EXPO_PUBLIC_POSTHOG_HOST` | `src/services/analytics/postHogService.ts` | PostHog instance host |
| `EXPO_PUBLIC_APP_ENV` | Build config | `development` or `production` |
| `EXPO_PUBLIC_AI_SIMULATION` | `src/services/ai/photoAnalyser.ts` | `true` = use mocked AI responses, skip real API calls |

---

## Project Structure

```
forge-ai/
├── app/                          # Expo Router file-based routing (32 files)
│   ├── _layout.tsx               # Root layout — auth guard, RevenueCat config, effect retry
│   ├── index.tsx                 # Redirect to splash
│   ├── (auth)/                   # Onboarding flow (no bottom tabs)
│   │   ├── _layout.tsx           # Auth stack navigator
│   │   ├── splash.tsx            # Animated loading with session recovery
│   │   ├── welcome.tsx           # 3-slide carousel intro
│   │   ├── signup.tsx            # Email/password signup + login toggle
│   │   ├── quiz/                 # 7-question quiz (step-based dynamic routes)
│   │   ├── plan-loading.tsx      # AI plan generation spinner with progress
│   │   ├── plan-reveal.tsx       # Plan display, save to DB, navigate to paywall
│   │   ├── paywall.tsx           # RevenueCat $11/mo purchase screen
│   │   ├── estimated-score.tsx   # Pre-signup score estimate from quiz answers
│   │   └── baseline-photo.tsx    # Edge case: mid-onboarding baseline photo recovery
│   └── (app)/                    # Main authenticated app
│       ├── _layout.tsx           # App stack + tab navigator
│       ├── (tabs)/               # Bottom tabs (NativeTabs on iOS 18+)
│       │   ├── _layout.tsx       # Tab bar config (LiquidGlassTabBar on iOS 26+)
│       │   ├── index.tsx         # Home / Daily dashboard
│       │   ├── progress.tsx      # Progress stats + heatmap + pillar scores
│       │   ├── program.tsx       # Phase roadmap + milestones
│       │   ├── goals.tsx         # Challenges + achievements
│       │   ├── sprints.tsx      # Micro-sprints
│       │   └── profile.tsx       # Profile + settings (SwiftUI on iOS 26+)
│       ├── cycle.tsx             # Camera / 3-day photo check-in
│       ├── baseline-photo.tsx    # Day 3 in-app photo prompt
│       ├── photo-compare.tsx     # Before/after cycle comparison
│       ├── photo-timeline.tsx    # Scrollable cycle photo history
│       ├── share-card.tsx        # Social sharing score card
│       ├── season-complete.tsx   # End-of-90-day celebration + season report
│       ├── sprint-detail.tsx     # Micro-sprint detail view
│       ├── task/[taskId].tsx     # Single task detail
│       ├── pillar/[pillar].tsx   # Pillar drill-down with sparkline
│       ├── routine/[slug].tsx    # Routine detail
│       └── weekly-report/[week].tsx # AI coaching report
├── src/
│   ├── components/
│   │   └── ui/                   # 40+ reusable UI components
│   │       (AITipCard, CategoryBadge, ChallengeShareCard, CompletionCard,
│   │        CycleComparisonModal, CycleResultCard, DotTexture, ErrorBoundary,
│   │        FaceGuideOverlay, FirstStrikeModal, ForgeCard, ForgeEmptyState,
│   │        ForgeScoreCard, GrainOverlay, HabitGrid, HeatmapGrid,
│   │        LightingIndicator, MeshGradient, MilestoneTimeline, NativeControls,
│   │        PhaseProgressBar, PhaseRoadmap, PhotoCycleCard, PhotoTimeline,
│   │        PrimaryButton, ScoreCard, Season2TeaserCard, SecondaryButton,
│   │        SegmentBar, ShareScoreCard, SparklineChart, StatusStrip,
│   │        StreakBadge, StreakIndicator, StreakMilestoneModal, TaskCard,
│   │        ThisWeekCard, TopScrollFade, WarmBackground, XPBar)
│   ├── hooks/                    # 30 hooks — screen-facing reactive layer
│   │   (index, useAccount, useAchievements, useAgingVelocity, useAnalytics,
│   │    useAuth, useBaselineStatus, useBaselineUpload, useChallenges,
│   │    useCycleHistory, useCycles, useFirstStrike, useHeatmap, useInsights,
│   │    useNotifications, useOnboarding, usePhotoCapture, usePhotoTimeline,
│   │    usePlanGeneration, useProgramAdvancement, useProgress,
│   │    useSeasonComplete, useShareCard, useSprints, useStreak,
│   │    useSubscription, useTasks, useTodaysTasks, useWeeklyReport, useXP)
│   ├── services/                 # Business logic layer — NO UI code here
│   │   ├── ai/                   # AI integration
│   │   │   ├── planGenerator.ts      # Quiz + library → 90-day plan via Claude
│   │   │   ├── photoAnalyser.ts      # Cycle photo analysis (Claude Vision)
│   │   │   ├── coachingEngine.ts     # Daily insight + weekly/season reports
│   │   │   ├── agingVelocityService.ts # Pace-of-change metric (Season 2+)
│   │   │   ├── sanitize.ts           # AI output sanitization
│   │   │   └── prompts/              # AI system prompts
│   │   │       ├── planPrompt.ts     # 90-day plan generation prompt
│   │   │       ├── photoPrompt.ts    # Claude Vision analysis prompt
│   │   │       ├── coachingPrompt.ts # Daily/weekly/season coaching prompt
│   │   │       └── compliPrompt.ts   # Onboarding compliment prompt
│   │   ├── analytics/            # postHogService — 7 event types
│   │   ├── challenges/           # challengeEngine — start, track, complete
│   │   ├── firstStrike/         # firstStrikeService — Day 1 module
│   │   ├── image/                # imageService, signedUrl generation
│   │   ├── notifications/        # notificationService — schedule, cancel
│   │   ├── plan/                 # planCache — bridge plan-loading → plan-reveal
│   │   ├── program/              # programAdvancement, seasonTransition
│   │   ├── scores/               # scoreCalculator, quizScoreEstimator
│   │   ├── share/                # shareService — dynamic share card generation
│   │   ├── sprints/              # microSprintEngine
│   │   ├── streak/               # streakService — calculation, milestones
│   │   ├── tasks/                # taskEngine — CRUD, complete, XP/stats
│   │   └── xp/                   # xpService — XP awards, level-up detection
│   ├── store/                    # Zustand global state (3 stores)
│   │   ├── userStore.ts          # User profile, subscription, auth state
│   │   ├── programStore.ts       # Current plan, today's tasks, phases
│   │   └── progressStore.ts      # XP, streaks, pillar scores, optimisation score
│   ├── lib/                      # SDK wrappers — thin wrappers around external SDKs
│   │   ├── anthropic.ts          # Claude API — callClaude, callClaudeVision
│   │   ├── auth.ts               # Supabase auth — signUp, signIn, signOut, deleteAccount
│   │   ├── supabase.ts           # Supabase client singleton
│   │   ├── revenuecat.ts         # RevenueCat — configure, purchase, restore
│   │   └── planCache.ts          # In-memory cache for plan handoff between screens
│   ├── constants/                # Immutable data — design tokens, libraries, configs
│   │   ├── design.ts             # ALL design tokens — single source of truth
│   │   ├── swiftui.ts            # SwiftUI token bridge for @expo/ui components
│   │   ├── taskLibrary.ts        # ~150 curated Master Task Library entries
│   │   ├── phases.ts             # PHASE_DISPLAY — phase name constants
│   │   ├── pillars.ts            # PILLAR_DISPLAY, VISIBLE_PILLARS — pillar name constants
│   │   ├── phasedIntroduction.ts # weekNumber → eligibleTaskIds schedule
│   │   ├── levels.ts             # XP thresholds + 6 level names
│   │   ├── badges.ts             # Badge catalog
│   │   ├── challenges.ts         # Challenge templates
│   │   ├── microSprints.ts       # Micro-sprint templates
│   │   ├── faceShapeWeights.ts   # Face shape → pillar weight deltas
│   │   └── routines.ts           # Routine definitions
│   ├── types/                    # TypeScript type definitions
│   │   ├── database.ts           # Supabase row types — DbUser, DbProgress, DbCycle, etc.
│   │   ├── plan.ts               # QuizAnswers, GeneratedPlan, DailyTask, LibraryTask
│   │   ├── ai.ts                 # CycleAnalysis, PillarScore, FaceShape, WeeklyReport
│   │   ├── scores.ts             # Pillar, PillarWeights, PillarScores, OptimisationScore
│   │   └── vendor.d.ts          # Third-party module declarations
│   ├── utils/                    # Utility functions
│   │   ├── stagger.ts            # Stagger animation helper
│   │   ├── sparkline.ts          # Sparkline data processing
│   │   └── grainOverlay.ts       # Grain texture utility
│   └── config/                   # Runtime configuration
│       └── aiSimulation.ts       # AI simulation mode toggle + mock data
├── supabase/
│   ├── migrations/               # 17 SQL migrations (001–017)
│   │   (001_initial_schema, 002_storage_setup, 003_nine_pillar_migration,
│   │    004_plan_start_date, 005_timezone_field, 006_edge_function_tables,
│   │    007_schedule_edge_functions, 008_security_hardening,
│   │    009_claude_api_calls, 010_private_photo_bucket, 011_referral_codes,
│   │    012_program_day_advancement, 013_first_strike,
│   │    014_subscription_columns, 015_cycle_number_auto_assign,
│   │    016_task_library_selections_user_id, 017_pending_task_effects)
│   └── functions/                # 5 Supabase Edge Functions (Deno)
│       ├── claude-proxy/         # Server-side Claude API proxy
│       ├── weekly-report-generator/ # Sunday 06:00 — generate coaching reports
│       ├── streak-risk-notifier/    # Daily 21:00 — streak risk detection
│       ├── season-rollover-handler/ # Daily 00:00 — 90-day season transitions
│       └── revenuecat-webhook/      # RevenueCat event webhook handler
├── modules/                      # Native Swift modules (iOS)
│   ├── liquid-glass/             # Liquid Glass UI module (iOS 26+)
│   ├── forge-activity/           # Live Activity bridge
│   ├── forge-shared/             # App Group shared data writer
│   ├── forge-haptics/            # Haptic feedback engine
│   └── forge-symbol-effects/     # SF Symbol effect animations
├── assets/                       # Static assets (images, icons, fonts)
├── ios/                          # iOS native project (Xcode)
├── android/                      # Android native project
├── frontend/                     # Next.js web landing page (secondary)
├── __tests__/                    # Top-level enforcement tests
├── documentation/                # Additional documentation
│   └── creator_outreach.md       # Creator outreach template
├── docs/                         # Project documentation
│   ├── README.md
│   ├── data-model.md             # Full database schema reference
│   ├── glossary.md               # Terminology reference
│   └── personas.md               # Target user personas
├── AGENTS.md                     # Codex AI development rules
├── .env.example                  # Environment variable template
├── .env.local                    # Developer credentials (gitignored)
├── .secrets.local                # Build-time secrets (gitignored)
├── app.config.ts                 # Expo app configuration
├── babel.config.js               # Babel configuration
├── tsconfig.json                 # TypeScript configuration
├── jest.config.js                # Jest configuration
├── eas.json                      # EAS Build configuration
├── package.json                  # Dependencies and scripts
├── FORGE-BUILD-SPECIFICATION.md  # Build specification
├── PRODUCT_OVERVIEW.md           # Product overview
└── CLAUDE.md                     # Claude/Anthropic IDE rules
```

---

## External Service Integrations

### Supabase

**Auth**
- Email/password via `@supabase/supabase-js`. No social logins, no magic link.
- Tokens stored in `expo-secure-store` (iOS Keychain / Android Keystore).
- Web fallback: `@react-native-async-storage` when SecureStore is unavailable.
- Session persistence with auto-refresh via Supabase client's built-in `autoRefreshToken`.
- Auth state changes monitored by `onAuthStateChange` listener in `app/_layout.tsx`.
- On sign out: `userStore.reset()`, `programStore.reset()`, `progressStore.reset()`.

**Database**
- PostgreSQL 15 accessed via Supabase JS client.
- Row Level Security on all 16 tables (migration 008 hardened).
- Dual-policy model: `service_role` (full access, `USING true`) + `authenticated` (`auth.uid() = user_id`).
- Every table has both policies. No anonymous access to user data.
- Full schema documented in `docs/data-model.md`.

**Storage**
- Two buckets: `user-photos` (legacy, now private) and `user-photos-private` (current).
- Object path convention: `cycles/{user_id}/{filename}`.
- Storage RLS: authenticated users can only read/write/delete their own folder.
- Private bucket access: time-limited signed URLs (3600s default) generated via Supabase Storage API.
- No public read policy on the private bucket. Public bucket's public policy was dropped in migration 010.

**Edge Functions**
- 5 deployed functions (Deno runtime):
  - `claude-proxy`: All Claude API calls route through this. Validates user's Supabase token, checks rate limits (20 req/hr/user via `claude_api_calls` table), strips CORS headers, forwards to Anthropic API. Client never sees the Anthropic key.
  - `weekly-report-generator`: Scheduled via `pg_cron` every Sunday 06:00 UTC. Iterates active users, calls `coachingEngine.generateWeeklyReport()`, inserts into `weekly_reports`.
  - `streak-risk-notifier`: Scheduled daily 21:00 UTC. Checks `users.last_active_date` vs timezone-aware local time. Queues notifications in `pending_notifications`.
  - `season-rollover-handler`: Scheduled daily 00:00 UTC. Finds users at `program_day >= 90` with `season = 1`, increments season, resets `program_day` to 1, writes `season_events` audit row.
  - `revenuecat-webhook`: Receives RevenueCat server-side events (INITIAL_PURCHASE, RENEWAL, CANCELLATION, etc.), syncs `subscription_tier` / `subscription_expires_at` on `users` table.
- Authenticated via `cron_secret` stored in Supabase Vault. Functions call `verify_cron_secret()` on each invocation.

---

### Codex AI (Claude)

All AI calls route through the `claude-proxy` Supabase Edge Function. The client never holds or transmits the Anthropic API key.

**Architecture:**
```
Mobile App (Expo)
  │ POST /functions/v1/claude-proxy
  │ Header: Authorization: Bearer <supabase_access_token>
  │ Body: { system_prompt, user_message, image_urls?, model? }
  ▼
claude-proxy Edge Function (Deno)
  │ 1. Validate Supabase JWT
  │ 2. Check rate limit (COUNT claude_api_calls WHERE user_id = X AND created_at > NOW() - 1h)
  │ 3. Rate limit exceeded? → 429
  │ 4. Forward to Anthropic API
  │ 5. Log call to claude_api_calls
  │ 6. Return response to client
  ▼
Anthropic API
  Model: claude-sonnet-4-6
  Prompt caching: cache_control { type: "ephemeral" } on system prompts
```

**Client API** (`src/lib/anthropic.ts`):
```typescript
// Text generation (plan generation, coaching)
callClaude(systemPrompt: string, userMessage: string): Promise<string>

// Vision analysis (cycle photos)
callClaudeVision(systemPrompt: string, imageUrls: string[], userMessage: string): Promise<string>
```

**Vision:** Images are sent as URLs (not base64). URLs must be publicly accessible or Supabase signed URLs. The `imageService` uploads photos to the private bucket, then generates signed URLs for Claude Vision analysis.

**AI Simulation Mode:** When `EXPO_PUBLIC_AI_SIMULATION=true`, the `photoAnalyser` returns mock pillar scores and insights without calling the Claude API. Controlled by `src/config/aiSimulation.ts`. Used for development and UI testing.

---

### RevenueCat

**SDK:** `react-native-purchases` 8.6.2, configured in `app/_layout.tsx` on app boot.

**Package:** `basic_monthly` at $11/mo
**Entitlement:** `basic`

**Flow:**
1. `configure(userId)` called in root layout with Supabase user ID
2. `purchaseBasic()` called when user taps CTA on paywall
3. RevenueCat processes via Apple App Store (iOS) or Google Play (Android)
4. `revenuecat-webhook` edge function receives server-side event
5. Edge function syncs `users.subscription_tier` to `basic` and `users.subscription_expires_at`

**Dev bypass:** When `__DEV__` is true and `EXPO_PUBLIC_APP_ENV` is not `production`, returns mock subscription data — skips real RevenueCat purchase flow.

**Paywall screen:** Single CTA for $11/mo. "Maybe later" link styled as low-contrast text. 3-day free trial messaging. No tier-gating logic anywhere in the app — single Basic tier.

---

### PostHog

**7 instrumented events (7 event types):**

| Event | Trigger | Properties |
|---|---|---|
| `WELCOME_VIEWED` | Welcome screen mount | — |
| `WELCOME_SLIDE_VIEWED` | Slide change (3 slides) | `slide_index` |
| `QUIZ_STARTED` | Quiz init | — |
| `QUIZ_STEP_COMPLETED` | Each Q (1–7) | `step_number`, `answer` |
| `QUIZ_COMPLETE` | Final question answered | All quiz answers |
| `SIGNUP_VIEWED` | Signup screen mount | — |
| `SIGNUP` | Successful signup | `method: email` |
| `PLAN_GENERATING` | Plan loading start | — |
| `PLAN_GENERATION_FAILED` | Plan generation error | `error_message` |
| `PLAN_REVEALED` | Plan reveal screen | `plan_name` |
| `PHOTO_UPLOADED` | Any photo upload | `cycle_type`, `cycle_number` |
| `CYCLE_COMPLETED` | Cycle analysis returned | `cycle_number`, `optimisation_score` |

**User identification:** `identifyUser(userId)` called on signup and login. `resetAnalytics()` called on sign out.

---

## Key Subsystems

### Prompt System

Four system prompt files in `src/services/ai/prompts/`:

| File | Purpose | Output |
|---|---|---|
| `planPrompt.ts` | 90-day plan generation from quiz + task library | JSON: `GeneratedPlan` |
| `photoPrompt.ts` | Claude Vision cycle photo analysis | JSON: `CycleAnalysis` (9 pillars, face shape, narrative) |
| `coachingPrompt.ts` | Daily insights, weekly reports, season reports | String or markdown |
| `compliPrompt.ts` | Onboarding compliment, season report summary | Short string (15–25 words) |

All prompts enforce:
- Scientific, specific voice. No exclamation marks.
- Never say: handsome, attractive, hot, ugly.
- Never address the user by name.
- Never use "great job" or generic motivation.
- Output exactly the requested format (JSON or string). No preamble, no markdown wraps.

### State Machines

#### Onboarding State Machine

```
            ┌─────────┐
            │  SPLASH  │ (session check + recovery)
            └────┬─────┘
                 │
          ┌──────▼──────┐
          │   WELCOME   │ (3-slide carousel)
          └──────┬──────┘
                 │
          ┌──────▼──────┐
          │    QUIZ     │ (7 questions, answers cached in Zustand)
          └──────┬──────┘
                 │
          ┌──────▼──────┐
          │  ESTIMATED  │ (score preview from quiz answers)
          │   SCORE     │
          └──────┬──────┘
                 │
          ┌──────▼──────┐
          │   SIGNUP    │ (email + password or login)
          └──────┬──────┘
                 │
          ┌──────▼──────┐
          │   PLAN      │ (Claude generates 90-day plan from quiz + library)
          │  LOADING    │
          └──────┬──────┘
                 │
          ┌──────▼──────┐
          │   PLAN      │ (user reviews, taps "Begin" → saves plan to DB)
          │   REVEAL    │ (sets onboarded = true)
          └──────┬──────┘
                 │
          ┌──────▼──────┐
          │  PAYWALL    │ ($11/mo, RevenueCat purchase flow)
          └──────┬──────┘
                 │
          ┌──────▼──────┐
          │  MAIN APP   │ notifications permissions + schedule
          │  (tabs)     │
          └──────┬──────┘
                 │ (day 3 after plan_start_date)
          ┌──────▼──────┐
          │  BASELINE   │ in-app prompt via notification or banner
          │   PHOTO     │ (app/(app)/baseline-photo.tsx)
          └─────────────┘
```

#### Session Recovery State Machine

```
              ┌──────────┐
              │ APP BOOT │
              └────┬─────┘
                   │
         ┌─────────▼─────────┐
         │ onAuthStateChange │
         │     listener      │ (in app/_layout.tsx)
         └────┬──────┬──────┘
              │      │
     session? │      │ no session?
              │      │
    ┌─────────▼──┐  ┌▼──────────────┐
    │ query users│  │ getSession()  │
    │ by auth UID│  │ fallback      │
    └─────┬──────┘  └──┬────────────┘
          │            │
    ┌─────▼─────┐ ┌───▼────────┐
    │ dbUser    │ │ dbUser     │
    │ found?    │ │ found?     │
    └─────┬─────┘ └──┬─────────┘
          │          │
    yes   │     no   │    no    │ yes
          │          │          │
    ┌─────▼──────┐   │   ┌──────▼──────┐
    │ onboarded? │   │   │ onboarded?  │
    └──┬─────┬───┘   │   └──┬─────┬────┘
       │     │        │      │     │
    yes│  no │        │   yes│  no │
       │     │        │      │     │
  ┌────▼─┐ ┌▼───────┐│ ┌────▼─┐ ┌▼───────┐
  │/(app)│ │/(auth)/││ │/(app)│ │/(auth)/│
  │/(tabs│ │welcome ││ │/(tabs│ │welcome │
  └──────┘ └────────┘│ └──────┘ └────────┘
                     │
              ┌──────▼───────┐
              │ /(auth)/     │
              │   splash     │
              └──────────────┘
```

#### Season Lifecycle

```
SEASON 1 (days 1–90)
  day 1:    First Strike module completion
  days 1–14:  Outcome language stage (what this does for you)
  days 15–30: Habit language stage (building the routine)
  day 3:    Baseline photo prompt (in-app, app/(app)/baseline-photo.tsx)
  days 31–60: Activation phase, mechanism language, category names visible
  every 3 days: Cycle check-in (photo → Claude Vision → scores)
  every Sunday: Weekly AI coaching report generated
  days 61–90: Optimisation phase, advanced tier tasks
  day 90:   Season complete screen + end-of-season report
        │
        ▼ (auto-rollover via season-rollover-handler edge function)
SEASON 2 (days 1–90)
  Voice pillar unlocked (scored from task completion rate)
  Recalibrated pillar weights based on Season 1 delta
  Aging velocity metric available (pace of change)
  New task library selections generated
  program_day reset to 1
        │
        ▼
SEASON 3+ (repeat)
```

---

### Plan Handoff (Cache Pattern)

The plan cache (`src/lib/planCache.ts`) is an in-memory singleton that bridges the `plan-loading` and `plan-reveal` screens during onboarding. It is necessary because Expo Router navigation replaces the screen context — the generated plan cannot be passed as a route param (too large).

**Flow:**
1. `plan-loading.tsx` calls `planGenerator.generatePlan()` → Claude returns `GeneratedPlan`
2. Plan stored in module-level `_plan` variable in `planCache.ts`
3. `router.replace("/(auth)/plan-reveal")` navigates to reveal screen
4. `plan-reveal.tsx` calls `getCachedPlan()` → receives plan → renders UI
5. User taps "Begin" → `savePlanToDatabase(userId, plan)` → inserts plan + daily_tasks + task_library_selections
6. Cache cleared after save

Same pattern used for:
- `_baselineAnalysis` — baseline photo analysis result between `baseline-photo` and result display
- `_estimatedScore` — quiz-based score estimate between quiz and estimated-score screen

---

### Pending Task Effects Queue

Task completion triggers a +0.5 score drift on the task's pillar. If `applyTaskEffect()` fails due to network unavailability:

1. Effect is inserted into `pending_task_effects` table (columns: `user_id`, `task_id`, `pillar`, `drift`, `created_at`, `applied_at` NULL)
2. On next `app/_layout.tsx` mount: `retryPendingEffects(userId)` queries unapplied effects (`applied_at IS NULL`)
3. Each pending effect is retried: calls `applyTaskEffect(userId, pillar)` → on success, sets `applied_at = NOW()`
4. Failed retries remain for next boot. No data loss. Effects are idempotent — safe to retry multiple times.

---

### Design System

Single source of truth: `src/constants/design.ts`.

**Colors:**
- Backgrounds: `#0A0A0A` (bg), `#141414` (surface), `#1C1C1C` (elevated)
- Brand accents: `#00C4A7` (teal — progress, active states, scores), `#E8A400` (gold — CTAs, streaks, badges)
- Text: `#F7F4EF` (primary), `#5A5A5A` (secondary), `#3A3A3A` (tertiary)
- Semantic: `#E84545` (danger)
- 9 pillar colors: `#B8A4E8` (facial), `#00C4A7` (skin), `#E8A400` (grooming), `#D46A9E` (hair), `#E8744A` (fitness), `#8B7FE8` (style), `#5A8AE8` (sleep), `#6EC88A` (nutrition), `#C8A46E` (voice)

**Typography:** Inter font. Sizes: 64 (hero), 32 (display), 24 (title), 17 (heading), 13 (body), 11 (caption), 9 (label). Weights: 400 and 700 only. No intermediate weights.

**Spacing:** xs:2, sm:4, md:8, lg:16, xl:24, xxl:32, xxxl:48. Screen padding: 24.

**Files:**
| File | Purpose |
|---|---|
| `design.ts` | Design tokens — Colors, Typography, Spacing, Radius, Animation |
| `swiftui.ts` | Token bridge for native SwiftUI components (@expo/ui) |
| `phases.ts` | `PHASE_DISPLAY` — phase names (Foundation, Activation, Optimisation) |
| `pillars.ts` | `PILLAR_DISPLAY`, `VISIBLE_PILLARS`, `pillarDisplayName()` — pillar name constants |
| `levels.ts` | 6 XP level thresholds (Initiate → Apex) |
| `taskLibrary.ts` | ~150 curated Master Task Library entries |
| `phasedIntroduction.ts` | weekNumber → eligibleTaskIds schedule |
| `badges.ts` | Badge catalog |
| `challenges.ts` | Challenge templates |
| `microSprints.ts` | Micro-sprint event templates |
| `faceShapeWeights.ts` | Face shape → pillar weight deltas |
| `routines.ts` | Routine definitions |

---

### Hook Architecture

All screens import hooks from `src/hooks/`. Hooks call services. Services call Supabase/Anthropic. Screens never call Supabase directly.

**Key hooks:**

| Hook | Returns | Uses |
|---|---|---|
| `useTasks` | `tasks[]`, `completedCount`, `totalTasks`, `completeTask()`, `refetch()` | Task engine service |
| `useTodaysTasks` | Today's tasks from `programStore` | Zustand store (hydrated from Supabase) |
| `useStreak` | `currentStreak`, `longestStreak`, `isAtRisk`, `isMilestone` | Streak service |
| `useXP` | `totalXP`, `level`, `levelName`, `xpToNextLevel`, `leveledUp` | XP service |
| `useProgress` | `pillarScores` (9), `optimisationScore`, `programDay`, `season`, `faceShape`, `deltaVsBaseline` | Progress service + store |
| `useCycles` | `history[]`, `latest`, `daysUntilNextCycle`, `canCheckInNow` | Cycles service |
| `useSubscription` | `isActive`, `expiresAt`, `purchase()`, `restore()` | RevenueCat + Supabase |
| `useHeatmap` | `cells[]` (done/missed/upcoming), `completedCount` | Daily tasks service |
| `useAchievements` | `badges[]`, `totalUnlocked` | Achievements service |
| `useChallenges` | `activeChallenges[]`, `completedChallenges[]` | Challenge engine |
| `usePlanGeneration` | `generatePlan()`, `savePlan()`, `isGenerating`, `error` | Plan generator + plan cache |
| `usePhotoCapture` | `takePhoto()`, `pickFromLibrary()`, `uploadPhoto()`, `isUploading` | Image service |
| `useBaselineUpload` | `uploadBaseline()`, `hasBaseline`, `isUploading` | Image service + signed URLs |
| `useCycleHistory` | `cycles[]`, `baseline`, `latestCycle` | Cycles service |
| `usePhotoTimeline` | `photos[]`, `loadMore()` | Signed URL + cycles service |
| `useShareCard` | `generateCard()`, `shareCard()`, `isGenerating` | Share service + react-native-view-shot |
| `useAuth` | `signUp()`, `signIn()`, `signOut()`, `deleteAccount()` | Auth lib |
| `useOnboarding` | `currentStep`, `goNext()`, `goBack()`, `reset()` | Local state machine |
| `useNotifications` | `requestPermission()`, `scheduleAll()`, `cancelAll()`, `hasPermission` | Notification service |
| `useAccount` | `updateProfile()`, `updateTimezone()`, `deleteAccount()` | User store + Supabase |
| `useAnalytics` | `track()`, `identify()`, `reset()` | PostHog service |
| `useFirstStrike` | `isCompleted`, `completeFirstStrike()` | First Strike service |
| `useSprints` | `activeSprint`, `startSprint()`, `completeSprint()` | Micro-sprint engine |
| `useProgramAdvancement` | `advanceDay()`, `currentDay`, `currentPhase` | Program advancement service |
| `useSeasonComplete` | `isSeasonEnd`, `seasonReport`, `startNewSeason()` | Season transition service |
| `useWeeklyReport` | `latestReport`, `reports[]`, `loadReport()` | Weekly reports service |
| `useInsights` | `dailyInsight`, `refreshInsight()` | Coaching engine |
| `useBaselineStatus` | `hasBaseline`, `daysUntilRequired`, `needsBaseline` | User store |
| `useAgingVelocity` | `velocity`, `isAvailable` (Season 2+) | Aging velocity service |

---

### Zustand Store Architecture

Three stores in `src/store/`. Each is hydrated from Supabase on app mount.

**`useUserStore`:**
```
State:
  user: DbUser | null
  isHydrated: boolean
  isAuthenticated: boolean
Actions:
  setUser(user)
  updateUser(partial)
  hydrate()              // fetch from Supabase
  reset()                // clear on sign out
```

**`useProgramStore`:**
```
State:
  plan: GeneratedPlan | null
  todaysTasks: DailyTask[]
  currentPhase: Phase
  isHydrated: boolean
Actions:
  setPlan(plan)
  setTodaysTasks(tasks)
  markTaskComplete(taskId)
  hydrate()              // fetch plan + today's tasks from Supabase
  reset()
```

**`useProgressStore`:**
```
State:
  pillarScores: PillarScores
  optimisationScore: number
  currentStreak: number
  longestStreak: number
  totalXP: number
  level: number
  levelName: string
  isHydrated: boolean
Actions:
  setPillarScores(scores)
  updatePillarScore(pillar, value)
  setXP(xp)
  setStreak(streakData)
  hydrate()              // fetch from Supabase
  reset()
```

---

### Key Architecture Rules

1. **Screens import hooks, hooks call services, services call Supabase.** Never skip a layer.
2. **No hardcoded colors.** Always `Colors.*` from `src/constants/design.ts`.
3. **No hardcoded spacing.** Always `Spacing.*`.
4. **Font sizes only:** 64, 32, 24, 17, 13, 11, 9. Weights only: 400, 700.
5. **Every async function has try/catch** with user-visible error state + retry.
6. **Never use `any`** TypeScript types.
7. **Every screen handles 3 states:** loading (skeleton), content, empty/error.
8. **No shadows.** Flat dark surfaces with opacity borders only.
9. **Single Basic tier at $11/mo.** No tier-gating logic anywhere.
10. **Cycle photo cadence is every 3 days, always.** No Sunday-only or weekly logic.
11. **Baseline photo deferred to day 3.** Onboarding flow: splash → welcome → quiz → signup → plan-loading → plan-reveal → paywall → /(app). Baseline photo prompted in-app on day 3 via `app/(app)/baseline-photo.tsx`.
12. **Phase names from `PHASE_DISPLAY`** in `src/constants/phases.ts`. Never hardcode "Foundation" / "Activation" / "Optimisation" in JSX.
13. **Pillar UI from `PILLAR_DISPLAY`** and `pillarDisplayName()`. Surface only `VISIBLE_PILLARS` by default.
14. **Coaching strings obey `stageForDay(day)`** — outcome / habit / mechanism layers.
15. **Notifications must not use guilt language.** No "we miss you", "your streak is at risk", "don't lose progress". Factual reassurance only.

---

## Scheduled Jobs

| Job | Schedule | Edge Function | Purpose |
|---|---|---|---|
| `weekly-report-generator` | Sunday 06:00 UTC | `weekly-report-generator` | Generate AI coaching reports for all active users. Insert into `weekly_reports`. |
| `streak-risk-notifier` | Daily 21:00 UTC | `streak-risk-notifier` | Check streak risk per user. Queue notifications in `pending_notifications`. |
| `season-rollover-handler` | Daily 00:00 UTC | `season-rollover-handler` | Detect users at day 90, roll to next season. |
| `rate-limit-cleanup` | Every 5 min | (inline SQL) | DELETE `rate_limits` rows older than 1 hour. |

All three edge function jobs are idempotent — safe to re-run without side effects. Authenticated via `cron_secret` stored in Supabase Vault.

---

## Open Decisions

| Decision | Impact | Status |
|---|---|---|
| Should photo bucket stay private or return to public? | Private = added signed URL complexity, better privacy. Public = simpler, GDPR risk. | **Resolved:** Private with signed URLs |
| Should AI simulation mode be configurable per-feature or global? | Global is simpler but limits partial feature testing without a real Claude key. | **Deferred** to Phase 2 |
| Should post-paywall photo upload happen sync or background? | Sync (current) blocks UI during Claude analysis (~10-20s). Background would allow browsing app during analysis. | **Deferred:** Keep sync for MVP |
| Should plan regeneration be a paid feature? | Monetization vs. user experience tradeoff. Regeneration costs ~$0.02 in Claude tokens per call. | **Deferred** to Phase 2 |
| Should we add social login (Apple/Google)? | Reduces signup friction. Adds complexity in Supabase Auth configuration. | **Deferred** to Phase 2 |
