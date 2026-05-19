# FORGE — Changelog

## 2026-05-19

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
