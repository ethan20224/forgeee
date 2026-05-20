# FORGE — Changelog

## 2026-05-19

### Sprint 7 — Web Export + Production Deployment Config Complete

- **P15: React Native Web Export**
  - Created `app.config.ts` — typed config with web theme, permissions, plugin config
  - Installed web dependencies: react-dom, react-native-web, @expo/metro-runtime
  - Web-compatible auth storage already handled (SecureStore → localStorage fallback)
  - expo-image-picker works on web via native file input (no platform gates needed)
  - react-native-reanimated and react-native-svg work on web out of the box
  - Web export builds successfully: `npx expo export --platform web` → 2.45 MB JS bundle
  - Created `vercel.json` — SPA rewrites, security headers (X-Frame-Options, CSP, Referrer-Policy)

- **P16: Production Deployment Configuration**
  - Enhanced Dockerfile: multi-stage build, 2 uvicorn workers, built-in healthcheck, PYTHONUNBUFFERED
  - Created `fly.toml` — shared-cpu-1x, 512MB, syd region, auto-stop/start, /health check
  - Created `.env.production` — complete template with all required environment variables
  - Created `.dockerignore` — excludes venv, caches, env files, git
  - Added `GET /health/ready` endpoint — verifies database connectivity
  - Created `scripts/deploy.sh` — alembic upgrade + fly deploy + health verification
  - 185 backend tests still passing, TypeScript compilation clean

### Sprint 6 — Subscriptions + Scheduler + Settings Complete

- **P12: Subscription Webhooks**
  - Created `src/subscriptions/schemas.py` — RevenueCat and Stripe webhook payload models
  - Created `src/subscriptions/service.py` — sync_revenuecat_event(), sync_stripe_event(), get_subscription_status()
  - Created `src/subscriptions/router.py` — GET /status, POST /webhooks/revenuecat, POST /webhooks/stripe
  - RevenueCat: handles INITIAL_PURCHASE, RENEWAL, PRODUCT_CHANGE, CANCELLATION, EXPIRATION
  - Stripe: handles checkout.session.completed, invoice.paid, customer.subscription.deleted
  - Tier mapping: forge_pro_monthly/annual → pro, forge_premium_monthly/annual → premium
  - 9 tests — all passing

- **P13: Background Scheduler**
  - Created `src/scheduler/jobs.py` — advance_program_days, check_season_rollovers, generate_weekly_reports, check_streaks
  - Created `src/scheduler/setup.py` — APScheduler AsyncIOScheduler with CronTrigger integration
  - Jobs run daily at 00:05 (day advance), 00:10 (rollover), 00:15 (streaks), Sunday 06:00 (reports)
  - Integrated into FastAPI lifespan (start on boot, stop on shutdown)
  - 8 tests — all passing (185 total in suite)

- **F9: Profile Tab + Settings + Account**
  - Created `src/api/subscriptions.ts` — getSubscriptionStatus()
  - Rebuilt Profile tab: avatar initial, name, email, tier badge (Free/Pro/Premium), stats row (season/day/streak/level), XP bar, menu
  - Created Settings screen: notification toggles, version info, legal links
  - Created Account screen: user info display, danger zone with delete account + confirmation modal
  - Sign-out flow: clears tokens + redirects to login
  - Delete account flow: confirmation alert → DELETE /auth/account → sign out → login
  - TypeScript compilation clean (zero errors)

### Sprint 5 — Gamification Complete

- **P11: Gamification Backend**
  - Created `src/gamification/badges.py` — 22 badge definitions across 6 categories (streak, tasks, level, cycles, score, season)
  - Created `src/gamification/challenges.py` — 10 time-limited challenge templates with XP rewards
  - Created `src/gamification/xp.py` — 25-level progression system with named levels (Beginner → FORGE)
  - Created `src/gamification/service.py` — badge unlock (idempotent), challenge lifecycle, streak info, XP progression
  - Created `src/gamification/router.py` — GET /achievements, GET /challenges, POST /challenges/start, GET /streak, GET /xp
  - 25 tests (13 unit + 12 integration) — all passing (168 total in suite)

- **F8: Gamification UI (Goals Tab)**
  - Created `src/api/gamification.ts` — full API client (achievements, challenges, streak, XP, start challenge)
  - Created `XPBar` component — animated progress bar with level name and total XP
  - Created `ChallengeCard` component — progress bar, reward badge, start button for available challenges
  - Created `AchievementBadge` component — locked/unlocked states with ember glow
  - Rebuilt Goals tab — XP bar, cycle CTA, active/available challenges, badge grid, cycle history
  - Added gamification TypeScript interfaces to `types/api.ts`
  - TypeScript compilation clean (zero errors)

### Sprint 4 — Photo Check-ins + Cycles Complete

- **P9: Cloudflare R2 Storage**
  - Created `src/storage/r2_client.py` — S3-compatible presigned URL generation for Cloudflare R2
  - `generate_upload_url()` — presigned PUT (5-min expiry), path: `cycles/{user_id}/{timestamp}-{angle}.jpg`
  - `generate_download_url()` — presigned GET (1-hour expiry)
  - `generate_download_urls()` — batch download URLs for photo timeline
  - `delete_object()` — remove photo from R2
  - 8 unit tests (mocked boto3 client) — all passing

- **P10: Cycle Check-Ins & DeepSeek VL2 Photo Analysis**
  - Created `src/cycles/prompts.py` — face-scan and full-scan system prompts for VL2
  - Created `src/cycles/photo_analyser.py` — `analyse_photos()` with DeepSeek VL2 + simulation mode
  - Created `src/cycles/service.py` — eligibility (7-day cooldown), submit analysis, history, compare
  - Created `src/cycles/schemas.py` — UploadUrlResponse, CycleAnalysisResponse, CycleCompareResponse, etc.
  - Created `src/cycles/router.py` — POST /upload-url, GET /eligibility, POST /analyse, GET /history, GET /{id}, GET /compare
  - Score validation: clamp [0,100], face-shape whitelist, scan mode filtering
  - Progress table auto-updated with new pillar scores after analysis
  - 16 integration/unit tests — all passing (143 total in suite)

- **F7: Photo Check-In + Cycle History UI**
  - Installed `expo-image-picker`
  - Created `src/api/cycles.ts` — full API client (upload URL, analyse, history, detail, compare)
  - Created `src/store/cycleStore.ts` — Zustand store (eligibility, submitCheckin, history)
  - Created `cycle-checkin.tsx` — camera/gallery capture, face/full scan mode toggle, upload + analyse flow
  - Created `cycle-result.tsx` — score hero, pillar grid, AI insight card, next focus card
  - Rebuilt Goals tab — eligibility CTA, cycle history list, navigation to results
  - Added TypeScript interfaces for all cycle types to `types/api.ts`
  - TypeScript compilation clean (zero errors)

### Frontend — F6 Coaching UI + Program Tab Complete

- **F6: Coaching UI + Program Tab**
  - Created `src/api/coaching.ts` (getDailyInsight, getWeeklyReport, getWeeklyReports, getSeasonReport)
  - Created `InsightCard` component with stage badge (Results/Habit/Science) and pillar indicator
  - Added daily insight card to Home screen (fetched on mount)
  - Rebuilt Program tab: phase banner (The Basics → Building Up → Results), 13-week roadmap with WeekRow, HeatmapGrid
  - Created `WeekRow` component with completion %, status pill (Strong/Building/Starting/Upcoming), current week highlight
  - Created `HeatmapGrid` — 90-day grid with completion-rate heat coloring and current day marker
  - Created weekly report detail screen (`/weekly-report/[week]`) with pillar bars, coaching note, focus paragraph
  - Added coaching TypeScript interfaces to `types/api.ts`
  - TypeScript compilation clean (zero errors)

### Backend — P8 Coaching Engine Complete

- **P8: Coaching Engine (Deterministic Templates)**
  - Created `language_stage.py` — 3 language stages: outcome (≤14d), habit (15-30d), mechanism (31+d)
  - Created `templates.py` — ~60 daily insight templates across 3 stages × 4 contexts × 9 pillars
  - Created `weekly_templates.py` — coaching paragraphs + focus paragraphs for weekly reports
  - Created `season_templates.py` — narrative templates for end-of-season reports
  - Created `service.py` — template selection with context detection (streak milestones, pillar movers, completion rate)
  - Created `router.py` — `GET /daily-insight`, `GET /weekly-report/{week}`, `GET /weekly-reports`, `GET /season-report`
  - Zero LLM calls — all coaching content generated deterministically
  - 22 tests (13 unit + 9 integration) — all passing (119 total in suite)

### Frontend — F5 Main App Shell + Home Screen Complete

- **F5: Main App Shell + Home Screen**
  - Created `src/api/tasks.ts` (getTodaysTasks, completeTask, getHeatmap) and `src/api/progress.ts` (getProgress, getPillarDetail)
  - Created Zustand stores: `programStore.ts` (plan, tasks, completion) and `progressStore.ts` (scores, streak, XP, level)
  - Ported 5-tab layout (Home, Progress, Program, Goals, Profile) with Meridian dark theme + Ionicons
  - Built Home screen: time-based greeting, streak badge, completion ring (SVG), today's task list
  - Created `TaskCard` component with Reanimated press-scale animation, checkbox, pillar label, XP badge
  - Created `StreakBadge` with flame icon, hot state (7+ days), milestone callout
  - Created `CompletionRing` — SVG circular progress with fraction label
  - Created `PillarBar` — horizontal bar with score, delta indicator, color
  - Built Progress tab: FORGE Score hero card, delta vs baseline, XP/level display, 9 pillar bars
  - Pull-to-refresh on both Home and Progress tabs
  - Empty states handled for no tasks and no progress
  - Installed `react-native-svg` for ring component
  - TypeScript compilation clean (zero errors)

### Backend — P7 Progress & Score Calculator Complete

- **P7: Progress & Score Calculator**
  - Created `src/progress/score_calculator.py` — deterministic scoring engine
  - Ported face shape weights for 8 shapes (oval, square, round, long, oblong, heart, diamond, triangle)
  - Ported seasonal reweight: voice excluded in Season 1, included from Season 2+
  - Quiz concern boosts: +0.05 to relevant pillar(s), normalised to sum 1.0
  - `calculate_optimisation_score()` — weighted average with null-pillar exclusion
  - `derive_initial_weights()` — face shape + concern + season → personalised weights
  - `diff_pillars()` — per-pillar delta computation clamped to [-100, 100]
  - Created `src/progress/service.py` — `get_progress()`, `get_pillar_detail()` with history
  - Created `src/progress/router.py` — `GET /`, `GET /pillar/{pillar}`
  - 35 tests (27 unit + 8 integration) — all passing (97 total in suite)

### Backend — P6 Task Engine Complete

- **P6: Task Engine**
  - Created `src/tasks/service.py` with `get_todays_tasks()`, `complete_task()`, `get_heatmap()`
  - Created `src/tasks/schemas.py` — TaskResponse, CompleteTaskResponse, HeatmapResponse
  - Created `src/tasks/router.py` — `GET /today`, `POST /{task_id}/complete`, `GET /heatmap`
  - Task completion: idempotency guard prevents double XP award
  - XP system: +10 XP per task, +5 streak bonus when streak > 3, level calculation from 20 thresholds
  - Streak logic: increment on consecutive days, reset after gap, detect milestones (7, 14, 30, 60, 90)
  - Score drift: +0.5 to task's pillar score, capped at 100, recalculates optimisation score
  - Pending effects queue: inserts PendingTaskEffect before applying drift for resilience
  - 14 integration tests — all passing (62 total tests in suite)

## 2026-05-19

### Frontend — F1-F4 Complete

- **F1: Expo Scaffold + Design System + API Client**
  - Initialized Expo project (`mobile/`) with SDK 54, TypeScript, expo-router
  - Ported Meridian design system tokens (Colors, Typography, Spacing, Radius, Animation, Easing)
  - Created shared UI components: PrimaryButton, ForgeCard (fallback-only, no SwiftUI dependency)
  - Built API client with JWT interceptor, 401 auto-refresh, ApiRequestError class
  - Created auth/quiz/plans API modules targeting FastAPI backend
  - Created Zustand userStore + expo-secure-store token storage (with web localStorage fallback)
  - Created TypeScript interfaces matching backend Pydantic schemas

- **F2: Auth Screens**
  - Ported splash screen (animated progress bar, FORGE wordmark, radial glow)
  - Ported welcome slides (3 slides with Reanimated fade/slide transitions)
  - Ported signup/login screen rewired to FastAPI auth endpoints
  - Root layout with JWT-based auth check (replaces Supabase auth listener)

- **F3: Quiz Flow + Estimated Score**
  - Ported 6-step quiz with option values aligned to backend regex patterns
  - Options updated: daily_time (10/20/30/45/60min), timeline (30/60/90days), age_range (16-19 through 40+), main_concern (+overall)
  - Created client-side deterministic score estimator (mirrors backend heuristics)
  - Ported estimated-score screen (hero score, biggest levers, protocol bullets)

- **F4: Plan Loading + Plan Reveal**
  - Ported plan-loading screen (spinner, cycling messages, POST quiz/submit then POST plans/generate)
  - Ported plan-reveal screen (score banner, programme name, improvements, limitations, timeline, roadmap)
  - Added `POST /api/v1/auth/complete-onboarding` backend endpoint (sets onboarded=true, plan_start_date=today)
  - All 48 backend tests passing, TypeScript compilation clean

### Backend — Discovered During Work

- Added `POST /api/v1/auth/complete-onboarding` endpoint to `backend/src/auth/router.py`
- Updated CORS origins to include `http://localhost:19006` for Expo web dev server
