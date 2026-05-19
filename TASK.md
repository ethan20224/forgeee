# FORGE — Task Tracker

> Status key: ✅ Done · 🔄 In progress · ⬜ Todo · 🚫 Deferred · ❌ Blocked
> Architecture: See `PLANNING.md`
> Last updated: 2026-05-19

---

## Sprint Overview

| Sprint | Phases | Focus | Status |
|---|---|---|---|
| **S1** | P1–P5, F1–F4 | Backend scaffold + Auth + Quiz + Plans + Onboarding frontend | ✅ Done |
| **S2** | P6–P7, F5 | Task engine + Progress scoring + Main app shell (tabs, home) | ✅ Done |
| **S3** | P8, F6 | Coaching templates + Insights/weekly reports frontend | ⬜ Todo |
| **S4** | P9–P10, F7 | R2 storage + Photo check-ins + Cycle UI | ⬜ Todo |
| **S5** | P11, F8 | Gamification backend + Achievements/challenges frontend | ⬜ Todo |
| **S6** | P12–P13, F9 | Subscriptions + Scheduler + Settings/profile frontend | ⬜ Todo |
| **S7** | P15–P16 | React Native Web export + Production deployment | ⬜ Todo |

---

# Sprint 1 — Foundation + Onboarding ✅

## P1 — FastAPI Scaffold & Local Dev Environment

**Goal:** Runnable FastAPI server with PostgreSQL, config, and health check.

| Status | Task |
|---|---|
| ✅ | Create `backend/` directory with `pyproject.toml` (FastAPI, SQLAlchemy, Pydantic, uvicorn, alembic, python-jose, passlib, httpx, slowapi, boto3) |
| ✅ | Generate `requirements.txt` from pyproject |
| ✅ | Python 3.13 venv created at `backend/venv/` |
| ✅ | Local PostgreSQL 17.5 — database `forge` created |
| ✅ | Create `backend/src/main.py` — FastAPI app with CORS, rate limiter, health check (`GET /health`) |
| ✅ | Create `backend/src/config.py` — `Settings` class via `pydantic-settings`, loads `.env` |
| ✅ | Create `backend/.env.example` with all required env vars (see PLANNING.md §12) |
| ✅ | Create `Dockerfile` for production (multi-stage, Python 3.13-slim) |
| ✅ | Verify: `uvicorn src.main:app --port 8001` serves `/health` returning `{"status": "ok"}` |

---

## P2 — Database Models & Migrations

**Goal:** All 14 tables defined as SQLAlchemy ORM models with Alembic migrations applied.

| Status | Task |
|---|---|
| ✅ | Create `backend/src/database/connection.py` — async engine, session factory, `get_db` dependency |
| ✅ | Create `backend/src/database/models.py` — SQLAlchemy models for all 14 tables |
| ✅ | Init Alembic (`alembic init backend/src/database/migrations`) |
| ✅ | Configure `alembic.ini` and `env.py` to use `DATABASE_URL_SYNC` from settings |
| ✅ | Auto-generate initial migration from models |
| ✅ | 30 CHECK constraints (score bounds 0-100, non-negative XP/streak, season range, name length) |
| ✅ | 5 custom indexes (daily_tasks user+day, daily_tasks week+pillar, cycles user+type, season_events user+created, plan_cache hash) |
| ⬜ | Add triggers via migration: referral code auto-gen, cycle number auto-assign |
| ✅ | Verify: `alembic upgrade head` + downgrade + re-upgrade applies cleanly |

---

## P3 — Auth Module

**Goal:** Users can sign up, log in, refresh tokens, and delete their account via JWT auth.

| Status | Task |
|---|---|
| ✅ | Create `backend/src/auth/schemas.py` — `SignupRequest`, `LoginRequest`, `TokenResponse`, `RefreshRequest`, `UserResponse` |
| ✅ | Create `backend/src/auth/service.py` — `hash_password()`, `verify_password()`, `create_access_token()`, `create_refresh_token()`, `decode_token()` |
| ✅ | Create `backend/src/auth/dependencies.py` — `get_current_user()` FastAPI dependency |
| ✅ | Create `backend/src/auth/router.py` — `POST /signup`, `POST /login`, `POST /refresh`, `GET /me`, `DELETE /account` |
| ✅ | Signup: validate email uniqueness, hash password, create user + progress row, return JWT pair |
| ✅ | Login: verify credentials, return JWT pair |
| ✅ | Refresh: validate refresh token, issue new access + refresh token pair |
| ✅ | Delete account: cascade-delete all user data, return 204 |
| ✅ | Write tests: 13 tests covering all auth flows — all passing |
| ✅ | Test infra: `conftest.py` with `forge_test` DB, per-test transaction rollback, dependency override |

---

## P4 — Quiz, Score Estimator & Task Library

**Goal:** Quiz submission, deterministic score estimation, and task library available as data.

| Status | Task |
|---|---|
| ✅ | Create `backend/src/quiz/schemas.py` — `QuizSubmitRequest`, `QuizAnswerResponse`, `PillarEstimate`, `ScoreEstimateResponse` |
| ✅ | Create `backend/src/quiz/service.py` — `save_quiz_answers()`, `get_latest_quiz()` |
| ✅ | Create `backend/src/quiz/estimator.py` — deterministic score estimator with 6 heuristic factors |
| ✅ | Create `backend/src/quiz/router.py` — `POST /submit`, `GET /estimate-score` |
| ✅ | Create `backend/src/plans/task_library.py` — 144 curated tasks across 9 pillars × 3 tiers |
| ✅ | Create `backend/src/common/constants.py` — shared pillars, tiers, stages, labels |
| ✅ | Write tests: 11 estimator unit tests + 8 quiz integration tests — all 19 passing |

---

## P5 — Plan Generation (DeepSeek V4-Flash)

**Goal:** AI generates a personalised 90-day plan from quiz answers + task library via DeepSeek.

| Status | Task |
|---|---|
| ✅ | Create `backend/src/plans/prompts.py` — system prompt + `build_user_prompt()` |
| ✅ | Create `backend/src/plans/service.py` — `generate_plan()`: quiz hash → cache check → DeepSeek call → validate → persist |
| ✅ | Create `backend/src/plans/schemas.py` — `GeneratePlanResponse`, `PlanDetail`, `DailyTaskOut`, `LLMPlanOutput` |
| ✅ | Create `backend/src/plans/router.py` — `POST /generate` (rate limit: 2/hr), `GET /current`, `GET /{plan_id}` |
| ✅ | Plan cache: SHA-256 of quiz answers → `plan_cache` table → hit_count increment on reuse |
| ✅ | Plan validation: 13 weeks, ≥90 days, all task IDs must exist in library |
| ✅ | Markdown fence stripping for DeepSeek responses |
| ✅ | AI simulation mode: `AI_SIMULATION=true` returns mock plan without API call |
| ✅ | Rate limiter extracted to `src/common/rate_limit.py` |
| ✅ | Write tests: 8 integration + 7 validation unit tests — all 15 passing |

---

## F1 — Expo Scaffold + Design System + API Client

**Goal:** New Expo project with design tokens, shared UI components, API client with JWT auth, and Zustand stores.

| Status | Task |
|---|---|
| ✅ | Init Expo project in `mobile/` (blank-typescript template, SDK 54) |
| ✅ | Install deps: expo-router, reanimated, safe-area-context, screens, gesture-handler, secure-store, vector-icons, zustand |
| ✅ | Configure `app.json` (scheme: forge, dark UI, splash bg #0A0907) |
| ✅ | Configure `tsconfig.json` with `@/` → `src/` path alias |
| ✅ | Create `mobile/src/constants/design.ts` — Meridian design system tokens (Colors, Typography, Spacing, Radius, Animation, Easing) |
| ✅ | Create `mobile/src/constants/pillars.ts` — PILLAR_DISPLAY, pillarDisplayName |
| ✅ | Create `mobile/src/constants/phases.ts` — PHASE_DISPLAY, phaseForDay |
| ✅ | Create `mobile/src/components/ui/PrimaryButton.tsx` — Reanimated press-scale pill |
| ✅ | Create `mobile/src/components/ui/ForgeCard.tsx` — Raised surface card |
| ✅ | Create `mobile/src/types/api.ts` — TypeScript interfaces matching backend Pydantic schemas |
| ✅ | Create `mobile/src/store/authStorage.ts` — expo-secure-store wrappers with web fallback |
| ✅ | Create `mobile/src/store/userStore.ts` — Zustand store (user, isAuthChecked, setUser, signOut) |
| ✅ | Create `mobile/src/api/client.ts` — fetch wrapper with JWT interceptor, 401 auto-refresh |
| ✅ | Create `mobile/src/api/auth.ts` — signup, login, getMe, deleteAccount, completeOnboarding |
| ✅ | Create `mobile/src/api/quiz.ts` — submitQuiz, getEstimatedScore |
| ✅ | Create `mobile/src/api/plans.ts` — generatePlan, getCurrentPlan, getPlan |

---

## F2 — Auth Screens (Splash, Welcome, Signup/Login)

**Goal:** Port onboarding auth screens from old repo, rewired to FastAPI backend.

| Status | Task |
|---|---|
| ✅ | Create `mobile/app/_layout.tsx` — Root layout with JWT auth check (replaces Supabase) |
| ✅ | Create `mobile/app/index.tsx` — Redirect to /(auth)/splash |
| ✅ | Create `mobile/app/(auth)/_layout.tsx` — Stack with headerShown: false |
| ✅ | Create `mobile/app/(app)/_layout.tsx` — App layout stub |
| ✅ | Create `mobile/app/(app)/(tabs)/_layout.tsx` — Tabs placeholder |
| ✅ | Port `splash.tsx` — Animated progress bar, FORGE wordmark, radial glow |
| ✅ | Port `welcome.tsx` — 3 slides with Reanimated fade/slide transitions |
| ✅ | Port `signup.tsx` — Signup/login toggle form, calls api.auth.signup/login, stores JWT |

---

## F3 — Quiz Flow + Estimated Score

**Goal:** Port quiz and score estimation screens with option values aligned to backend regex patterns.

| Status | Task |
|---|---|
| ✅ | Create `mobile/src/lib/quizCache.ts` — In-memory quiz answer cache |
| ✅ | Create `mobile/app/(auth)/quiz/_layout.tsx` — Stack layout |
| ✅ | Create `mobile/app/(auth)/quiz/index.tsx` — Redirect to step 1 |
| ✅ | Port `quiz/[step].tsx` — 6-step quiz with aligned option values |
| ✅ | Create `mobile/src/lib/scoreEstimator.ts` — Client-side deterministic estimator |
| ✅ | Create `mobile/src/lib/planCache.ts` — In-memory plan + estimated score cache |
| ✅ | Port `estimated-score.tsx` — Hero score, biggest levers, protocol bullets |

---

## F4 — Plan Loading + Plan Reveal

**Goal:** Port plan generation and reveal screens, add complete-onboarding backend endpoint.

| Status | Task |
|---|---|
| ✅ | Port `plan-loading.tsx` — Spinner animation, cycling messages, POST quiz/submit + plans/generate |
| ✅ | Port `plan-reveal.tsx` — Score banner, programme name, improvements, timeline, Start Day 1 CTA |
| ✅ | Add `POST /api/v1/auth/complete-onboarding` backend endpoint |
| ✅ | Write test: `test_complete_onboarding` (idempotent) — passing |
| ✅ | All 48 backend tests passing (14 auth + 19 quiz + 15 plans) |
| ✅ | TypeScript compilation clean (zero errors) |

---

# Sprint 2 — Task Engine + Main App Shell

## P6 — Task Engine

**Goal:** Users can view today's tasks, complete them, earn XP, maintain streaks, and apply score drift.

| Status | Task |
|---|---|
| ✅ | Create `backend/src/tasks/service.py` — `get_todays_tasks()`, `complete_task()`, `get_heatmap()` |
| ✅ | Create `backend/src/tasks/schemas.py` — `TaskResponse`, `CompleteTaskResponse`, `HeatmapResponse` |
| ✅ | Create `backend/src/tasks/router.py` — `GET /today`, `POST /{task_id}/complete`, `GET /heatmap` |
| ✅ | `complete_task()`: idempotency guard, set `is_completed=True`, `completed_at=now()` |
| ✅ | XP award: +10 XP per task, +5 streak bonus when streak > 3, update level from thresholds |
| ✅ | Streak update: compare `last_active_date`, increment or reset, detect milestones (7, 14, 30, 60, 90) |
| ✅ | Score drift: +0.5 to task's pillar, cap at 100, recalculate optimisation score |
| ✅ | Pending effects queue: insert before applying, mark `applied_at` on success |
| ✅ | Write tests: 14 tests covering all task flows — all passing |

---

## P7 — Progress & Score Calculator

**Goal:** Deterministic scoring engine serving pillar scores, optimisation score, and progress data.

| Status | Task |
|---|---|
| ✅ | Create `backend/src/progress/score_calculator.py` — `calculate_optimisation_score()`, `derive_initial_weights()`, `apply_task_effect()`, `diff_pillars()` |
| ✅ | Port face shape weight adjustments from `faceShapeWeights.ts` — 8 face shapes (oval, square, round, long, oblong, heart, diamond, triangle) |
| ✅ | Port seasonal reweight logic (voice pillar unlocked in Season 2+) |
| ✅ | Create `backend/src/progress/service.py` — `get_progress()`, `get_pillar_detail()` |
| ✅ | Create `backend/src/progress/schemas.py` — `ProgressResponse`, `PillarDetailResponse` |
| ✅ | Create `backend/src/progress/router.py` — `GET /`, `GET /pillar/{pillar}` |
| ✅ | Write tests: 27 unit + 8 integration tests — all 35 passing |

---

## F5 — Main App Shell + Home Screen

**Goal:** Port tab navigation and home screen showing today's tasks, streak, and daily progress.

| Status | Task |
|---|---|
| ✅ | Create API modules: `mobile/src/api/tasks.ts` (getToday, completeTask, getHeatmap) and `mobile/src/api/progress.ts` (getProgress, getPillar) |
| ✅ | Create Zustand stores: `programStore.ts` (plan, tasks, currentDay) and `progressStore.ts` (pillarScores, streak, xp, level) |
| ✅ | Port `mobile/app/(app)/(tabs)/_layout.tsx` — 5-tab layout (Home, Progress, Program, Goals, Profile) with Meridian styling and icon set |
| ✅ | Port `mobile/app/(app)/(tabs)/index.tsx` — Home screen: greeting header, streak flame, today's task cards, completion ring |
| ✅ | Create `mobile/src/components/TaskCard.tsx` — Task card with pillar color accent, checkbox, tap-to-complete animation |
| ✅ | Create `mobile/src/components/StreakBadge.tsx` — Flame icon + streak count + milestone callout |
| ✅ | Create `mobile/src/components/CompletionRing.tsx` — Animated circular progress for daily task completion |
| ✅ | Wire Home screen: `GET /tasks/today` on mount, `POST /tasks/{id}/complete` on tap, refresh progress after completion |
| ✅ | Port `mobile/app/(app)/(tabs)/progress.tsx` — Progress tab: optimisation score hero, 9 pillar score bars |
| ✅ | Create `mobile/src/components/PillarBar.tsx` — Horizontal bar with pillar color, score label, delta indicator |
| ✅ | Wire Progress tab: `GET /progress` on mount, pull-to-refresh |
| ✅ | Handle empty state: show "Complete your first task to see progress" when no tasks completed yet |

---

# Sprint 3 — Coaching + Program View

## P8 — Coaching Engine (Deterministic Templates)

**Goal:** Daily insights, weekly reports, and season reports generated from templates — zero LLM calls.

| Status | Task |
|---|---|
| ⬜ | Create `backend/src/coaching/language_stage.py` — `stage_for_day()`: outcome (≤14), habit (15–30), mechanism (31+) |
| ⬜ | Create `backend/src/coaching/templates.py` — ~60 daily insight templates keyed by (stage, context_type, pillar) |
| ⬜ | Create `backend/src/coaching/weekly_templates.py` — ~20 weekly report paragraph templates |
| ⬜ | Create `backend/src/coaching/season_templates.py` — season report narrative templates |
| ⬜ | Create `backend/src/coaching/service.py` — `get_daily_insight()`, `get_weekly_report()`, `get_season_report()`, `generate_onboarding_compliment()` |
| ⬜ | Template selection: find biggest pillar mover, streak state, completion rate → pick template → interpolate |
| ⬜ | Rotation tracking: store last-used template index per user to avoid repetition |
| ⬜ | Create `backend/src/coaching/schemas.py` — `InsightResponse`, `WeeklyReportResponse`, `SeasonReportResponse` |
| ⬜ | Create `backend/src/coaching/router.py` — `GET /daily-insight`, `GET /weekly-report/{week}`, `GET /weekly-reports`, `GET /season-report` |
| ⬜ | Write tests: `test_stage_for_day`, `test_template_selection`, `test_variable_interpolation`, `test_rotation_no_repeat`, `test_all_stages_covered` |

---

## F6 — Coaching UI + Program Tab

**Goal:** Port daily insight card, weekly reports, program roadmap, and season overview screens.

| Status | Task |
|---|---|
| ⬜ | Create API module: `mobile/src/api/coaching.ts` (getDailyInsight, getWeeklyReport, getWeeklyReports, getSeasonReport) |
| ⬜ | Add daily insight to Home screen: fetch `GET /coaching/daily-insight`, render insight card below streak badge |
| ⬜ | Create `mobile/src/components/InsightCard.tsx` — Coaching insight with stage indicator, pillar badge, animated reveal |
| ⬜ | Port `mobile/app/(app)/(tabs)/program.tsx` — Program tab: phase banner, week-by-week roadmap, current day marker |
| ⬜ | Create `mobile/src/components/WeekRow.tsx` — Week summary row (week number, completion %, status pill) |
| ⬜ | Create `mobile/app/(app)/weekly-report/[week].tsx` — Weekly report detail screen (pillar table, coaching note, focus) |
| ⬜ | Port heatmap view: `GET /tasks/heatmap` → 90-day grid colored by completion rate |
| ⬜ | Create `mobile/src/components/HeatmapGrid.tsx` — 90-day calendar grid with pillar-colored dots |
| ⬜ | Wire Program tab: `GET /plans/current` for roadmap, `GET /coaching/weekly-reports` for list |
| ⬜ | Handle phase transitions: show phase banner (Foundation → Building → Optimisation) based on `phaseForDay()` |

---

# Sprint 4 — Photo Check-ins + Cycles

## P9 — Cloudflare R2 Storage

**Goal:** Photo upload and download via presigned URLs through Cloudflare R2.

| Status | Task |
|---|---|
| ⬜ | Create `backend/src/storage/r2_client.py` — `generate_upload_url()`, `generate_download_url()`, `delete_object()` |
| ⬜ | Upload URL: presigned PUT, 5-min expiry, path `cycles/{user_id}/{timestamp}-{angle}.jpg` |
| ⬜ | Download URL: presigned GET, 1-hour expiry |
| ⬜ | Batch download URLs for photo timeline |
| ⬜ | Write tests: `test_presigned_url_format`, `test_path_construction` (mocked S3 client) |

---

## P10 — Cycle Check-Ins & DeepSeek VL2 Photo Analysis

**Goal:** Users upload photos, get AI vision analysis of 9 pillars via DeepSeek VL2.

| Status | Task |
|---|---|
| ⬜ | Create `backend/src/cycles/prompts.py` — vision analysis system prompt |
| ⬜ | Create `backend/src/cycles/photo_analyser.py` — `analyse_photos()`: call DeepSeek VL2, parse 9-pillar JSON, validate |
| ⬜ | Create `backend/src/cycles/service.py` — `get_upload_url()`, `submit_analysis()`, `get_history()`, `get_cycle()`, `compare_cycles()` |
| ⬜ | Create `backend/src/cycles/schemas.py` — `UploadUrlResponse`, `AnalyseRequest`, `CycleAnalysisResponse`, `CycleHistoryResponse`, `CompareResponse` |
| ⬜ | Create `backend/src/cycles/router.py` — `POST /upload-url`, `POST /analyse` (rate limit: 5/hr), `GET /history`, `GET /{cycle_id}`, `GET /compare/{a}/{b}` |
| ⬜ | Check-in eligibility: enforce 3-day cadence from `plan_start_date` or last cycle |
| ⬜ | Scan mode support: "face" vs "full" pillar filtering |
| ⬜ | Update progress table with new pillar scores after analysis |
| ⬜ | AI simulation mode: return mock analysis without API call |
| ⬜ | Write tests: `test_eligibility_check`, `test_analysis_validation`, `test_scan_mode_filter`, `test_score_update`, `test_rate_limit` |

---

## F7 — Photo Check-In + Cycle History UI

**Goal:** Port photo capture flow, analysis results, cycle history, and before/after comparison.

| Status | Task |
|---|---|
| ⬜ | Install `expo-camera` and `expo-image-picker` dependencies |
| ⬜ | Create API module: `mobile/src/api/cycles.ts` (getUploadUrl, analyse, getHistory, getCycle, compareCycles) |
| ⬜ | Create `mobile/app/(app)/check-in/index.tsx` — Check-in entry: eligibility check, scan mode selector (face/full) |
| ⬜ | Create `mobile/app/(app)/check-in/capture.tsx` — Camera screen: guided overlay (face outline), capture front photo |
| ⬜ | Create `mobile/app/(app)/check-in/upload.tsx` — Upload progress: presigned URL PUT, loading spinner |
| ⬜ | Create `mobile/app/(app)/check-in/results.tsx` — Analysis results: 9-pillar score cards, before/after delta |
| ⬜ | Create `mobile/src/components/CycleCard.tsx` — Cycle summary card (date, overall score, photo thumbnail) |
| ⬜ | Create `mobile/app/(app)/cycles/index.tsx` — Cycle history list: `GET /cycles/history`, newest first |
| ⬜ | Create `mobile/app/(app)/cycles/[id].tsx` — Single cycle detail: photo, all 9 pillar scores |
| ⬜ | Create `mobile/app/(app)/cycles/compare.tsx` — Side-by-side comparison: two cycles, pillar delta bars |
| ⬜ | Add check-in CTA to Home screen: show "Check-in available" card when eligible (3-day cadence) |
| ⬜ | Wire photo upload: get presigned URL → PUT image → POST /analyse → show results |

---

# Sprint 5 — Gamification

## P11 — Gamification

**Goal:** Achievements, challenges, streak milestones, and XP levels.

| Status | Task |
|---|---|
| ⬜ | Create `backend/src/gamification/badges.py` — badge catalog |
| ⬜ | Create `backend/src/gamification/challenges.py` — challenge templates |
| ⬜ | Create `backend/src/gamification/xp.py` — XP thresholds, `calculate_level()`, level names |
| ⬜ | Create `backend/src/gamification/service.py` — `get_achievements()`, `unlock_badge()`, `get_challenges()`, `start_challenge()`, `update_challenge_progress()` |
| ⬜ | Create `backend/src/gamification/schemas.py` — `AchievementResponse`, `ChallengeResponse`, `StreakResponse` |
| ⬜ | Create `backend/src/gamification/router.py` — `GET /achievements`, `GET /challenges`, `GET /streak` |
| ⬜ | Badge unlock on events: streak milestones, challenge completion, season complete |
| ⬜ | Write tests: `test_badge_unlock_idempotent`, `test_challenge_progress`, `test_level_calculation`, `test_streak_milestones` |

---

## F8 — Gamification UI (Goals Tab + Achievements)

**Goal:** Port goals tab with active challenges, achievement showcase, and XP/level display.

| Status | Task |
|---|---|
| ⬜ | Create API module: `mobile/src/api/gamification.ts` (getAchievements, getChallenges, getStreak) |
| ⬜ | Port `mobile/app/(app)/(tabs)/goals.tsx` — Goals tab: active challenges, completed challenges, streak milestones |
| ⬜ | Create `mobile/src/components/ChallengeCard.tsx` — Challenge card with progress bar, time remaining, reward preview |
| ⬜ | Create `mobile/src/components/AchievementBadge.tsx` — Badge icon with unlock animation (locked = greyscale, unlocked = colored + glow) |
| ⬜ | Create `mobile/app/(app)/achievements.tsx` — Full achievement grid (all badges, unlocked highlighted) |
| ⬜ | Add XP bar + level indicator to Home screen header |
| ⬜ | Create `mobile/src/components/XPBar.tsx` — Animated XP progress bar with level label and level-up celebration |
| ⬜ | Wire challenges: show active challenges on Goals tab, update progress after task completion |
| ⬜ | Streak milestone celebrations: show confetti/modal on 7, 14, 30, 60, 90 day milestones |

---

# Sprint 6 — Subscriptions + Settings

## P12 — Subscription Webhooks

**Goal:** RevenueCat (mobile) and Stripe (web) webhooks sync subscription status to DB.

| Status | Task |
|---|---|
| ⬜ | Create `backend/src/subscriptions/schemas.py` — `SubscriptionStatusResponse`, webhook payload models |
| ⬜ | Create `backend/src/subscriptions/service.py` — `sync_subscription()`, `get_subscription_status()` |
| ⬜ | Create `backend/src/subscriptions/router.py` — `GET /status`, `POST /revenuecat-webhook`, `POST /stripe-webhook` |
| ⬜ | RevenueCat webhook: validate secret, handle INITIAL_PURCHASE, RENEWAL, CANCELLATION, EXPIRATION |
| ⬜ | Stripe webhook: validate signature, handle checkout.session.completed, invoice.paid, customer.subscription.deleted |
| ⬜ | Write tests: `test_revenuecat_webhook_purchase`, `test_revenuecat_webhook_cancel`, `test_stripe_webhook`, `test_invalid_webhook_secret` |

---

## P13 — Background Scheduler

**Goal:** Scheduled jobs for weekly report generation, season rollover, and streak checks.

| Status | Task |
|---|---|
| ⬜ | Create `backend/src/scheduler/jobs.py` — `generate_weekly_reports()`, `check_season_rollovers()`, `check_streaks()` |
| ⬜ | Weekly report generation (Sunday 06:00 UTC): iterate onboarded users, generate template-based report |
| ⬜ | Season rollover (daily 00:00 UTC): find users at `program_day >= 90`, increment season, reset program_day, reweight pillars |
| ⬜ | Program day advancement: advance `program_day` for active users daily |
| ⬜ | Integrate APScheduler into FastAPI startup/shutdown lifecycle |
| ⬜ | Write tests: `test_weekly_report_idempotent`, `test_season_rollover`, `test_program_day_advance` |

---

## F9 — Profile Tab + Settings + Paywall

**Goal:** Port profile/settings screen, account management, and subscription paywall.

| Status | Task |
|---|---|
| ⬜ | Create API module: `mobile/src/api/subscriptions.ts` (getStatus) |
| ⬜ | Port `mobile/app/(app)/(tabs)/profile.tsx` — Profile tab: avatar, name, email, subscription tier, program day, season |
| ⬜ | Create `mobile/app/(app)/settings.tsx` — Settings screen: notifications toggle, theme (future), privacy policy, terms |
| ⬜ | Create `mobile/app/(app)/account.tsx` — Account management: change email (future), change password (future), delete account with confirmation |
| ⬜ | Wire delete account: `DELETE /auth/account` with confirmation modal + sign-out + redirect to splash |
| ⬜ | Create `mobile/app/(app)/paywall.tsx` — Subscription paywall: tier comparison, CTA, RevenueCat purchase flow |
| ⬜ | Install and configure `react-native-purchases` (RevenueCat SDK) |
| ⬜ | Gate premium features: check subscription tier before allowing cycle check-ins beyond free limit |
| ⬜ | Add subscription badge to Profile tab header (Free / Pro / Premium) |

---

# Sprint 7 — Web + Production

## P15 — React Native Web Export

**Goal:** Web version of the app running from the same Expo codebase.

| Status | Task |
|---|---|
| ⬜ | Configure `app.config.ts` for web platform export |
| ⬜ | Replace native-only modules with web-compatible alternatives (camera → file input, secure-store → localStorage with encryption) |
| ⬜ | Gate iOS-only native modules behind `Platform.OS` checks |
| ⬜ | Stripe Checkout integration for web subscriptions (replace RevenueCat on web) |
| ⬜ | Test all screens render correctly in browser |
| ⬜ | Verify: full user journey works in Chrome/Safari/Firefox |

---

## P16 — Production Deployment

**Goal:** Live production environment on Fly.io + Neon + Cloudflare R2.

| Status | Task |
|---|---|
| ⬜ | Create Fly.io app, deploy FastAPI via `Dockerfile` |
| ⬜ | Provision Neon PostgreSQL database, run migrations |
| ⬜ | Create Cloudflare R2 bucket (`forge-photos`), configure CORS |
| ⬜ | Set all production env vars as Fly.io secrets |
| ⬜ | Configure custom domain + SSL (api.forge.app) |
| ⬜ | Set CORS origins to production domains only |
| ⬜ | EAS build for iOS + Android with production API URL |
| ⬜ | Deploy web build to Vercel/Cloudflare Pages |
| ⬜ | Smoke test: signup → quiz → plan → task → cycle → progress across all 3 platforms |
| ⬜ | Set up basic uptime monitoring |

---

## Discovered During Work

Tasks discovered during implementation that weren't in the original plan.

| Status | Task | Discovered In |
|---|---|---|
| ✅ | `POST /api/v1/auth/complete-onboarding` — marks user onboarded, sets plan_start_date | F4 |
| ✅ | CORS updated: added `http://localhost:19006` for Expo web dev server | F1 |
| ✅ | Dev CORS: allow all origins in dev mode (Expo Go doesn't send Origin headers) | F4 debugging |
| ✅ | Added `babel.config.js` with `react-native-reanimated/plugin` | F4 debugging |
| ✅ | Installed `react-native-worklets` (required by Reanimated v4) | F4 debugging |
| ✅ | Mobile `.env` uses LAN IP (`192.168.86.216`) instead of `localhost` for simulator | F4 debugging |
| ✅ | Added `.npmrc` with `legacy-peer-deps=true` to resolve React version conflicts | F4 debugging |

---

## Notes

- Architecture decisions documented in `PLANNING.md`
- Each sprint should be completed and tested before starting the next
- Backend phases within a sprint should be completed before their paired frontend phase
- LLM endpoints (P5, P10) require DeepSeek API keys — use `AI_SIMULATION=true` for dev without keys
- Frontend phases F5–F9 depend on their corresponding backend phases being complete
